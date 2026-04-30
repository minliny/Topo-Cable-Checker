// mocks/profiles.mock.ts
// PARAMETER_PROFILES, THRESHOLD_PROFILES, SCOPE_SELECTORS, RULE_SETS
// Migrated from TopoChecker 完整前台.html top-level constants

import { ParameterProfile, ThresholdProfile } from '../models/profile';
import { ScopeSelector } from '../models/scope';
import { RuleSet } from '../models/baseline';

export const PARAMETER_PROFILES: ParameterProfile[] = [
  {
    profile_id: 'pp-001',
    name: '生产环境标准参数',
    description: '适用于 DC-A/DC-B 生产网络',
    parameters: [
      { key: 'min_uplinks',        label: '最小上行链路数',  type: 'number',  value: 2,    unit: '条',  description: '核心设备要求的最少上行链路数量' },
      { key: 'bgp_hold_timer',     label: 'BGP Hold Timer', type: 'number',  value: 180,  unit: '秒',  description: 'BGP 会话保活超时时间' },
      { key: 'max_util_threshold', label: '最大利用率阈值',  type: 'number',  value: 0.85, unit: '',    description: '接口 30m 均值利用率上限（0~1）' },
      { key: 'ntp_drift_ms',       label: 'NTP 偏差上限',   type: 'number',  value: 100,  unit: 'ms',  description: '允许的最大 NTP 时钟偏差' },
    ],
  },
  {
    profile_id: 'pp-002',
    name: 'DR 站点宽松参数',
    description: '灾备站点允许更宽松的参数配置',
    parameters: [
      { key: 'min_uplinks',        label: '最小上行链路数',  type: 'number', value: 1,    unit: '条', description: 'DR 站点允许单上行' },
      { key: 'bgp_hold_timer',     label: 'BGP Hold Timer', type: 'number', value: 90,   unit: '秒', description: 'DR 站点更短的保活超时' },
      { key: 'max_util_threshold', label: '最大利用率阈值',  type: 'number', value: 0.90, unit: '',   description: 'DR 站点允许更高利用率' },
      { key: 'ntp_drift_ms',       label: 'NTP 偏差上限',   type: 'number', value: 200,  unit: 'ms', description: 'DR 站点允许更大时钟偏差' },
    ],
  },
];

export const THRESHOLD_PROFILES: ThresholdProfile[] = [
  {
    profile_id: 'tp-001',
    name: '生产网络阈值配置',
    description: '生产环境标准告警阈值',
    thresholds: [
      { key: 'uplink_critical',  label: '上行链路严重阈值', operator: '<',  value: 2,    severity: 'critical', description: '低于此值触发严重告警' },
      { key: 'util_warning',     label: '利用率警告阈值',   operator: '>',  value: 0.80, severity: 'warning',  description: '超过此值触发警告' },
      { key: 'util_critical',    label: '利用率严重阈值',   operator: '>',  value: 0.90, severity: 'critical', description: '超过此值触发严重告警' },
      { key: 'ntp_info',         label: 'NTP 偏差提示阈值', operator: '>',  value: 100,  severity: 'info',     description: '超过此值触发提示' },
    ],
  },
  {
    profile_id: 'tp-002',
    name: 'DR 站点阈值配置',
    description: '灾备站点宽松告警阈值',
    thresholds: [
      { key: 'uplink_critical', label: '上行链路严重阈值', operator: '<', value: 1,    severity: 'critical', description: 'DR 允许单上行' },
      { key: 'util_warning',    label: '利用率警告阈值',   operator: '>', value: 0.88, severity: 'warning',  description: 'DR 宽松利用率警告' },
    ],
  },
];

export const SCOPE_SELECTORS: ScopeSelector[] = [
  { scope_id: 'sc-001', name: '生产全量范围', method: 'role_filter', scope_fields: ['role', 'site'], included_groups: ['core', 'aggregation', 'access'], excluded_groups: [], description: '覆盖 DC-A/DC-B 所有角色设备' },
  { scope_id: 'sc-002', name: '核心层范围',   method: 'role_filter', scope_fields: ['role'],         included_groups: ['core'],                          excluded_groups: [], description: '仅核心交换机' },
  { scope_id: 'sc-003', name: 'DR 站点范围',  method: 'site_filter', scope_fields: ['site'],         included_groups: ['DC-DR'],                         excluded_groups: [], description: '灾备站点设备' },
];

