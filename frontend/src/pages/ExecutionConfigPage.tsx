// pages/ExecutionConfigPage.tsx
// P0 CONSTRAINT: "开始检查" is ONLY enabled when recognitionStatus === 'confirmed'
// P0 CONSTRAINT: DataSource and ExecutionScope must come from structural models, never hardcoded strings
// P0 CONSTRAINT: ParameterProfile / ThresholdProfile shown as structured snapshot

import React, { useState, useEffect } from 'react';
import { DataSource, ExecutionScope, RecognitionResult, RecognitionStatus } from '../models/execution';
import { Baseline } from '../models/baseline';
import { ParameterProfile, ThresholdProfile } from '../models/profile';
import { getDataSourceList, getScopeList, getBaselineProfileMapEntry, getParameterProfileList, getThresholdProfileList } from '../api';

export interface ExecutionConfigPageProps {
  baselines: Baseline[];
  onRunComplete: (runConfig: {
    baseline_id: string;
    baseline_version: string;
    scenario_id: string;
    dataset_id: string;
    scope_id: string;
  }) => void;
  initialBaselineId?: string;
}

const SCENARIOS = [
  { id: 's1', name: '全量拓扑检查' },
  { id: 's2', name: '链路冗余检查' },
  { id: 's3', name: 'BGP 会话审计' },
  { id: 's4', name: 'VLAN 一致性检查' },
];

