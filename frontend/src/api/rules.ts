import apiClient from './client';
import {
  BaselineNodeDTO,
  VersionMetaDTO,
  ValidationResultDTO,
  PublishResultDTO,
  DiffSourceTargetDTO,
  RollbackCandidateDTO,
  SaveDraftResultDTO,
  LoadDraftResultDTO
} from '../types/dto';
import {
  normalizeBaselineTreeResponse,
  normalizeVersionDetailResponse,
  normalizeValidationResponse,
  normalizePublishResponse,
  normalizeDiffResponse,
  normalizeRollbackCandidateResponse
} from './adapters';

export interface ValidateRequest {
  rule_type: string;
  params: Record<string, any>;
}

/** P1.0-1: Explicit publish request matching backend PublishRequestDTO */
export interface PublishRequest {
  rule_id?: string;
  rule_type: string;
  target_type?: string;
  severity?: string;
  params: Record<string, any>;
}

/** A1-4: Save draft request matching backend SaveDraftRequestDTO */
export interface SaveDraftRequest {
  baseline_id: string;
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
  publishRules: async (baselineId: string, rule_set: Record<string, any>, changeNote?: string): Promise<PublishResultDTO> => {
    try {
      const raw = await apiClient.post(`/rules/publish/${baselineId}`, {
        rule_set,
        change_note: changeNote
      });
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

  // Rollback Create
  createRollbackCandidate: async (baselineId: string, versionId: string): Promise<RollbackCandidateDTO> => {
    const raw = await apiClient.post('/rules/rollback', { baseline_id: baselineId, version_id: versionId });
    return normalizeRollbackCandidateResponse(raw, baselineId, versionId);
  },

  // A1-4: Save draft — real API call (replaces setTimeout mock)
  saveDraft: async (payload: { baseline_id: string; rule_set: any; active_rule_id?: string }): Promise<SaveDraftResultDTO> => {
    console.log(`[rulesApi.saveDraft] Request payload:`, payload);
    const raw = await apiClient.post<SaveDraftResultDTO, SaveDraftResultDTO>('/rules/draft/save', payload);
    console.log(`[rulesApi.saveDraft] Success:`, raw);
    return {
      success: raw.success,
      saved_at: raw.saved_at,
      draft_snapshot: raw.draft_snapshot,
    };
  },

  // A1-4/A1-6: Load draft — for draft auto-recovery on page init
  loadDraft: async (baselineId: string): Promise<LoadDraftResultDTO> => {
    const raw = await apiClient.get<LoadDraftResultDTO, LoadDraftResultDTO>(`/rules/draft/${baselineId}`);
    return {
      has_draft: raw.has_draft,
      draft_data: raw.draft_data,
      saved_at: raw.saved_at,
    };
  },

  // A1-4: Clear draft — manual discard
  clearDraft: async (baselineId: string): Promise<void> => {
    await apiClient.delete(`/rules/draft/${baselineId}`);
  },
};
