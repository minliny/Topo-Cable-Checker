// pages/RuleEditorPage.tsx
// P0 CONSTRAINT: RuleEditor is parameter editor - condition DSL is read-only
// P0 CONSTRAINT: Parameter editing goes to rule_overrides ONLY - must NOT mutate ParameterProfile
// P0 CONSTRAINT: No version publishing, no rollback, no execution triggers
// P0 CONSTRAINT: No UI diff recomputation

import React, { useState, useEffect } from 'react';
import { Baseline, RuleSet } from '../models/baseline';
import { ParameterDefinition, ParameterType, ParameterProfile, ThresholdProfile } from '../models/profile';
import { ScopeSelector } from '../models/scope';
import { getBaselineProfileMapEntry, getParameterProfileList, getThresholdProfileList, getScopeSelectorList, getRuleSetList } from '../api';

export interface RuleEditorPageProps {
  baseline: Baseline;
}

interface RuleEntry {
  id: string;
  name: string;
  enabled: boolean;
  condition: string;
  threshold: string;
  category: string;
  severity: 'critical' | 'warning' | 'info';
  parameters: Record<string, string | number | boolean>;
}

const RULES_MAP: Record<string, RuleEntry[]> = {
  'bl-001': [
    { id: 'R-001', name: 'Core Uplink Redundancy', severity: 'critical', category: 'redundancy', enabled: true, condition: 'device.role=="core" AND count(active_uplinks)>=param.min_uplinks', threshold: '2', parameters: { min_uplinks: 2 } },
    { id: 'R-002', name: 'BGP Session Health', severity: 'critical', category: 'routing', enabled: true, condition: 'bgp.session.state=="Established" AND bgp.hold_timer<=param.bgp_hold_timer', threshold: '180s', parameters: { bgp_hold_timer: 180 } },
    { id: 'R-003', name: 'OSPF Adjacency', severity: 'warning', category: 'routing', enabled: true, condition: 'ospf.neighbor.count>=param.min_ospf_neighbors', threshold: '1', parameters: { min_ospf_neighbors: 1 } },
    { id: 'R-004', name: 'STP Root Bridge', severity: 'warning', category: 'layer2', enabled: true, condition: 'stp.root_bridge==device.id', threshold: '-', parameters: {} },
    { id: 'R-005', name: 'Port Utilization Cap', severity: 'warning', category: 'capacity', enabled: true, condition: 'interface.utilization_30d<=param.max_util_threshold', threshold: '85%', parameters: { max_util_threshold: 0.85 } },
    { id: 'R-006', name: 'NTP Clock Drift', severity: 'info', category: 'management', enabled: true, condition: 'ntp.clock_drift<=param.ntp_drift_ms', threshold: '100ms', parameters: { ntp_drift_ms: 100 } },
    { id: 'R-007', name: 'Management Reachability', severity: 'info', category: 'management', enabled: true, condition: 'ping(mgmt_ip).rtt<=param.mgmt_ping_timeout', threshold: '5s', parameters: { mgmt_ping_timeout: 5000 } },
    { id: 'R-008', name: 'Syslog Server', severity: 'info', category: 'management', enabled: false, condition: 'syslog.server.reachable==true', threshold: '-', parameters: {} },
    { id: 'R-009', name: 'Aggregation Redundancy', severity: 'critical', category: 'redundancy', enabled: true, condition: 'device.role=="aggregation" AND count(downlinks)>=param.min_uplinks', threshold: '2', parameters: { min_uplinks: 2 } },
    { id: 'R-010', name: 'VLAN Consistency', severity: 'warning', category: 'layer2', enabled: true, condition: 'vlan consistency check across switches', threshold: '-', parameters: {} },
  ],
  'bl-002': [
    { id: 'R-001', name: 'Core Uplink Redundancy', severity: 'critical', category: 'redundancy', enabled: true, condition: 'device.role=="core" AND count(active_uplinks)>=param.min_uplinks', threshold: '1', parameters: { min_uplinks: 1 } },
    { id: 'R-002', name: 'BGP Session Health', severity: 'critical', category: 'routing', enabled: true, condition: 'bgp.session.state=="Established" AND bgp.hold_timer<=param.bgp_hold_timer', threshold: '90s', parameters: { bgp_hold_timer: 90 } },
    { id: 'R-003', name: 'OSPF Adjacency', severity: 'warning', category: 'routing', enabled: true, condition: 'ospf.neighbor.count>=param.min_ospf_neighbors', threshold: '0', parameters: { min_ospf_neighbors: 0 } },
    { id: 'R-004', name: 'STP Root Bridge', severity: 'warning', category: 'layer2', enabled: true, condition: 'stp.root_bridge==device.id', threshold: '-', parameters: {} },
    { id: 'R-005', name: 'Port Utilization Cap', severity: 'warning', category: 'capacity', enabled: false, condition: 'interface.utilization_30d<=param.max_util_threshold', threshold: '90%', parameters: { max_util_threshold: 0.90 } },
    { id: 'R-006', name: 'NTP Clock Drift', severity: 'info', category: 'management', enabled: true, condition: 'ntp.clock_drift<=param.ntp_drift_ms', threshold: '200ms', parameters: { ntp_drift_ms: 200 } },
  ],
};

