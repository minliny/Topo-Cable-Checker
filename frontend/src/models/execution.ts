// models/execution.ts
// DataSource, ExecutionScope, RecognitionResult, CheckResultBundle, IssueItem

import { SeverityLevel } from './profile';
import { ScopeMethod } from './scope';

// ── Data Source ────────────────────────────────────────────────────────────
export type DataSourceType = 'offline_snapshot' | 'live_pull' | 'file_import';

export interface DataSource {
  dataset_id: string;
  name: string;
  type: DataSourceType;
  updated_at: string;
  sheet_count: number;
  device_count: number;
  link_count: number;
}

// ── Execution Scope ────────────────────────────────────────────────────────
// ScopeMethod imported from scope.ts — single source of truth

export interface ExecutionScope {
  scope_id: string;
  method: ScopeMethod;
  scope_fields: string[];
  included_groups: string[];
  excluded_groups: string[];
}

// ── Recognition ───────────────────────────────────────────────────────────
export type RecognitionStatus = 'not_started' | 'ready' | 'confirmed' | 'rejected';

export interface RecognitionResult {
  recognized_device_count: number;
  unmatched_device_count: number;
  out_of_scope_device_count: number;
  warnings: string[];
}

// ── Issue ──────────────────────────────────────────────────────────────────
export interface IssueEvidence {
  expected_value: string;
  actual_value: string;
  comparison_operator: string;
  evidence_type: string;
  field_name: string;
  related_values?: Record<string, string>;
  raw_snapshot?: unknown;
}

export interface ReviewContextDevice {
  id: string;
  role: string;
  vendor: string;
  model: string;
  firmware: string;
  mgmt_ip: string;
}

export interface ReviewContextPort {
  device: string;
  port: string;
  status: string;
  speed: string;
  peer: string;
}

export interface ReviewContextLink {
  id: string;
  from: string;
  to: string;
  status: string;
  utilization: string;
}

export interface ReviewContext {
  related_devices: ReviewContextDevice[];
  related_ports: ReviewContextPort[];
  related_links: ReviewContextLink[];
  related_issues?: string[];
  topology_snapshot?: unknown;
}

export interface IssueItem {
  id: string;
  ruleId: string;
  rule_id: string;
  rule_name: string;
  rule_category: string;
  severity: SeverityLevel;
  title: string;
  anchor_type: string;
  anchor_id: string;
  source_device: string;
  source_port: string;
  target_device: string;
  target_port: string;
  description: string;
  remediation: string;
  evidence: IssueEvidence;
  // mock-private fields (simulate separate API responses)
  _review_context?: ReviewContext;
  _diff_items?: Array<{ type: 'added' | 'removed' | 'changed'; field: string; old: string | null; new: string | null }>;
}

// ── Check Result Bundle ────────────────────────────────────────────────────
export interface CheckResultBundle {
  id: string;
  baseline_id: string;
  baseline_version: string;
  scenario_id: string;
  scenario: string;
  time: string;
  score: number;
  issues: IssueItem[];
  data_source?: string;
  execution_scope?: string;
}

// ── Run History ────────────────────────────────────────────────────────────
export type RunStatus = 'pending' | 'running' | 'completed' | 'failed';

export interface SeveritySummary {
  critical: number;
  warning: number;
  info: number;
}

export interface CategorySummary {
  category: string;
  count: number;
}

export interface RunHistoryEntry {
  run_id: string;
  baseline_id: string;
  baseline_version: string;
  scenario_id: string;
  scenario_name: string;
  status: RunStatus;
  started_at: string;
  completed_at: string;
  data_source_id: string;
  scope_id: string;
  issue_total: number;
  severity_summary: SeveritySummary;
  category_summary?: CategorySummary[];
  check_result_bundle_id?: string;
}
