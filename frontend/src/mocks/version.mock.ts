// mocks/version.mock.ts
// VERSION_CHANGE_SUMMARIES, VERSION_SNAPSHOTS, VERSION_DIFF_SNAPSHOTS
// Migrated from TopoChecker 完整前台.html
// CONSTRAINT: UI must NOT compute version diff; consume VERSION_DIFF_SNAPSHOTS only

import { VersionChangeSummary, VersionSnapshot, VersionDiffSnapshot } from '../models/version';

// key: `${baseline_id}|${version}`
export const VERSION_CHANGE_SUMMARIES: Record<string, VersionChangeSummary> = {
  'bl-001|2.1.0': {
    version_id: 'bl-001|2.1.0', from_version: '2.0.0', to_version: '2.1.0',
    rule_added_count: 2, rule_removed_count: 0, rule_modified_count: 1,
    parameter_changed_keys: ['ntp_drift_ms'], threshold_changed_keys: ['ntp_info'],
    scope_changed_count: 0, ruleset_changed_count: 1,
    change_items: [
      { change_id: 'ci-001', change_type: 'rule_added',      target_type: 'rule',      target_id: 'R-005', target_name: '接口利用率阈值', before_summary: null,    after_summary: '新增容量检查规则', impact_level: 'medium' },
      { change_id: 'ci-002', change_type: 'rule_added',      target_type: 'rule',      target_id: 'R-009', target_name: 'LACP 状态一致', before_summary: null,    after_summary: '新增二层冗余检查', impact_level: 'low' },
      { change_id: 'ci-003', change_type: 'param_changed',   target_type: 'parameter', target_id: 'ntp_drift_ms', target_name: 'NTP 偏差上限', before_summary: '200ms', after_summary: '100ms', impact_level: 'low' },
      { change_id: 'ci-004', change_type: 'threshold_changed', target_type: 'threshold', target_id: 'ntp_info', target_name: 'NTP 偏差提示阈值', before_summary: '200', after_summary: '100', impact_level: 'low' },
      { change_id: 'ci-005', change_type: 'ruleset_changed', target_type: 'ruleset',   target_id: 'rs-004', target_name: '容量与管理集', before_summary: '2 条规则', after_summary: '4 条规则', impact_level: 'medium' },
    ],
  },
  'bl-001|2.0.0': {
    version_id: 'bl-001|2.0.0', from_version: '1.5.0', to_version: '2.0.0',
    rule_added_count: 4, rule_removed_count: 0, rule_modified_count: 3,
    parameter_changed_keys: ['bgp_hold_timer', 'max_util_threshold'], threshold_changed_keys: ['util_warning', 'util_critical'],
    scope_changed_count: 1, ruleset_changed_count: 4,
    change_items: [
      { change_id: 'ci-010', change_type: 'rule_added',    target_type: 'rule',   target_id: 'R-007', target_name: '固件版本一致性', before_summary: null, after_summary: '新增合规检查', impact_level: 'medium' },
      { change_id: 'ci-011', change_type: 'rule_added',    target_type: 'rule',   target_id: 'R-008', target_name: '管理接口可达性', before_summary: null, after_summary: '新增管理检查（初始停用）', impact_level: 'low' },
      { change_id: 'ci-012', change_type: 'scope_changed', target_type: 'scope',  target_id: 'sc-001', target_name: '生产全量范围', before_summary: '仅 role_filter', after_summary: 'role_filter + site_filter', impact_level: 'high' },
    ],
  },
  'bl-001|1.5.0': {
    version_id: 'bl-001|1.5.0', from_version: '1.0.0', to_version: '1.5.0',
    rule_added_count: 1, rule_removed_count: 0, rule_modified_count: 1,
    parameter_changed_keys: [], threshold_changed_keys: [],
    scope_changed_count: 0, ruleset_changed_count: 1,
    change_items: [
      { change_id: 'ci-020', change_type: 'rule_added',    target_type: 'rule', target_id: 'R-004', target_name: 'VLAN 一致性', before_summary: null, after_summary: '新增二层 VLAN 检查', impact_level: 'medium' },
      { change_id: 'ci-021', change_type: 'rule_modified', target_type: 'rule', target_id: 'R-002', target_name: 'BGP 会话健康', before_summary: '条件简单检查', after_summary: '新增 hold_timer 参数条件', impact_level: 'high' },
    ],
  },
};

// key: `${baseline_id}|${version}`
export const VERSION_SNAPSHOTS: Record<string, VersionSnapshot> = {
  'bl-001|2.1.0': { snapshot_id: 'vs-001', baseline_id: 'bl-001', version: '2.1.0', status: 'published',  description: '覆盖 DC-A/DC-B 核心、汇聚、接入三层设备，共 24 条规则。', parameter_profile_id: 'pp-001', threshold_profile_id: 'tp-001', scope_selector_id: 'sc-001', ruleset_ids: ['rs-001', 'rs-002', 'rs-003', 'rs-004'], rule_count: 24, enabled_count: 22, created_at: '2026-01-10', published_at: '2026-03-15' },
  'bl-001|2.0.0': { snapshot_id: 'vs-002', baseline_id: 'bl-001', version: '2.0.0', status: 'deprecated', description: '重构规则分类体系，拆分路由/冗余/合规三类。',                 parameter_profile_id: 'pp-001', threshold_profile_id: 'tp-001', scope_selector_id: 'sc-001', ruleset_ids: ['rs-001', 'rs-002', 'rs-003'],              rule_count: 22, enabled_count: 20, created_at: '2025-12-01', published_at: '2026-01-20' },
  'bl-001|1.5.0': { snapshot_id: 'vs-003', baseline_id: 'bl-001', version: '1.5.0', status: 'deprecated', description: '新增 VLAN 一致性规则，修复 BGP 条件定义。',                  parameter_profile_id: 'pp-001', threshold_profile_id: 'tp-001', scope_selector_id: 'sc-001', ruleset_ids: ['rs-001', 'rs-002'],              rule_count: 18, enabled_count: 18, created_at: '2025-10-01', published_at: '2025-11-10' },
  'bl-002|0.3.0': { snapshot_id: 'vs-005', baseline_id: 'bl-002', version: '0.3.0', status: 'draft',       description: '灾备站点轻量化检查基线。',                                   parameter_profile_id: 'pp-002', threshold_profile_id: 'tp-002', scope_selector_id: 'sc-003', ruleset_ids: ['rs-001', 'rs-002'],              rule_count: 12, enabled_count: 10, created_at: '2026-04-01', published_at: null },
};