type OverridesState = Record<string, Record<string, number | string | boolean>>;

function SeverityTag({ sev }: { sev: 'critical' | 'warning' | 'info' }) {
  const labels = { critical: 'Critical', warning: 'Warning', info: 'Info' };
  return <span className={`sev-tag sev-${sev}`}>{labels[sev]}</span>;
}

function TypedInput({
  ruleId,
  param,
  value,
  onChange,
}: {
  ruleId: string;
  param: ParameterDefinition;
  value: number | string | boolean;
  onChange: (ruleId: string, key: string, val: number | string | boolean) => void;
}) {
  const handleChange = (raw: string, type: ParameterType) => {
    let parsed: number | string | boolean = raw;
    if (type === 'number') parsed = Number(raw);
    if (type === 'boolean') parsed = raw === 'true';
    onChange(ruleId, param.key, parsed);
  };

  const baseStyle: React.CSSProperties = {
    background: 'var(--bg2)',
    border: '1px solid var(--border-hi)',
    borderRadius: 3,
    padding: '2px 5px',
    color: 'var(--text0)',
    fontFamily: 'var(--mono)',
    fontSize: 11,
    outline: 'none',
    width: 80,
  };

  if (param.type === 'boolean') {
    return (
      <select style={baseStyle} value={String(value)} onChange={e => handleChange(e.target.value, 'boolean')}>
        <option value="true">true</option>
        <option value="false">false</option>
      </select>
    );
  }

  if (param.type === 'enum' && param.options) {
    return (
      <select style={baseStyle} value={String(value)} onChange={e => handleChange(e.target.value, 'enum')}>
        {param.options.map(o => <option key={o} value={o}>{o}</option>)}
      </select>
    );
  }

  if (param.type === 'number') {
    const numVal = typeof value === 'number' ? value : Number(value);
    return <input type="number" style={baseStyle} value={numVal} onChange={e => handleChange(e.target.value, 'number')} />;
  }

  return <input type="text" style={baseStyle} value={String(value)} onChange={e => handleChange(e.target.value, 'string')} />;
}

