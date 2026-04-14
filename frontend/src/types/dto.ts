/**
 * GET /api/baselines
 * Maps to left navigation tree
 */
export interface BaselineNodeDTO {
  id: string; // UI requirement
  type: 'baseline_root' | 'working_draft' | 'published_version' | 'rollback_candidate'; // UI requirement
  name: string; // UI requirement
  baseline_id: string; // UI requirement
  parent_id?: string;
  version_id?: string; // UI requirement
  source_version_id?: string; // Used for UI state recovery (rollback)
  source_version_label?: string; // Used for UI display
  status?: 'draft' | 'testing' | 'published';
  created_at?: string;
  updated_at?: string;
}

/**
 * GET /api/baselines/{id}/versions/{version_id}
 * Maps to right panel version_meta
 */
export interface VersionMetaDTO {
  version_id: string; // UI requirement
  baseline_id: string; // UI requirement
  version_label: string; // UI requirement
  summary: string; // UI requirement
  publisher: string; // UI requirement
  published_at: string; // UI requirement
  parent_version_id?: string;
}

/**
 * POST /api/rules/draft/validate
 * Error issue model
 */
export interface ValidationIssueDTO {
  field_path: string; // Used for UI jump-to-field
  issue_type: 'error' | 'warning'; // UI requirement
  message: string; // UI requirement
  suggestion?: string;
}

export interface ValidationResultDTO {
  valid: boolean; // UI requirement
  issues: ValidationIssueDTO[]; // UI requirement
  errors?: string[]; // Legacy alias — some paths still use this
  evidence?: Record<string, any>; // Optional evidence blob
}

/**
 * POST /api/rules/publish/{baseline_id}
 */
export interface PublishResultDTO {
  success: boolean; // UI requirement
  version_id?: string; // Used for UI state recovery
  version_label?: string; // UI requirement
  summary?: string; // UI requirement
  blocked_issues?: ValidationIssueDTO[]; // Used for publish_blocked UI
}

/**
 * POST /api/rules/rollback
 */
export interface RollbackCandidateDTO {
  baseline_id: string; // UI requirement
  source_version_id: string; // Used for UI state recovery
  source_version_label: string; // UI requirement
  draft_data: any; // Used to hydrate UI editor
  rule_set?: Record<string, any>; // B2: Full rule set for complete rollback
}

/**
 * P1.1-2: Diff models — enhanced with per-field before/after and human-readable summaries
 */
export interface DiffFieldChangeDTO {
  field_name: string;
  old_value: any;
  new_value: any;
}

export interface DiffRuleDTO {
  rule_id: string; // Used for UI jump-to-rule
  change_type: 'added' | 'removed' | 'modified'; // UI requirement
  changed_fields?: string[];
  field_changes?: DiffFieldChangeDTO[]; // P1.1-2: per-field before/after
  old_value?: any;
  new_value?: any;
  human_summary?: string; // P1.1-2: e.g. "severity: warning → error"
}

/**
 * GET /api/baselines/{id}/diff
 */
export interface DiffSourceTargetDTO {
  source_version_id: string; // UI requirement
  target_version_id: string; // UI requirement
  diff_summary: {
    added: number; // UI requirement
    removed: number; // UI requirement
    modified: number; // UI requirement
  };
  human_readable_summary?: string; // P1.1-2: e.g. "2 rules added, 1 modified (severity)"
  rules: DiffRuleDTO[]; // UI requirement
}

/**
 * A1-4: POST /api/rules/draft/save
 */
export interface SaveDraftRequestDTO {
  baseline_id: string;
  rule_id?: string;
  rule_type: string;
  target_type?: string;
  severity?: string;
  params: Record<string, any>;
}

export interface SaveDraftResultDTO {
  success: boolean;
  saved_at?: string;
  message?: string;
}

/**
 * A1-4: GET /api/rules/draft/{baseline_id}
 */
export interface LoadDraftResultDTO {
  has_draft: boolean;
  draft_data?: any;
  saved_at?: string;
}

export interface BaselineVersionRuleSetDTO {
  baseline_id: string;
  version_id: string;
  rule_set: Record<string, any>;
}
