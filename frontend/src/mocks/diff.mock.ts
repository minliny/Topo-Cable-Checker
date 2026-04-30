// mocks/diff.mock.ts
// RECHECK_DIFF_SNAPSHOTS
// Migrated from TopoChecker 完整前台.html
// UI MUST NOT compute diff; consume this map by key `${base_run_id}|${target_run_id}`

import { RecheckDiffSnapshot } from '../models/diff';

// key: `${base_run_id}|${target_run_id}`
export const RECHECK_DIFF_SNAPSHOTS: Record<string, RecheckDiffSnapshot> = {
  'run-20260420-0901|run-20260420-1432': {
    diff_id: 'diff-001',
    base_run_id: 'run-20260420-0901',
    target_run_id: 'run-20260420-1432',
    summary: { trend: 'degraded', total_before: 5, total_after: 6, delta: 1, severity_diff: { critical: 1, warning: 0, info: 0 } },
    issue_changes: [
      { issue_id: 'i2', diff_type: 'new',              severity_before: null,       severity_after: 'critical', summary: 'BGP 会话断开，备份路径饱和' },
      { issue_id: 'i1', diff_type: 'severity_changed', severity_before: 'warning',  severity_after: 'critical', summary: 'uplink-A2 状态变更，SPOF 升级为严重' },
      { issue_id: 'i3', diff_type: 'remaining',        severity_before: 'warning',  severity_after: 'warning',  summary: '路由不对称持续存在' },
      { issue_id: 'i4', diff_type: 'remaining',        severity_before: 'warning',  severity_after: 'warning',  summary: 'VLAN 200 缺失持续' },
      { issue_id: 'i5', diff_type: 'remaining',        severity_before: 'warning',  severity_after: 'warning',  summary: '利用率超阈值持续' },
      { issue_id: 'i6', diff_type: 'remaining',        severity_before: 'info',     severity_after: 'info',     summary: 'NTP 偏差持续' },
    ],
  },
  'run-20260419-1800|run-20260420-0901': {
    diff_id: 'diff-002',
    base_run_id: 'run-20260419-1800',
    target_run_id: 'run-20260420-0901',
    summary: { trend: 'degraded', total_before: 3, total_after: 5, delta: 2, severity_diff: { critical: 0, warning: 1, info: 1 } },
    issue_changes: [
      { issue_id: 'i4', diff_type: 'new',       severity_before: null,      severity_after: 'warning', summary: 'VLAN 200 缺失为新增问题' },
      { issue_id: 'i6', diff_type: 'new',       severity_before: null,      severity_after: 'info',    summary: 'NTP 偏差为新增问题' },
      { issue_id: 'i1', diff_type: 'remaining', severity_before: 'critical',severity_after: 'critical',summary: 'SPOF 持续' },
      { issue_id: 'i3', diff_type: 'remaining', severity_before: 'warning', severity_after: 'warning', summary: '路由不对称持续' },
      { issue_id: 'i5', diff_type: 'regression',severity_before: null,      severity_after: 'warning', summary: '利用率超阈值回归' },
    ],
  },
  'run-20260419-1800|run-20260420-1432': {
    diff_id: 'diff-003',
    base_run_id: 'run-20260419-1800',
    target_run_id: 'run-20260420-1432',
    summary: { trend: 'degraded', total_before: 3, total_after: 6, delta: 3, severity_diff: { critical: 1, warning: 1, info: 1 } },
    issue_changes: [
      { issue_id: 'i2', diff_type: 'new',              severity_before: null,      severity_after: 'critical', summary: 'BGP 会话新断开' },
      { issue_id: 'i4', diff_type: 'new',              severity_before: null,      severity_after: 'warning',  summary: 'VLAN 200 缺失为新增' },
      { issue_id: 'i6', diff_type: 'new',              severity_before: null,      severity_after: 'info',     summary: 'NTP 偏差为新增' },
      { issue_id: 'i1', diff_type: 'severity_changed', severity_before: 'warning', severity_after: 'critical', summary: 'SPOF 严重度升级' },
      { issue_id: 'i3', diff_type: 'remaining',        severity_before: 'warning', severity_after: 'warning',  summary: '路由不对称持续' },
      { issue_id: 'i5', diff_type: 'regression',       severity_before: null,      severity_after: 'warning',  summary: '利用率超阈值回归' },
    ],
  },
};