export const RuleEditorPage: React.FC<RuleEditorPageProps> = ({ baseline }) => {
  const [profileBinding, setProfileBinding] = useState<{ parameter_profile_id: string; threshold_profile_id: string; scope_selector_id: string; ruleset_ids: string[] } | null>(null);
  const [parameterProfiles, setParameterProfiles] = useState<ParameterProfile[]>([]);
  const [thresholdProfiles, setThresholdProfiles] = useState<ThresholdProfile[]>([]);
  const [scopeSelectors, setScopeSelectors] = useState<ScopeSelector[]>([]);
  const [rulesets, setRulesets] = useState<RuleSet[]>([]);

  useEffect(() => {
    getBaselineProfileMapEntry(baseline.id).then(setProfileBinding);
    getParameterProfileList().then(setParameterProfiles);
    getThresholdProfileList().then(setThresholdProfiles);
    getScopeSelectorList().then(setScopeSelectors);
    getRuleSetList().then(setRulesets);
  }, [baseline.id]);

  const boundRulesets = profileBinding?.ruleset_ids
    ? (profileBinding.ruleset_ids.map((id: string) => rulesets.find(rs => rs.ruleset_id === id)).filter(Boolean) as RuleSet[])
    : [];
  const allRules = RULES_MAP[baseline.id] ?? [];

  const [enabled, setEnabled] = useState<Record<string, boolean>>(() => {
    const m: Record<string, boolean> = {};
    allRules.forEach(r => { m[r.id] = r.enabled; });
    return m;
  });

  const [overrides, setOverrides] = useState<OverridesState>({});
  const [expandedRule, setExpandedRule] = useState<string | null>(null);

  const setOverride = (rId: string, key: string, val: number | string | boolean) => {
    setOverrides(prev => ({ ...prev, [rId]: { ...(prev[rId] ?? {}), [key]: val } }));
  };

  const resetOverrides = () => setOverrides({});

  const effectiveParamValue = (rule: RuleEntry, paramKey: string): number | string | boolean => {
    if (overrides[rule.id]?.[paramKey] !== undefined) {
      return overrides[rule.id][paramKey];
    }
    return rule.parameters[paramKey] ?? '';
  };

  return (
    <div className="page rule-editor-page">
      <div className="page-header">
        <div>
          <div className="page-title">Rule Editor - {baseline.name}</div>
          <div className="page-sub">Grouped by RuleSet | Condition Read-Only | Parameters via rule_overrides</div>
        </div>
        <div className="page-actions">
          <button className="btn btn-secondary btn-sm" onClick={resetOverrides} style={{ marginRight: 4 }}>Reset Overrides</button>
          <button className="btn btn-primary">Save Changes</button>
        </div>
      </div>

      {rulesets.length === 0 && (
        <div className="empty-state">
          <div className="empty-icon">O</div>
          <div className="empty-title">No RuleSet bound to this baseline</div>
        </div>
      )}

      {boundRulesets.map(rs => {
        const rsRuleIds = rs.rule_ids ?? [];
        const rsRules = rsRuleIds.map(id => allRules.find(r => r.id === id)).filter(Boolean) as RuleEntry[];
        const rp = {
          parameter_profile_id: profileBinding?.parameter_profile_id ?? '',
          threshold_profile_id: profileBinding?.threshold_profile_id ?? '',
          scope_selector_id: profileBinding?.scope_selector_id ?? '',
        };
        const pp = rp.parameter_profile_id ? parameterProfiles.find(p => p.profile_id === rp.parameter_profile_id) : null;
        const tp = rp.threshold_profile_id ? thresholdProfiles.find(p => p.profile_id === rp.threshold_profile_id) : null;
        const sc = rp.scope_selector_id ? scopeSelectors.find(s => s.scope_id === rp.scope_selector_id) : null;

        return (
          <div key={rs.ruleset_id} className="ruleset-group" style={{ marginBottom: 16 }}>
            <div className="ruleset-header-bar">
              <code className="ruleset-id">{rs.ruleset_id}</code>
              <span className="ruleset-name">{rs.name}</span>
              <span className="ruleset-desc">{rs.description}</span>
              <span className="ruleset-priority">priority {rs.priority}</span>
            </div>
            <div className="ruleset-body">
              {rsRules.map(rule => {
                const hasOverride = overrides[rule.id] && Object.keys(overrides[rule.id]).length > 0;
                const isExpanded = expandedRule === rule.id;
                return (
                  <div key={rule.id} className={`rule-item ${enabled[rule.id] ? '' : 'disabled'}`}>
                    <div className="rule-row" onClick={() => setExpandedRule(isExpanded ? null : rule.id)}>
                      <label className="toggle-label">
                        <input
                          type="checkbox"
                          checked={!!enabled[rule.id]}
                          onChange={e => { e.stopPropagation(); setEnabled(prev => ({ ...prev, [rule.id]: e.target.checked })); }}
                        />
                      </label>
                      <div className="rule-name">{rule.name}</div>
                      <SeverityTag sev={rule.severity} />
                      <code className="rule-condition">{rule.condition}</code>
                      {hasOverride && <span className="override-badge">Overridden</span>}
                      <span className="expand-icon">{isExpanded ? '^' : 'v'}</span>
                    </div>
                    {isExpanded && (
                      <div className="rule-detail">
                        <div className="rule-detail-grid">
                          <div className="detail-card">
                            <h4>Basic Info</h4>
                            <dl className="kv-grid">
                              <dt>rule_id</dt><dd><code>{rule.id}</code></dd>
                              <dt>name</dt><dd>{rule.name}</dd>
                              <dt>category</dt><dd>{rule.category}</dd>
                              <dt>severity</dt><dd><SeverityTag sev={rule.severity} /></dd>
                              <dt>condition</dt><dd><code className="condition-readonly">{rule.condition}</code></dd>
                              <dt>threshold</dt><dd>{rule.threshold}</dd>
                            </dl>
                          </div>
                          {pp && (
                            <div className="detail-card">
                              <h4>ParameterProfile</h4>
                              <dl className="kv-grid">
                                <dt>profile_id</dt><dd><code>{pp.profile_id}</code></dd>
                                <dt>name</dt><dd>{pp.name}</dd>
                              </dl>
                              <table className="param-table">
                                <thead><tr><th>Key</th><th>Default</th><th>Current</th><th>Action</th></tr></thead>
                                <tbody>
                                  {pp.parameters.map(param => {
                                    const currentVal = effectiveParamValue(rule, param.key);
                                    const isOverridden = overrides[rule.id]?.[param.key] !== undefined;
                                    return (
                                      <tr key={param.key}>
                                        <td><code>{param.key}</code></td>
                                        <td className="default-val">{String(param.value)}{param.unit ?? ''}</td>
                                        <td className="current-val">
                                          <TypedInput ruleId={rule.id} param={param} value={currentVal} onChange={setOverride} />
                                        </td>
                                        <td>
                                          {isOverridden && (
                                            <button className="reset-param-btn" onClick={() => {
                                              setOverrides(prev => {
                                                const next = { ...prev };
                                                if (next[rule.id]) {
                                                  const { [param.key]: _, ...rest } = next[rule.id];
                                                  next[rule.id] = rest;
                                                  if (Object.keys(next[rule.id]).length === 0) delete next[rule.id];
                                                }
                                                return next;
                                              });
                                            }}>Reset</button>
                                          )}
                                        </td>
                                      </tr>
                                    );
                                  })}
                                </tbody>
                              </table>
                            </div>
                          )}
                          {tp && (
                            <div className="detail-card">
                              <h4>ThresholdProfile</h4>
                              <dl className="kv-grid">
                                <dt>profile_id</dt><dd><code>{tp.profile_id}</code></dd>
                                <dt>name</dt><dd>{tp.name}</dd>
                              </dl>
                              <table className="threshold-table">
                                <thead><tr><th>Key</th><th>Operator</th><th>Value</th><th>Severity</th></tr></thead>
                                <tbody>
                                  {tp.thresholds.map(t => (
                                    <tr key={t.key}>
                                      <td><code>{t.key}</code></td>
                                      <td className="op-cell">{t.operator}</td>
                                      <td>{String(t.value)}</td>
                                      <td><SeverityTag sev={t.severity} /></td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          )}
                          {sc && (
                            <div className="detail-card">
                              <h4>ScopeSelector</h4>
                              <dl className="kv-grid">
                                <dt>scope_id</dt><dd><code>{sc.scope_id}</code></dd>
                                <dt>name</dt><dd>{sc.name}</dd>
                                <dt>method</dt><dd>{sc.method}</dd>
                                <dt>included</dt><dd>{sc.included_groups.join(', ')}</dd>
                                <dt>excluded</dt><dd>{sc.excluded_groups.join(', ') || '-'}</dd>
                              </dl>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default RuleEditorPage;