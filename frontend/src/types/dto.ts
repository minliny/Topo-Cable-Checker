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
}

/**
 * Diff models
 */
export interface DiffRuleDTO {
  rule_id: string; // Used for UI jump-to-rule
  change_type: 'added' | 'removed' | 'modified'; // UI requirement
  changed_fields?: string[];
  old_value?: any;
  new_value?: any;
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
  rules: DiffRuleDTO[]; // UI requirement
}

