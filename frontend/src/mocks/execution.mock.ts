// mocks/execution.mock.ts
// DataSource, ExecutionScope, RecognitionResults, CheckResultBundle runs
// Migrated from TopoChecker 完整前台.html

import { DataSource, ExecutionScope, RecognitionResult, CheckResultBundle, IssueItem } from '../models/execution';

export const DATA_SOURCES: DataSource[] = [
  { dataset_id: 'ds-prod-20260420', name: '生产网络快照 2026-04-20', type: 'offline_snapshot', updated_at: '2026-04-20T06:00:00Z', sheet_count: 4, device_count: 24, link_count: 38 },
  { dataset_id: 'ds-prod-20260419', name: '生产网络快照 2026-04-19', type: 'offline_snapshot', updated_at: '2026-04-19T06:00:00Z', sheet_count: 4, device_count: 24, link_count: 38 },
  { dataset_id: 'ds-dr-20260418',   name: 'DR 站点快照 2026-04-18',  type: 'offline_snapshot', updated_at: '2026-04-18T18:00:00Z', sheet_count: 2, device_count: 12, link_count: 16 },
];

export const EXECUTION_SCOPES: ExecutionScope[] = [
  { scope_id: 'scope-all',       method: 'role_filter', scope_fields: ['role', 'site'], included_groups: ['core', 'aggregation', 'access'], excluded_groups: [] },
  { scope_id: 'scope-core-only', method: 'role_filter', scope_fields: ['role'],         included_groups: ['core'],                          excluded_groups: [] },
  { scope_id: 'scope-dr',        method: 'site_filter', scope_fields: ['site'],         included_groups: ['DC-DR'],                         excluded_groups: [] },
];

// key: `${dataset_id}|${scope_id}`
export const RECOGNITION_RESULTS: Record<string, RecognitionResult> = {
  'ds-prod-20260420|scope-all':    { recognized_device_count: 22, unmatched_device_count: 2, out_of_scope_device_count: 0,  warnings: ['core-sw-04 hostname 无法匹配，已跳过', 'access-sw-15 mgmt_ip 缺失'] },
  'ds-prod-20260420|scope-core-only': { recognized_device_count: 3, unmatched_device_count: 0, out_of_scope_device_count: 19, warnings: [] },
  'ds-prod-20260419|scope-all':    { recognized_device_count: 22, unmatched_device_count: 2, out_of_scope_device_count: 0,  warnings: ['core-sw-04 hostname 无法匹配，已跳过', 'access-sw-15 mgmt_ip 缺失'] },
  'ds-dr-20260418|scope-dr':       { recognized_device_count: 10, unmatched_device_count: 2, out_of_scope_device_count: 0,  warnings: ['dr-sw-03 firmware 字段缺失'] },
};

// Minimal mock issues (full set lives in prototype for reference)
const MOCK_ISSUES: IssueItem[] = [
  {
    id: 'i1', ruleId: 'TOPO-001', rule_id: 'R-001', rule_name: '核心上行冗余', rule_category: '冗余', severity: 'critical',
    title: '单点故障：core-sw-03 无冗余上行链路', anchor_type: 'device', anchor_id: 'core-sw-03',
    source_device: 'core-sw-03', source_port: 'uplink-A2', target_device: 'agg-sw-02', target_port: 'downlink-3',
    description: '设备 core-sw-03 仅有一条活跃上行链路。', remediation: '添加第二条上行链路。',
    evidence: { expected_value: '2', actual_value: '1', comparison_operator: '>=', evidence_type: 'threshold', field_name: 'active_uplinks_count' },
    _diff_items: [{ type: 'changed', field: 'uplink-A2.status', old: 'up', new: 'down' }],
  },
  {
    id: 'i2', ruleId: 'TOPO-007', rule_id: 'R-002', rule_name: 'BGP 会话健康', rule_category: '路由', severity: 'critical',
    title: 'edge-r-01 与 ISP-peer-A 之间 BGP 会话已断开', anchor_type: 'bgp_session', anchor_id: 'edge-r-01::ISP-peer-A',
    source_device: 'edge-r-01', source_port: 'isp-link-A', target_device: 'ISP-peer-A', target_port: '—',
    description: 'BGP 会话断开超过 15 分钟。', remediation: '检查物理连通性和 BGP 计时器配置。',
    evidence: { expected_value: 'Established', actual_value: 'Idle', comparison_operator: '==', evidence_type: 'state_check', field_name: 'bgp.session.state' },
    _diff_items: [{ type: 'changed', field: 'isp-link-A.status', old: 'up', new: 'down' }],
  },
];

export const INIT_RUNS: CheckResultBundle[] = [
  { id: 'run-20260420-1432', baseline_id: 'bl-001', baseline_version: '2.1.0', scenario_id: 's1', scenario: '全量拓扑检查', time: '今日 14:32', score: 54, issues: MOCK_ISSUES },
  { id: 'run-20260420-0901', baseline_id: 'bl-001', baseline_version: '2.1.0', scenario_id: 's1', scenario: '全量拓扑检查', time: '今日 09:01', score: 71, issues: MOCK_ISSUES.filter(i => i.id !== 'i2') },
  { id: 'run-20260419-1800', baseline_id: 'bl-001', baseline_version: '2.0.0', scenario_id: 's2', scenario: '链路冗余检查', time: '昨日 18:00', score: 68, issues: MOCK_ISSUES.filter(i => i.id === 'i1') },
];
