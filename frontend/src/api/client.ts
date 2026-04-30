// api/client.ts
// Minimal ApiClient Interface
// No real http requests, no real endpoints

import {
  GetBaselineListResponse,
  GetBaselineDetailResponse,
  UpdateBaselineRequest,
  GetBaselineProfileMapEntryResponse,
  GetBaselineVersionSnapshotResponse,
  GetRuleDefinitionsResponse,
  GetRuleSetListResponse,
  UpdateRuleOverrideRequest,
  GetVersionListResponse,
  GetVersionSnapshotResponse,
  GetVersionDiffResponse,
  CreateVersionRequest,
  PublishVersionRequest,
  GetDataSourceListResponse,
  GetScopeListResponse,
  GetRecognitionStatusResponse,
  StartRecognitionRequest,
  ConfirmRecognitionRequest,
  StartCheckRequest,
  GetRunHistoryResponse,
  GetRunDetailResponse,
  GetCheckResultBundleResponse,
  GetIssueDetailResponse,
  GetRecheckDiffResponse,
  GetParameterProfileListResponse,
  GetThresholdProfileListResponse,
  GetScopeSelectorListResponse,
} from './contracts';

export interface ApiClient {
  // ── Baseline ────────────────────────────────────────────────────────────
  getBaselineList(): Promise<GetBaselineListResponse>;
  getBaselineDetail(baseline_id: string): Promise<GetBaselineDetailResponse>;
  updateBaseline(baseline_id: string, request: UpdateBaselineRequest): Promise<void>;
  getBaselineProfileMapEntry(baseline_id: string): Promise<GetBaselineProfileMapEntryResponse>;
  getBaselineVersionSnapshot(baseline_id: string): Promise<GetBaselineVersionSnapshotResponse | null>;

  // ── Rules / Rule Editor ─────────────────────────────────────────────────
  getRuleDefinitions(): Promise<GetRuleDefinitionsResponse>;
  getRuleSetList(): Promise<GetRuleSetListResponse>;
  updateRuleOverride(request: UpdateRuleOverrideRequest): Promise<void>;

  // ── Version Management ──────────────────────────────────────────────────
  getVersionList(baseline_id: string): Promise<GetVersionListResponse>;
  getVersionSnapshot(version_id: string): Promise<GetVersionSnapshotResponse>;
  getVersionDiff(from_version: string, to_version: string): Promise<GetVersionDiffResponse>;
  createVersion(baseline_id: string, request: CreateVersionRequest): Promise<{ version_id: string }>;
  publishVersion(request: PublishVersionRequest): Promise<void>;

  // ── Execution Config ────────────────────────────────────────────────────
  getDataSourceList(): Promise<GetDataSourceListResponse>;
  getScopeList(): Promise<GetScopeListResponse>;
  getRecognitionStatus(): Promise<GetRecognitionStatusResponse>;
  startRecognition(request: StartRecognitionRequest): Promise<{ recognition_id: string }>;
  confirmRecognition(request: ConfirmRecognitionRequest): Promise<void>;
  startCheck(request: StartCheckRequest): Promise<{ run_id: string }>;

  // ── Run History ─────────────────────────────────────────────────────────
  getRunHistory(): Promise<GetRunHistoryResponse>;
  getRunDetail(run_id: string): Promise<GetRunDetailResponse>;

  // ── Analysis Workbench ──────────────────────────────────────────────────
  getCheckResultBundle(bundle_id: string): Promise<GetCheckResultBundleResponse>;
  getIssueDetail(issue_id: string): Promise<GetIssueDetailResponse>;

  // ── Diff Compare ─────────────────────────────────────────────────────────
  getRecheckDiff(base_run_id: string, target_run_id: string): Promise<GetRecheckDiffResponse>;

  // ── Profiles / Selectors ─────────────────────────────────────────────────
  getParameterProfileList(): Promise<GetParameterProfileListResponse>;
  getThresholdProfileList(): Promise<GetThresholdProfileListResponse>;
  getScopeSelectorList(): Promise<GetScopeSelectorListResponse>;
}

