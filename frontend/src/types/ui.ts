import { ValidationResult, DiffResponse } from '../api/rules';

export type CenterMode = 
  | 'empty'           // 空白页
  | 'edit'            // 编辑规则草稿
  | 'history_detail'  // 历史详情 (只读)
  | 'diff'            // 差异对比主视图
  | 'publish_confirm';// 发布确认视图

export type RightPanelMode = 
  | 'help'            // 字段说明或填写提示
  | 'validation'      // 实时校验结果
  | 'impact'          // 影响分析
  | 'diff_summary'    // 差异导航摘要
  | 'publish_check'   // 发布检查结果
  | 'version_meta';   // 版本元信息

export interface DraftData {
  rule_type?: string;
  params?: string;
}

// Tree structure for left navigation
export interface BaselineTreeNode {
  key: string;        // unique identifier, e.g. "base-001-draft" or "base-001-v1.0"
  title: string;      // display name
  isLeaf?: boolean;
  baselineId: string;
  versionId: string;  // 'draft' or specific version string like 'v1.0'
  status?: 'published' | 'draft' | 'testing';
  children?: BaselineTreeNode[];
}

export interface PageState {
  // Navigation State
  selectedBaselineId?: string;
  selectedVersionId?: string;
  
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
  
  // Cached Results
  validationResult: ValidationResult | null;
  diffData: DiffResponse | null;
  
  // Target positioning (driven by right panel interactions)
  targetFieldPath?: string;
  targetRuleId?: string;
}