export const RULE_SETS: RuleSet[] = [
  { ruleset_id: 'rs-001', name: '冗余检查集',   description: '网络冗余性相关规则',       priority: 1, rule_ids: ['R-001', 'R-009'] },
  { ruleset_id: 'rs-002', name: '路由检查集',   description: '路由协议和路径相关规则',   priority: 2, rule_ids: ['R-002', 'R-003'] },
  { ruleset_id: 'rs-003', name: '二层检查集',   description: 'VLAN、STP 等二层协议规则', priority: 3, rule_ids: ['R-004', 'R-010'] },
  { ruleset_id: 'rs-004', name: '容量与管理集', description: '容量、NTP、管理接口规则',  priority: 4, rule_ids: ['R-005', 'R-006', 'R-007', 'R-008'] },
];

// Profile lookup maps
export const PARAMETER_PROFILE_MAP: Record<string, ParameterProfile> =
  Object.fromEntries(PARAMETER_PROFILES.map(p => [p.profile_id, p]));

export const THRESHOLD_PROFILE_MAP: Record<string, ThresholdProfile> =
  Object.fromEntries(THRESHOLD_PROFILES.map(p => [p.profile_id, p]));

export const SCOPE_SELECTOR_MAP: Record<string, ScopeSelector> =
  Object.fromEntries(SCOPE_SELECTORS.map(s => [s.scope_id, s]));

// Baseline → profile binding (supplementary, does not mutate BASELINES)
export const BASELINE_PROFILE_MAP: Record<string, {
  parameter_profile_id: string;
  threshold_profile_id: string;
  scope_selector_id: string;
  ruleset_ids: string[];
}> = {
  'bl-001': { parameter_profile_id: 'pp-001', threshold_profile_id: 'tp-001', scope_selector_id: 'sc-001', ruleset_ids: ['rs-001', 'rs-002', 'rs-003', 'rs-004'] },
  'bl-002': { parameter_profile_id: 'pp-002', threshold_profile_id: 'tp-002', scope_selector_id: 'sc-003', ruleset_ids: ['rs-001', 'rs-002'] },
  'bl-003': { parameter_profile_id: 'pp-001', threshold_profile_id: 'tp-001', scope_selector_id: 'sc-001', ruleset_ids: [] },
};

// Rule → profile binding
export const RULE_PROFILE_MAP: Record<string, {
  parameter_profile_id: string;
  threshold_profile_id: string;
  scope_selector_id: string;
}> = {
  'R-001': { parameter_profile_id: 'pp-001', threshold_profile_id: 'tp-001', scope_selector_id: 'sc-001' },
  'R-002': { parameter_profile_id: 'pp-001', threshold_profile_id: 'tp-001', scope_selector_id: 'sc-001' },
  'R-003': { parameter_profile_id: 'pp-001', threshold_profile_id: 'tp-001', scope_selector_id: 'sc-001' },
  'R-004': { parameter_profile_id: 'pp-001', threshold_profile_id: 'tp-001', scope_selector_id: 'sc-001' },
  'R-005': { parameter_profile_id: 'pp-001', threshold_profile_id: 'tp-001', scope_selector_id: 'sc-001' },
  'R-006': { parameter_profile_id: 'pp-001', threshold_profile_id: 'tp-001', scope_selector_id: 'sc-001' },
  'R-007': { parameter_profile_id: 'pp-001', threshold_profile_id: 'tp-001', scope_selector_id: 'sc-001' },
  'R-008': { parameter_profile_id: 'pp-001', threshold_profile_id: 'tp-001', scope_selector_id: 'sc-001' },
  'R-009': { parameter_profile_id: 'pp-001', threshold_profile_id: 'tp-001', scope_selector_id: 'sc-001' },
  'R-010': { parameter_profile_id: 'pp-001', threshold_profile_id: 'tp-001', scope_selector_id: 'sc-001' },
};
