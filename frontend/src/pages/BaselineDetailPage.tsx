// pages/BaselineDetailPage.tsx
// P0 CONSTRAINT: BaselineDetail is read-only — no editing, no publishing, no execution
// P0 CONSTRAINT: No UI diff recomputation
// P0 CONSTRAINT: No router library, no state management library

import React, { useState, useEffect } from 'react';
import { Baseline, RuleSet } from '../models/baseline';
import { ParameterProfile, ThresholdProfile } from '../models/profile';
import { ScopeSelector } from '../models/scope';
import { RuleDefinition } from '../models/baseline';
import { getBaselineProfileMapEntry, getBaselineVersionSnapshot, getParameterProfileList, getThresholdProfileList, getScopeSelectorList, getRuleSetList } from '../api';

export interface BaselineDetailPageProps {
  baseline: Baseline;
  onNavigateToVersions?: () => void;
  onNavigateToRules?: () => void;
}

interface RuleSummary {
  id: string;
  name: string;
  severity: 'critical' | 'warning' | 'info';
  category: string;
  enabled: boolean;
}

const MOCK_RULES: Record<string, RuleSummary[]> = {
  'bl-001': [
    { id: 'R-001', name: '核心上行冗余', severity: 'critical', category: '冗余', enabled: true },
    { id: 'R-002', name: 'BGP 会话健康', severity: 'critical', category: '路由', enabled: true },
    { id: 'R-003', name: 'OSPF 邻接健康', severity: 'warning', category: '路由', enabled: true },
    { id: 'R-004', name: 'STP 根桥稳定', severity: 'warning', category: '二层', enabled: true },
    { id: 'R-005', name: '端口利用率上限', severity: 'warning', category: '容量', enabled: true },
    { id: 'R-006', name: 'NTP 时钟偏差', severity: 'info', category: '管理', enabled: true },
    { id: 'R-007', name: '管理网段可达', severity: 'info', category: '管理', enabled: true },
    { id: 'R-008', name: '日志服务器可达', severity: 'info', category: '管理', enabled: false },
    { id: 'R-009', name: '汇聚层冗余', severity: 'critical', category: '冗余', enabled: true },
    { id: 'R-010', name: 'VLAN 一致性', severity: 'warning', category: '二层', enabled: true },
  ],
  'bl-002': [
    { id: 'R-001', name: '核心上行冗余', severity: 'critical', category: '冗余', enabled: true },
    { id: 'R-002', name: 'BGP 会话健康', severity: 'critical', category: '路由', enabled: true },
    { id: 'R-003', name: 'OSPF 邻接健康', severity: 'warning', category: '路由', enabled: true },
    { id: 'R-004', name: 'STP 根桥稳定', severity: 'warning', category: '二层', enabled: true },
    { id: 'R-005', name: '端口利用率上限', severity: 'warning', category: '容量', enabled: false },
    { id: 'R-006', name: 'NTP 时钟偏差', severity: 'info', category: '管理', enabled: true },
  ],
};

const SEVERITY_ORDER = ['critical', 'warning', 'info'] as const;

function StatusTag({ status }: { status: string }) {
  const cls = status === 'published' ? 'status-published' : status === 'draft' ? 'status-draft' : 'status-deprecated';
  const labels: Record<string, string> = { published: '已发布', draft: '草稿', deprecated: '已废弃' };
  return <span className={`status-tag ${cls}`}>{labels[status] ?? status}</span>;
}

function SeverityTag({ sev }: { sev: 'critical' | 'warning' | 'info' }) {
  const labels = { critical: '严重', warning: '警告', info: '提示' };
  return <span className={`sev-tag sev-${sev}`}>{labels[sev]}</span>;
}