// key: `${baseline_id}|${baseline_version}`
export const BASELINE_VERSION_SNAPSHOTS: Record<string, {
  baseline_id: string;
  current_version: string;
  previous_version: string | null;
  rule_added_count: number;
  rule_removed_count: number;
  parameter_changed_count: number;
  threshold_changed_count: number;
}> = {
  'bl-001': { baseline_id: 'bl-001', current_version: '2.1.0', previous_version: '2.0.0', rule_added_count: 2, rule_removed_count: 0, parameter_changed_count: 1, threshold_changed_count: 1 },
  'bl-002': { baseline_id: 'bl-002', current_version: '0.3.0', previous_version: '0.2.0', rule_added_count: 2, rule_removed_count: 0, parameter_changed_count: 2, threshold_changed_count: 0 },
  'bl-003': { baseline_id: 'bl-003', current_version: '1.0.0', previous_version: null,    rule_added_count: 0, rule_removed_count: 0, parameter_changed_count: 0, threshold_changed_count: 0 },
};

// key: `${baseline_id}|${from_version}|${to_version}`
// UI MUST NOT use set operations to compute; consume this map only
export const VERSION_DIFF_SNAPSHOTS: Record<string, VersionDiffSnapshot> = {
  'bl-001|2.0.0|2.1.0': {
    diff_id: 'vd-001', from_version: '2.0.0', to_version: '2.1.0',
    summary: { rule_added_count: 2, rule_removed_count: 0, rule_modified_count: 1, parameter_changed_count: 1, threshold_changed_count: 1, scope_changed_count: 0, ruleset_changed_count: 1 },
    rule_changes: [
      { change_id: 'vd-001-r1', change_type: 'added',    target_id: 'R-005', target_name: '接口利用率阈值', impact_level: 'medium', after_summary: '新增容量检查规则' },
      { change_id: 'vd-001-r2', change_type: 'added',    target_id: 'R-009', target_name: 'LACP 状态一致',  impact_level: 'low',    after_summary: '新增二层冗余检查' },
      { change_id: 'vd-001-r3', change_type: 'modified', target_id: 'R-006', target_name: 'NTP 同步偏差',   impact_level: 'low',    before_summary: 'threshold 200ms', after_summary: 'threshold 100ms' },
    ],
    parameter_changes: [{ change_id: 'vd-001-p1', target_id: 'ntp_drift_ms', target_name: 'NTP 偏差上限', before_summary: '200', after_summary: '100' }],
    threshold_changes: [{ change_id: 'vd-001-t1', target_id: 'ntp_info',     target_name: 'NTP 偏差提示阈值', before_summary: '200', after_summary: '100' }],
    scope_changes: [],
    ruleset_changes: [{ change_id: 'vd-001-rs1', target_id: 'rs-004', target_name: '容量与管理集', before_summary: '2 条', after_summary: '4 条' }],
  },
  'bl-001|1.5.0|2.0.0': {
    diff_id: 'vd-002', from_version: '1.5.0', to_version: '2.0.0',
    summary: { rule_added_count: 4, rule_removed_count: 0, rule_modified_count: 3, parameter_changed_count: 2, threshold_changed_count: 2, scope_changed_count: 1, ruleset_changed_count: 4 },
    rule_changes: [
      { change_id: 'vd-002-r1', change_type: 'added',    target_id: 'R-007', target_name: '固件版本一致性', impact_level: 'medium', after_summary: '新增合规检查' },
      { change_id: 'vd-002-r2', change_type: 'added',    target_id: 'R-008', target_name: '管理接口可达性', impact_level: 'low',    after_summary: '停用状态' },
      { change_id: 'vd-002-r3', change_type: 'modified', target_id: 'R-002', target_name: 'BGP 会话健康',   impact_level: 'high',   before_summary: '简单状态检查', after_summary: '含 hold_timer 参数' },
    ],
    parameter_changes: [
      { change_id: 'vd-002-p1', target_id: 'bgp_hold_timer',     target_name: 'BGP Hold Timer',  before_summary: '90',   after_summary: '180' },
      { change_id: 'vd-002-p2', target_id: 'max_util_threshold', target_name: '最大利用率阈值', before_summary: '0.80', after_summary: '0.85' },
    ],
    threshold_changes: [
      { change_id: 'vd-002-t1', target_id: 'util_warning',  target_name: '利用率警告阈值', before_summary: '0.75', after_summary: '0.80' },
      { change_id: 'vd-002-t2', target_id: 'util_critical', target_name: '利用率严重阈值', before_summary: '0.85', after_summary: '0.90' },
    ],
    scope_changes: [{ change_id: 'vd-002-sc1', target_id: 'sc-001', target_name: '生产全量范围', before_summary: 'role_filter', after_summary: 'role+site filter' }],
    ruleset_changes: [{ change_id: 'vd-002-rs1', target_id: 'rs-003', target_name: '二层检查集', before_summary: '1 条', after_summary: '2 条' }],
  },
};
