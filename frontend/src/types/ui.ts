import { ValidationResult, DiffResponse } from '../api/rules';

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
  rule_type?: string;
  params?: string;
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
  versionId: string;
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
  
  // Side Effect Requests (State Machine Signals)
  validationRequested: boolean;
  publishRequested: boolean;
  diffRequested: boolean;
  rollbackRequested: boolean;
  
  // Cached Results
  validationResult: ValidationResult | null;
  diffData: DiffResponse | null;
  
  // Target positioning
  targetFieldPath?: string;
  targetRuleId?: string;
}
