// api/contracts.ts
// API Contract Types for TopoChecker Frontend

import {
  Baseline,
  RuleSet,
  RuleDefinition,
} from '../models/baseline';
import {
  VersionChangeSummary,
  VersionSnapshot,
  VersionDiffSnapshot,
} from '../models/version';
import {
  DataSource,
  ExecutionScope,
  RecognitionResult,
  CheckResultBundle,
  IssueItem,
  RunHistoryEntry,
  SeveritySummary,
} from '../models/execution';
import {
  RecheckDiffSnapshot,
} from '../models/diff';
import {
  ParameterProfile,
  ThresholdProfile,
} from '../models/profile';
import {
  ScopeSelector,
} from '../models/scope';

// ── Response Wrapper ───────────────────────────────────────────────────────
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  error?: string;
}

// ── Baseline Endpoints ──────────────────────────────────────────────────────
export interface GetBaselineListResponse {
  baselines: Baseline[];
}

export interface GetBaselineDetailResponse {
  baseline: Baseline;
  rulesets: RuleSet[];
  rules: RuleDefinition[];
  parameter_profile?: ParameterProfile;
  threshold_profile?: ThresholdProfile;
  scope_selector?: ScopeSelector;
}

export interface UpdateBaselineRequest {
  name?: string;
  description?: string;
  status?: 'published' | 'draft' | 'deprecated';
  identification_strategy?: object;
  naming_template?: string;
  parameter_profile_id?: string;
  threshold_profile_id?: string;
  scope_selector_id?: string;
  ruleset_ids?: string[];
}

export interface GetBaselineProfileMapEntryResponse {
  parameter_profile_id: string;
  threshold_profile_id: string;
  scope_selector_id: string;
  ruleset_ids: string[];
}

export interface GetBaselineVersionSnapshotResponse {
  baseline_id: string;
  current_version: string;
  previous_version: string | null;
  rule_added_count: number;
  rule_removed_count: number;
  parameter_changed_count: number;
  threshold_changed_count: number;
}

// ── Rule Editor Endpoints ───────────────────────────────────────────────────
export interface GetRuleDefinitionsResponse {
  rules: RuleDefinition[];
}

export interface UpdateRuleOverrideRequest {
  rule_id: string;
  rule_overrides: Record<string, number | string | boolean>;
}

export interface GetRuleSetListResponse {
  rulesets: RuleSet[];
}

// ── Version Management Endpoints ────────────────────────────────────────────
export interface GetVersionListResponse {
  versions: VersionSnapshot[];
}

export interface GetVersionSnapshotResponse {
  snapshot: VersionSnapshot;
}

export interface GetVersionDiffResponse {
  diff: VersionDiffSnapshot;
}

export interface CreateVersionRequest {
  description: string;
  status?: 'draft';
}

export interface PublishVersionRequest {
  version_id: string;
}

// ── Execution Config Endpoints ──────────────────────────────────────────────
export interface GetDataSourceListResponse {
  data_sources: DataSource[];
}

export interface GetScopeListResponse {
  scopes: ExecutionScope[];
}

export interface GetRecognitionStatusResponse {
  status: 'not_started' | 'ready' | 'confirmed' | 'rejected';
  result?: RecognitionResult;
}

export interface StartRecognitionRequest {
  dataset_id: string;
  scope_id: string;
}

export interface ConfirmRecognitionRequest {
  confirmed: boolean;
}

export interface StartCheckRequest {
  baseline_id: string;
  scenario_id: string;
}

// ── Run History Endpoints ───────────────────────────────────────────────────
export interface GetRunHistoryResponse {
  runs: RunHistoryEntry[];
}

export interface GetRunDetailResponse {
  run: RunHistoryEntry;
  bundle?: CheckResultBundle;
}

export interface GetSeveritySummaryResponse {
  severity_summary: SeveritySummary;
}

// ── Analysis Workbench Endpoints ────────────────────────────────────────────
export interface GetCheckResultBundleResponse {
  bundle: CheckResultBundle;
}

export interface GetIssueDetailResponse {
  issue: IssueItem;
}

// ── Diff Compare Endpoints ──────────────────────────────────────────────────
export interface GetRecheckDiffResponse {
  diff: RecheckDiffSnapshot;
}

// ── Profiles / Selectors Endpoints ─────────────────────────────────────────
export interface GetParameterProfileListResponse {
  profiles: ParameterProfile[];
}

export interface GetThresholdProfileListResponse {
  profiles: ThresholdProfile[];
}

export interface GetScopeSelectorListResponse {
  selectors: ScopeSelector[];
}

