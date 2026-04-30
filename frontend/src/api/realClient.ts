// api/realClient.ts
// Real API Client
// Implements ApiClient interface using native fetch for HTTP transport
//
// IMPORTANT: Do NOT use axios, react-query, swr, or any HTTP library except native fetch
// Do NOT add real production URLs
// Set baseUrl in config.ts before enabling real mode

import { ApiClient } from './client';
import { getBaseUrl, isRealMode } from './config';
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

interface ApiError {
  code: string;
  message: string;
  details?: Record<string, unknown>;
}

class RealApiTransportError extends Error {
  constructor(
    message: string,
    public readonly code: string,
    public readonly statusCode?: number,
    public readonly details?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'RealApiTransportError';
  }
}

async function requestJson<T>(
  path: string,
  options?: RequestInit
): Promise<T> {
  const baseUrl = getBaseUrl();
  if (!baseUrl) {
    throw new RealApiTransportError(
      'baseUrl is not configured. Set baseUrl in config.ts before using real mode.',
      'CONFIG_MISSING',
      undefined,
      { path }
    );
  }

  const url = `${baseUrl}${path}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  });

  if (!response.ok) {
    let errorBody: ApiError | null = null;
    try {
      errorBody = await response.json();
    } catch {
      // ignore parse error
    }
    throw new RealApiTransportError(
      errorBody?.message ?? `HTTP ${response.status}`,
      errorBody?.code ?? 'HTTP_ERROR',
      response.status,
      errorBody?.details
    );
  }

  return response.json() as Promise<T>;
}

const NOT_IMPLEMENTED = 'Real API client methods are not implemented. Set mode to "real" and configure baseUrl in config.ts to enable.';

export const realApiClient: ApiClient = {
  // ── Baseline ────────────────────────────────────────────────────────────
  async getBaselineList(): Promise<GetBaselineListResponse> {
    if (!isRealMode()) throw new Error(NOT_IMPLEMENTED);
    return requestJson<GetBaselineListResponse>('/api/baselines');
  },

  async getBaselineDetail(baseline_id: string): Promise<GetBaselineDetailResponse> {
    if (!isRealMode()) throw new Error(NOT_IMPLEMENTED);
    return requestJson<GetBaselineDetailResponse>(`/api/baselines/${baseline_id}`);
  },

  async updateBaseline(baseline_id: string, request: UpdateBaselineRequest): Promise<void> {
    if (!isRealMode()) throw new Error(NOT_IMPLEMENTED);
    await requestJson<void>(`/api/baselines/${baseline_id}`, {
      method: 'PATCH',
      body: JSON.stringify(request),
    });
  },

  async getBaselineProfileMapEntry(baseline_id: string): Promise<GetBaselineProfileMapEntryResponse> {
    if (!isRealMode()) throw new Error(NOT_IMPLEMENTED);
    return requestJson<GetBaselineProfileMapEntryResponse>(`/api/baselines/${baseline_id}/profile-map`);
  },

  async getBaselineVersionSnapshot(baseline_id: string): Promise<GetBaselineVersionSnapshotResponse | null> {
    if (!isRealMode()) throw new Error(NOT_IMPLEMENTED);
    return requestJson<GetBaselineVersionSnapshotResponse | null>(`/api/baselines/${baseline_id}/version-snapshot`);
  },

  // ── Rules / Rule Editor ─────────────────────────────────────────────────
  async getRuleDefinitions(): Promise<GetRuleDefinitionsResponse> {
    if (!isRealMode()) throw new Error(NOT_IMPLEMENTED);
    return requestJson<GetRuleDefinitionsResponse>('/api/rules/definitions');
  },

  async getRuleSetList(): Promise<GetRuleSetListResponse> {
    if (!isRealMode()) throw new Error(NOT_IMPLEMENTED);
    return requestJson<GetRuleSetListResponse>('/api/rulesets');
  },

  async updateRuleOverride(request: UpdateRuleOverrideRequest): Promise<void> {
    if (!isRealMode()) throw new Error(NOT_IMPLEMENTED);
    await requestJson<void>(`/api/rules/${request.rule_id}/override`, {
      method: 'PATCH',
      body: JSON.stringify(request),
    });
  },

  // ── Version Management ──────────────────────────────────────────────────
  async getVersionList(baseline_id: string): Promise<GetVersionListResponse> {
    if (!isRealMode()) throw new Error(NOT_IMPLEMENTED);
    return requestJson<GetVersionListResponse>(`/api/baselines/${baseline_id}/versions`);
  },

  async getVersionSnapshot(version_id: string): Promise<GetVersionSnapshotResponse> {
    if (!isRealMode()) throw new Error(NOT_IMPLEMENTED);
    return requestJson<GetVersionSnapshotResponse>(`/api/versions/${version_id}`);
  },

  async getVersionDiff(from_version: string, to_version: string): Promise<GetVersionDiffResponse> {
    if (!isRealMode()) throw new Error(NOT_IMPLEMENTED);
    return requestJson<GetVersionDiffResponse>(`/api/versions/diff?from_version=${encodeURIComponent(from_version)}&to_version=${encodeURIComponent(to_version)}`);
  },

  async createVersion(baseline_id: string, request: CreateVersionRequest): Promise<{ version_id: string }> {
    if (!isRealMode()) throw new Error(NOT_IMPLEMENTED);
    return requestJson<{ version_id: string }>(`/api/baselines/${baseline_id}/versions`, {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  async publishVersion(request: PublishVersionRequest): Promise<void> {
    if (!isRealMode()) throw new Error(NOT_IMPLEMENTED);
    await requestJson<void>(`/api/versions/${request.version_id}/publish`, {
      method: 'POST',
    });
  },

  // ── Execution Config ────────────────────────────────────────────────────
  async getDataSourceList(): Promise<GetDataSourceListResponse> {
    if (!isRealMode()) throw new Error(NOT_IMPLEMENTED);
    return requestJson<GetDataSourceListResponse>('/api/data-sources');
  },

  async getScopeList(): Promise<GetScopeListResponse> {
    if (!isRealMode()) throw new Error(NOT_IMPLEMENTED);
    return requestJson<GetScopeListResponse>('/api/scopes');
  },

  async getRecognitionStatus(): Promise<GetRecognitionStatusResponse> {
    if (!isRealMode()) throw new Error(NOT_IMPLEMENTED);
    return requestJson<GetRecognitionStatusResponse>('/api/recognition/status');
  },

  async startRecognition(request: StartRecognitionRequest): Promise<{ recognition_id: string }> {
    if (!isRealMode()) throw new Error(NOT_IMPLEMENTED);
    return requestJson<{ recognition_id: string }>('/api/recognition/start', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  async confirmRecognition(request: ConfirmRecognitionRequest): Promise<void> {
    if (!isRealMode()) throw new Error(NOT_IMPLEMENTED);
    await requestJson<void>('/api/recognition/confirm', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  async startCheck(request: StartCheckRequest): Promise<{ run_id: string }> {
    if (!isRealMode()) throw new Error(NOT_IMPLEMENTED);
    return requestJson<{ run_id: string }>('/api/checks/start', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  // ── Run History ─────────────────────────────────────────────────────────
  async getRunHistory(): Promise<GetRunHistoryResponse> {
    if (!isRealMode()) throw new Error(NOT_IMPLEMENTED);
    return requestJson<GetRunHistoryResponse>('/api/runs');
  },

  async getRunDetail(run_id: string): Promise<GetRunDetailResponse> {
    if (!isRealMode()) throw new Error(NOT_IMPLEMENTED);
    return requestJson<GetRunDetailResponse>(`/api/runs/${run_id}`);
  },

  // ── Analysis Workbench ──────────────────────────────────────────────────
  async getCheckResultBundle(bundle_id: string): Promise<GetCheckResultBundleResponse> {
    if (!isRealMode()) throw new Error(NOT_IMPLEMENTED);
    return requestJson<GetCheckResultBundleResponse>(`/api/bundles/${bundle_id}`);
  },

  async getIssueDetail(issue_id: string): Promise<GetIssueDetailResponse> {
    if (!isRealMode()) throw new Error(NOT_IMPLEMENTED);
    return requestJson<GetIssueDetailResponse>(`/api/issues/${issue_id}`);
  },

  // ── Diff Compare ─────────────────────────────────────────────────────────
  async getRecheckDiff(base_run_id: string, target_run_id: string): Promise<GetRecheckDiffResponse> {
    if (!isRealMode()) throw new Error(NOT_IMPLEMENTED);
    return requestJson<GetRecheckDiffResponse>(`/api/diff/recheck?base_run_id=${encodeURIComponent(base_run_id)}&target_run_id=${encodeURIComponent(target_run_id)}`);
  },

  // ── Profiles / Selectors ─────────────────────────────────────────────────
  async getParameterProfileList(): Promise<GetParameterProfileListResponse> {
    if (!isRealMode()) throw new Error(NOT_IMPLEMENTED);
    return requestJson<GetParameterProfileListResponse>('/api/profiles/parameters');
  },

  async getThresholdProfileList(): Promise<GetThresholdProfileListResponse> {
    if (!isRealMode()) throw new Error(NOT_IMPLEMENTED);
    return requestJson<GetThresholdProfileListResponse>('/api/profiles/thresholds');
  },

  async getScopeSelectorList(): Promise<GetScopeSelectorListResponse> {
    if (!isRealMode()) throw new Error(NOT_IMPLEMENTED);
    return requestJson<GetScopeSelectorListResponse>('/api/scopes/selectors');
  },
};