export const BaselineDetailPage: React.FC<BaselineDetailPageProps> = ({
  baseline,
  onNavigateToVersions,
  onNavigateToRules,
}) => {
  const [expandedRuleset, setExpandedRuleset] = useState<string | null>(null);
  const [profileBinding, setProfileBinding] = useState<{ parameter_profile_id: string; threshold_profile_id: string; scope_selector_id: string; ruleset_ids: string[] } | null>(null);
  const [versionSnapshot, setVersionSnapshot] = useState<{ baseline_id: string; current_version: string; previous_version: string | null; rule_added_count: number; rule_removed_count: number; parameter_changed_count: number; threshold_changed_count: number } | null>(null);
  const [parameterProfiles, setParameterProfiles] = useState<ParameterProfile[]>([]);
  const [thresholdProfiles, setThresholdProfiles] = useState<ThresholdProfile[]>([]);
  const [scopeSelectors, setScopeSelectors] = useState<ScopeSelector[]>([]);
  const [rulesets, setRulesets] = useState<RuleSet[]>([]);

  useEffect(() => {
    getBaselineProfileMapEntry(baseline.id).then(setProfileBinding);
    getBaselineVersionSnapshot(baseline.id).then(setVersionSnapshot);
    getParameterProfileList().then(setParameterProfiles);
    getThresholdProfileList().then(setThresholdProfiles);
    getScopeSelectorList().then(setScopeSelectors);
    getRuleSetList().then(setRulesets);
  }, [baseline.id]);

  const parameterProfile = profileBinding?.parameter_profile_id
    ? parameterProfiles.find(p => p.profile_id === profileBinding.parameter_profile_id)
    : null;
  const thresholdProfile = profileBinding?.threshold_profile_id
    ? thresholdProfiles.find(p => p.profile_id === profileBinding.threshold_profile_id)
    : null;
  const scopeSelector = profileBinding?.scope_selector_id
    ? scopeSelectors.find(s => s.scope_id === profileBinding.scope_selector_id)
    : null;
  const boundRulesets = profileBinding?.ruleset_ids
    ? (profileBinding.ruleset_ids.map((id: string) => rulesets.find(rs => rs.ruleset_id === id)).filter(Boolean) as RuleSet[])
    : [];
  const mockRules = MOCK_RULES[baseline.id] ?? [];

  return (
    <div className="page baseline-detail-page">
      <div className="page-header">
        <div className="header-left">
          <div className="header-title-row">
            <StatusTag status={baseline.status} />
            <code className="version-badge">v{baseline.version}</code>
          </div>
          <div className="page-title">{baseline.name}</div>
          <div className="page-sub">{baseline.description}</div>
        </div>
      </div>

      <div className="detail-grid">
        {/* Basic info */}
        <div className="card">
          <h3>基本信息</h3>
          <dl className="kv-grid">
            <dt>baseline_id</dt><dd><code>{baseline.id}</code></dd>
            <dt>version</dt><dd>{baseline.version}</dd>
            <dt>status</dt><dd><StatusTag status={baseline.status} /></dd>
            <dt>enabled_rules</dt><dd>{baseline.enabled_count} / {baseline.rule_count}</dd>
            <dt>created_at</dt><dd>{baseline.created_at}</dd>
            <dt>published_at</dt><dd>{baseline.published_at ?? '未发布'}</dd>
          </dl>
        </div>

        {/* Identification strategy */}
        <div className="card">
          <h3>识别策略</h3>
          <dl className="kv-grid">
            <dt>method</dt><dd>{baseline.identification_strategy.method}</dd>
            <dt>id_fields</dt><dd>{(baseline.identification_strategy.id_fields).join(', ')}</dd>
            <dt>naming_template</dt><dd><code>{baseline.naming_template}</code></dd>
          </dl>
        </div>

        {/* ParameterProfile */}
        {parameterProfile && (
          <div className="card">
            <div className="card-header">
              <h3>ParameterProfile</h3>
              <code className="profile-id">{parameterProfile.profile_id}</code>
            </div>
            <div className="profile-desc">{parameterProfile.description}</div>
            <table className="param-table">
              <thead><tr><th>参数</th><th>值</th><th>说明</th></tr></thead>
              <tbody>
                {parameterProfile.parameters.map(p => (
                  <tr key={p.key}>
                    <td><code>{p.key}</code></td>
                    <td className="param-val">{p.value}{p.unit ?? ''}</td>
                    <td className="param-desc">{p.description}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* ThresholdProfile */}
        {thresholdProfile && (
          <div className="card">
            <div className="card-header">
              <h3>ThresholdProfile</h3>
              <code className="profile-id">{thresholdProfile.profile_id}</code>
            </div>
            <div className="profile-desc">{thresholdProfile.description}</div>
            <table className="threshold-table">
              <thead><tr><th>阈值</th><th>操作符</th><th>值</th><th>级别</th></tr></thead>
              <tbody>
                {thresholdProfile.thresholds.map(t => (
                  <tr key={t.key}>
                    <td><code>{t.key}</code></td>
                    <td className="op-cell">{t.operator}</td>
                    <td className="thresh-val">{t.value}</td>
                    <td><SeverityTag sev={t.severity} /></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* ScopeSelector */}
        {scopeSelector && (
          <div className="card">
            <div className="card-header">
              <h3>ScopeSelector</h3>
              <code className="profile-id">{scopeSelector.scope_id}</code>
            </div>
            <div className="profile-desc">{scopeSelector.description}</div>
            <dl className="kv-grid">
              <dt>method</dt><dd>{scopeSelector.method}</dd>
              <dt>scope_fields</dt><dd>{scopeSelector.scope_fields.join(', ')}</dd>
              <dt>included</dt><dd>{scopeSelector.included_groups.join(', ')}</dd>
              <dt>excluded</dt><dd>{scopeSelector.excluded_groups.join(', ') || '—'}</dd>
            </dl>
          </div>
        )}

        {/* Version snapshot summary */}
        {versionSnapshot && (
          <div className="card version-snapshot-card">
            <h3>版本快照</h3>
            <dl className="kv-grid">
              <dt>current_version</dt><dd>{versionSnapshot.current_version}</dd>
              <dt>previous_version</dt><dd>{versionSnapshot.previous_version ?? '—'}</dd>
              <dt>rule_added</dt><dd className="change-added">+{versionSnapshot.rule_added_count}</dd>
              <dt>rule_removed</dt><dd className="change-removed">-{versionSnapshot.rule_removed_count}</dd>
              <dt>parameter_changed</dt><dd>{versionSnapshot.parameter_changed_count}</dd>
              <dt>threshold_changed</dt><dd>{versionSnapshot.threshold_changed_count}</dd>
            </dl>
          </div>
        )}
      </div>

      {/* Rule sets */}
      <div className="rulesets-section">
        <h3>规则集</h3>
        <div className="rulesets-list">
          {boundRulesets.map(rs => {
            const rsRules = rs.rule_ids.map(rid => mockRules.find(r => r.id === rid)).filter(Boolean) as RuleSummary[];
            const isExpanded = expandedRuleset === rs.ruleset_id;
            return (
              <div key={rs.ruleset_id} className={`ruleset-card ${isExpanded ? 'expanded' : ''}`}>
                <div className="ruleset-header" onClick={() => setExpandedRuleset(isExpanded ? null : rs.ruleset_id)}>
                  <div className="ruleset-info">
                    <span className="ruleset-name">{rs.name}</span>
                    <code className="ruleset-id">{rs.ruleset_id}</code>
                    <span className="ruleset-priority">P{rs.priority}</span>
                  </div>
                  <div className="ruleset-meta">
                    <span className="rule-count">{rs.rule_ids.length} 条规则</span>
                    <span className={`expand-icon ${isExpanded ? 'expanded' : ''}`}>▶</span>
                  </div>
                </div>
                {isExpanded && (
                  <div className="ruleset-rules">
                    <table className="rule-table">
                      <thead><tr><th>规则 ID</th><th>名称</th><th>级别</th><th>类别</th><th>状态</th></tr></thead>
                      <tbody>
                        {rsRules.map(r => (
                          <tr key={r.id}>
                            <td><code>{r.id}</code></td>
                            <td>{r.name}</td>
                            <td><SeverityTag sev={r.severity} /></td>
                            <td>{r.category}</td>
                            <td><span className={r.enabled ? 'enabled' : 'disabled'}>{r.enabled ? '启用' : '禁用'}</span></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default BaselineDetailPage;