export const ExecutionConfigPage: React.FC<ExecutionConfigPageProps> = ({
  baselines,
  onRunComplete,
  initialBaselineId,
}) => {
  const [dataSources, setDataSources] = useState<DataSource[]>([]);
  const [executionScopes, setExecutionScopes] = useState<ExecutionScope[]>([]);
  const [parameterProfiles, setParameterProfiles] = useState<ParameterProfile[]>([]);
  const [thresholdProfiles, setThresholdProfiles] = useState<ThresholdProfile[]>([]);
  const [profileBinding, setProfileBinding] = useState<{ parameter_profile_id: string; threshold_profile_id: string; scope_selector_id: string; ruleset_ids: string[] } | null>(null);

  const [selBaselineId, setSelBaselineId] = useState(initialBaselineId ?? baselines[0]?.id ?? '');
  const [selScenarioId, setSelScenarioId] = useState<string>(SCENARIOS[0]?.id ?? SCENARIOS[0].id);
  const [selDatasetId, setSelDatasetId] = useState<string>('');
  const [selScopeId, setSelScopeId] = useState<string>('');

  // P0: recognition_status state machine
  const [recognitionStatus, setRecognitionStatus] = useState<RecognitionStatus>('not_started');
  const [recognitionResult, setRecognitionResult] = useState<RecognitionResult | null>(null);
  const [recognizing, setRecognizing] = useState(false);
  const [running, setRunning] = useState(false);

  // Load data sources and scopes
  useEffect(() => {
    getDataSourceList().then(setDataSources);
    getScopeList().then(setExecutionScopes);
    getParameterProfileList().then(setParameterProfiles);
    getThresholdProfileList().then(setThresholdProfiles);
  }, []);

  // Load profile binding when baseline changes
  useEffect(() => {
    if (selBaselineId) {
      getBaselineProfileMapEntry(selBaselineId).then(setProfileBinding);
    } else {
      setProfileBinding(null);
    }
  }, [selBaselineId]);

  // Set default selections once data is loaded
  useEffect(() => {
    if (dataSources.length > 0 && !selDatasetId) {
      setSelDatasetId(dataSources[0].dataset_id);
    }
    if (executionScopes.length > 0 && !selScopeId) {
      setSelScopeId(executionScopes[0].scope_id);
    }
  }, [dataSources, executionScopes, selDatasetId, selScopeId]);

  // Reset recognition when inputs change
  useEffect(() => {
    setRecognitionStatus('not_started');
    setRecognitionResult(null);
  }, [selBaselineId, selDatasetId, selScopeId]);

  const baseline = baselines.find(b => b.id === selBaselineId);
  const dataSource: DataSource | undefined = dataSources.find(d => d.dataset_id === selDatasetId);
  const execScope: ExecutionScope | undefined = executionScopes.find(s => s.scope_id === selScopeId);

  // Profile snapshot from profile service — structural binding, never hardcoded
  const paramProfile: ParameterProfile | undefined = profileBinding?.parameter_profile_id
    ? parameterProfiles.find(p => p.profile_id === profileBinding.parameter_profile_id)
    : undefined;
  const threshProfile: ThresholdProfile | undefined = profileBinding?.threshold_profile_id
    ? thresholdProfiles.find(p => p.profile_id === profileBinding.threshold_profile_id)
    : undefined;

  function handleRecognize(): void {
    setRecognizing(true);
    setRecognitionResult(null);
    setTimeout(() => {
      const result: RecognitionResult = {
        recognized_device_count: dataSource?.device_count ?? 0,
        unmatched_device_count: Math.floor((dataSource?.device_count ?? 0) * 0.05),
        out_of_scope_device_count: Math.floor((dataSource?.device_count ?? 0) * 0.02),
        warnings: ['当前配对暂无识别数据'],
      };
      setRecognitionResult(result);
      setRecognizing(false);
      setRecognitionStatus('ready');
    }, 600);
  }

  function handleConfirm(): void { setRecognitionStatus('confirmed'); }
  function handleReject(): void  { setRecognitionStatus('rejected'); setRecognitionResult(null); }

  // P0: canCheck ONLY true when confirmed
  const canCheck = recognitionStatus === 'confirmed' && !running;

  function handleRun(): void {
    if (!canCheck || !baseline) return;
    setRunning(true);
    setTimeout(() => {
      setRunning(false);
      onRunComplete({
        baseline_id: selBaselineId,
        baseline_version: baseline.version,
        scenario_id: selScenarioId,
        dataset_id: selDatasetId,
        scope_id: selScopeId,
      });
    }, 1500);
  }

  const STEP_LABEL: Record<RecognitionStatus, string> = {
    not_started: '待执行', ready: '待确认', confirmed: '已确认', rejected: '已拒绝',
  };

  return (
    <div className="page execution-config-page">
      <div className="page-header">
        <div>
          <div className="page-title">执行配置</div>
          <div className="page-sub">完成识别确认后才可开始检查 · 当前识别状态：<code>{STEP_LABEL[recognitionStatus]}</code></div>
        </div>
      </div>

      {/* Step 1: Baseline */}
      <section className="exec-section">
        <h4>① 检查基线</h4>
        <select value={selBaselineId} onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setSelBaselineId(e.target.value)}>
          {baselines.filter(b => b.status !== 'deprecated').map(b => (
            <option key={b.id} value={b.id}>{b.name} — v{b.version} ({b.status})</option>
          ))}
        </select>
        {baseline && (
          <dl className="kv-grid">
            <dt>规则数</dt><dd>{baseline.enabled_count} / {baseline.rule_count} 启用</dd>
            <dt>识别方式</dt><dd>{baseline.identification_strategy.method}</dd>
            <dt>识别字段</dt><dd>{baseline.identification_strategy.id_fields.join(', ')}</dd>
          </dl>
        )}
        {/* P1: ParameterProfile / ThresholdProfile snapshot — structural binding */}
        {(paramProfile || threshProfile) && (
          <div className="profile-snapshot-row">
            {paramProfile && (
              <div className="profile-card">
                <span className="profile-label">ParameterProfile</span>
                <code>{paramProfile.profile_id}</code>
                <span>{paramProfile.name} · {paramProfile.parameters.length} 个参数</span>
              </div>
            )}
            {threshProfile && (
              <div className="profile-card">
                <span className="profile-label">ThresholdProfile</span>
                <code>{threshProfile.profile_id}</code>
                <span>{threshProfile.name} · {threshProfile.thresholds.length} 个阈值</span>
              </div>
            )}
          </div>
        )}
      </section>

      {/* Step 2: Scenario */}
      <section className="exec-section">
        <h4>② 检查场景</h4>
        <select value={selScenarioId} onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setSelScenarioId(e.target.value)}>
          {SCENARIOS.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
        </select>
      </section>

      {/* Step 3: DataSource — structural binding from DataSource model, never hardcoded */}
      <section className="exec-section">
        <h4>③ 数据来源</h4>
        <select value={selDatasetId} onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setSelDatasetId(e.target.value)}>
          {dataSources.map(d => <option key={d.dataset_id} value={d.dataset_id}>{d.name}</option>)}
        </select>
        {dataSource && (
          <dl className="kv-grid">
            <dt>dataset_id</dt><dd><code>{dataSource.dataset_id}</code></dd>
            <dt>type</dt><dd><code>{dataSource.type}</code></dd>
            <dt>updated_at</dt><dd>{dataSource.updated_at}</dd>
            <dt>设备数</dt><dd>{dataSource.device_count}</dd>
            <dt>链路数</dt><dd>{dataSource.link_count}</dd>
          </dl>
        )}
      </section>

      {/* Step 4: ExecutionScope — structural binding from ExecutionScope model, never hardcoded */}
      <section className="exec-section">
        <h4>④ 执行范围</h4>
        <select value={selScopeId} onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setSelScopeId(e.target.value)}>
          {executionScopes.map(s => <option key={s.scope_id} value={s.scope_id}>{s.scope_id} — {s.method}</option>)}
        </select>
        {execScope && (
          <dl className="kv-grid">
            <dt>method</dt><dd>{execScope.method}</dd>
            <dt>scope_fields</dt><dd>{execScope.scope_fields.join(', ')}</dd>
            <dt>included_groups</dt><dd>{execScope.included_groups.join(', ') || '—'}</dd>
            <dt>excluded_groups</dt><dd>{execScope.excluded_groups.join(', ') || '—'}</dd>
          </dl>
        )}
      </section>

      {/* Step 5: Recognition — P0 guard */}
      <section className="exec-section recognition-section">
        <div className="section-header">
          <h4>⑤ 识别确认</h4>
          {(recognitionStatus === 'not_started' || recognitionStatus === 'rejected') && (
            <button onClick={handleRecognize} disabled={recognizing}>
              {recognizing ? '识别中…' : '执行识别'}
            </button>
          )}
        </div>
        {recognitionStatus === 'not_started' && !recognizing && (
          <p className="hint">点击「执行识别」查看识别结果，确认后方可开始检查。</p>
        )}
        {recognizing && <p>识别中，请稍候…</p>}
        {recognitionResult && recognitionStatus !== 'not_started' && (
          <div className="recognition-result">
            <div className="recognition-stats">
              <div className="stat good"><span>{recognitionResult.recognized_device_count}</span><label>已识别设备</label></div>
              <div className="stat warn"><span>{recognitionResult.unmatched_device_count}</span><label>未匹配设备</label></div>
              <div className="stat neutral"><span>{recognitionResult.out_of_scope_device_count}</span><label>超出范围</label></div>
            </div>
            {recognitionResult.warnings.length > 0 && (
              <ul className="recognition-warnings">
                {recognitionResult.warnings.map((w, i) => <li key={i}>⚠ {w}</li>)}
              </ul>
            )}
            {recognitionStatus === 'ready' && (
              <div className="recognition-actions">
                <button onClick={handleConfirm} className="btn btn-primary">确认识别结果</button>
                <button onClick={handleReject}  className="btn btn-danger">拒绝并重新配置</button>
              </div>
            )}
            {recognitionStatus === 'confirmed' && <p className="confirmed">✓ 识别结果已确认 — 可开始检查</p>}
            {recognitionStatus === 'rejected'  && <p className="rejected">✗ 已拒绝，请重新配置后执行识别。</p>}
          </div>
        )}
      </section>

      {/* Step 6: Submit — P0: disabled until confirmed */}
      <button
        className="btn btn-primary btn-lg"
        onClick={handleRun}
        disabled={!canCheck}
        aria-disabled={!canCheck}
      >
        {running ? '检查中…' : canCheck ? '▶ 开始检查' : '▶ 开始检查（请先完成识别确认）'}
      </button>
    </div>
  );
};

export default ExecutionConfigPage;
