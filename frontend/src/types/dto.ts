export interface BaselineNodeDTO {
  id: string;
  type: 'baseline_root' | 'working_draft' | 'published_version' | 'rollback_candidate';
  name: string;
  baseline_id: string;
  parent_id?: string;
  version_id?: string;
  source_version_id?: string;
  source_version_label?: string;
  status?: 'draft' | 'testing' | 'published';
  created_at?: string;
  updated_at?: string;
}

export interface VersionMetaDTO {
  version_id: string;
  baseline_id: string;
  version_label: string;
  summary: string;
  publisher: string;
  published_at: string;
  parent_version_id?: string;
}

export interface ValidationIssueDTO {
  field_path: string;
  issue_type: 'error' | 'warning';
  message: string;
  suggestion?: string;
}

export interface ValidationResultDTO {
  valid: boolean;
  issues: ValidationIssueDTO[];
}

export interface PublishResultDTO {
  success: boolean;
  version_id?: string;
  version_label?: string;
  summary?: string;
  blocked_issues?: ValidationIssueDTO[];
}

export interface RollbackCandidateDTO {
  baseline_id: string;
  source_version_id: string;
  source_version_label: string;
  draft_data: any;
}

export interface DiffRuleDTO {
  rule_id: string;
  change_type: 'added' | 'removed' | 'modified';
  changed_fields?: string[];
  old_value?: any;
  new_value?: any;
}

export interface DiffSourceTargetDTO {
  source_version_id: string;
  target_version_id: string;
  diff_summary: {
    added: number;
    removed: number;
    modified: number;
  };
  rules: DiffRuleDTO[];
}
