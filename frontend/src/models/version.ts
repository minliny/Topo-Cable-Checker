// models/version.ts
// VersionChangeSummary, VersionSnapshot, VersionDiffSnapshot

import { SeverityLevel } from './profile';

export type ImpactLevel = 'high' | 'medium' | 'low';
export type ChangeType =
  | 'rule_added'
  | 'rule_removed'
  | 'rule_modified'
  | 'param_changed'
  | 'threshold_changed'
  | 'scope_changed'
  | 'ruleset_changed';

export interface VersionChangeItem {
  change_id: string;
  change_type: ChangeType;
  target_type: 'rule' | 'parameter' | 'threshold' | 'scope' | 'ruleset';
  target_id: string;
  target_name: string;
  before_summary: string | null;
  after_summary: string | null;
  impact_level: ImpactLevel;
}

export interface VersionChangeSummary {
  version_id: string;
  from_version: string | null;
  to_version: string;
  rule_added_count: number;
  rule_removed_count: number;
  rule_modified_count: number;
  parameter_changed_keys: string[];
  threshold_changed_keys: string[];
  scope_changed_count: number;
  ruleset_changed_count: number;
  change_items: VersionChangeItem[];
}

export interface VersionSnapshot {
  snapshot_id: string;
  baseline_id: string;
  version: string;
  status: 'published' | 'draft' | 'deprecated';
  description: string;
  parameter_profile_id: string;
  threshold_profile_id: string;
  scope_selector_id: string;
  ruleset_ids: string[];
  rule_count: number;
  enabled_count: number;
  created_at: string;
  published_at: string | null;
}

export interface VersionDiffRuleChange {
  change_id: string;
  change_type: 'added' | 'removed' | 'modified';
  target_id: string;
  target_name: string;
  impact_level: ImpactLevel;
  before_summary?: string;
  after_summary?: string;
}

export interface VersionDiffFieldChange {
  change_id: string;
  target_id: string;
  target_name: string;
  before_summary?: string;
  after_summary?: string;
}

export interface VersionDiffSummary {
  rule_added_count: number;
  rule_removed_count: number;
  rule_modified_count: number;
  parameter_changed_count: number;
  threshold_changed_count: number;
  scope_changed_count: number;
  ruleset_changed_count: number;
}

export interface VersionDiffSnapshot {
  diff_id: string;
  from_version: string;
  to_version: string;
  summary: VersionDiffSummary;
  rule_changes: VersionDiffRuleChange[];
  parameter_changes: VersionDiffFieldChange[];
  threshold_changes: VersionDiffFieldChange[];
  scope_changes: VersionDiffFieldChange[];
  ruleset_changes: VersionDiffFieldChange[];
}
