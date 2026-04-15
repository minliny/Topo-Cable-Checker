import apiClient from './client';
import {
  BaselineNodeDTO,
  VersionMetaDTO,
  ValidationResultDTO,
  PublishResultDTO,
  DiffSourceTargetDTO,
  RestoreDraftResultDTO,
  SaveDraftResultDTO,
  LoadDraftResultDTO,
  BaselineVersionRuleSetDTO
} from '../types/dto';
import {
  normalizeBaselineTreeResponse,
  normalizeVersionDetailResponse,
  normalizeValidationResponse,
  normalizePublishResponse,
  normalizeDiffResponse,
  normalizeRestoreDraftResponse,
  normalizeRollbackEffectDiffResponse,
  normalizeBaselineVersionRuleSetResponse
} from './adapters';

export interface ValidateRequest {
  rule_type: string;
  params: Record<string, any>;
}

/** P1.0-1: Explicit publish request matching backend PublishRequestDTO */
export interface PublishRequest {
  rule_id?: string;
  expected_revision?: number;
  rule_type: string;
  target_type?: string;
  severity?: string;
  params: Record<string, any>;
}

/** A1-4: Save draft request matching backend SaveDraftRequestDTO */
export interface SaveDraftRequest {
  baseline_id: string;
  expected_revision: number;
  rule_id?: string;
  rule_type: string;
  target_type?: string;
  severity?: string;
  params: Record<string, any>;
}

export const rulesApi = {
  // Get all baselines
  getBaselines: async (): Promise<BaselineNodeDTO[]> => {
    const raw = await apiClient.get('/baselines');
    return normalizeBaselineTreeResponse(raw);
  },

  bootstrapDefaultBaseline: async (): Promise<void> => {
    await apiClient.post('/baselines/bootstrap-default');
  },

  // Get version meta (Not fully used in mock UI yet, but prepped for real API)
  getVersionMeta: async (baselineId: string, versionId: string): Promise<VersionMetaDTO> => {
    const raw = await apiClient.get(`/baselines/${baselineId}/versions/${versionId}`);
    return normalizeVersionDetailResponse(raw);
  },

  // Validate rule draft
  validateDraft: async (data: ValidateRequest): Promise<ValidationResultDTO> => {
    try {
      const raw = await apiClient.post('/rules/draft/validate', data);
      return normalizeValidationResponse(raw);
    } catch (err: any) {
      // Handle validation errors from HTTP 400s
      return normalizeValidationResponse(err);
    }
  },

  // P1.0-1: Publish baseline rules — sends explicit PublishRequest body
  publishRules: async (baselineId: string, draftData?: any): Promise<PublishResultDTO> => {
    try {
      const raw = await apiClient.post(`/rules/publish/${baselineId}`, draftData);
      return normalizePublishResponse(raw);
    } catch (err: any) {
      // HTTP 400/422 responses during publish often contain blocked_issues
      return normalizePublishResponse(err);
    }
  },

  // Get baseline diff
  getBaselineDiff: async (baselineId: string, sourceId: string, targetId: string): Promise<DiffSourceTargetDTO> => {
    const raw = await apiClient.get(`/baselines/${baselineId}/diff?source=${sourceId}&target=${targetId}`);
    return normalizeDiffResponse(raw, sourceId, targetId);
  },

  getRestoreDraftEffectDiff: async (baselineId: string, targetId: string): Promise<DiffSourceTargetDTO> => {
    const raw = await apiClient.get(`/baselines/${baselineId}/restore-draft-effect-diff?target=${targetId}`);
    return normalizeRollbackEffectDiffResponse(raw, 'previous_version', targetId);
  },

  getBaselineVersionRuleSet: async (baselineId: string, versionId: string): Promise<BaselineVersionRuleSetDTO> => {
    const raw = await apiClient.get(`/baselines/${baselineId}/versions/${versionId}/rule-set`);
    return normalizeBaselineVersionRuleSetResponse(raw);
  },

  restoreHistoricalDraft: async (baselineId: string, versionId: string): Promise<RestoreDraftResultDTO> => {
    const raw = await apiClient.post('/rules/restore-draft', { baseline_id: baselineId, version_id: versionId });
    return normalizeRestoreDraftResponse(raw, baselineId, versionId);
  },

  // A1-4: Save draft — real API call (replaces setTimeout mock)
  saveDraft: async (data: SaveDraftRequest): Promise<SaveDraftResultDTO> => {
    const raw = await apiClient.post<SaveDraftResultDTO, SaveDraftResultDTO>('/rules/draft/save', data);
    return {
      success: raw.success,
      saved_at: raw.saved_at,
      message: raw.message,
      new_revision: (raw as any).new_revision,
    };
  },

  // A1-4/A1-6: Load draft — for draft auto-recovery on page init
  loadDraft: async (baselineId: string): Promise<LoadDraftResultDTO> => {
    const raw = await apiClient.get<LoadDraftResultDTO, LoadDraftResultDTO>(`/rules/draft/${baselineId}`);
    return {
      has_draft: raw.has_draft,
      draft_data: raw.draft_data,
      saved_at: raw.saved_at,
      base_revision: (raw as any).base_revision,
    };
  },

  // A1-4: Clear draft — manual discard
  clearDraft: async (baselineId: string): Promise<void> => {
    await apiClient.delete(`/rules/draft/${baselineId}`);
  },
};
