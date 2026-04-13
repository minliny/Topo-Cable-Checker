import { ValidationResultDTO, DiffSourceTargetDTO } from './dto';

export type CenterMode = 
  | 'empty'
  | 'edit'
  | 'history_detail'
  | 'diff'
  | 'publish_confirm'
  | 'publish_checking'
  | 'publish_blocked'
  | 'publishing'
  | 'published'
  | 'rollback_confirm'
  | 'rollback_preparing'
  | 'rollback_ready_edit';

export type RightPanelMode = 
  | 'help'
  | 'validation'
  | 'impact'
  | 'diff_summary'
  | 'publish_check'
  | 'version_meta';

export interface DraftData {
  rule_set: Record<string, any>;
  active_rule_id?: string;
  is_dirty: boolean;
  is_saving: boolean;
  saved_at?: string;
}

export type BaselineNodeType = 
  | 'baseline_root'
  | 'working_draft'
  | 'published_version'
  | 'rollback_candidate';

// Tree structure for left navigation
export interface BaselineTreeNode {
  key: string;
  title: string;
  type: BaselineNodeType;
  isLeaf?: boolean;
  baselineId: string;
  parentId?: string;
  versionId: string;
  sourceVersionId?: string;
  sourceVersionLabel?: string;
  status?: 'published' | 'draft' | 'testing';
  children?: BaselineTreeNode[];
}

export interface PageState {
  // Navigation State
  selectedBaselineId?: string;
  selectedVersionId?: string;
  selectedNodeType?: BaselineNodeType;
  
  // View State
  centerMode: CenterMode;
  rightPanelMode: RightPanelMode;
  
  // Data State
  draftData: DraftData;
  dirty: boolean;
  
  // Validation / Blocking Info
  validationResult: ValidationResultDTO | null;
  publishBlockedIssues: any[] | null;
  
  // Target positioning
  targetFieldPath?: string;
  targetRuleId?: string;
  
  // Diff Info
  diffData: DiffSourceTargetDTO | null;
  diffContext?: {
    sourceVersionId: string;
    targetVersionId: string;
  };
}
