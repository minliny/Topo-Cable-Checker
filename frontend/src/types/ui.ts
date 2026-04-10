import { ValidationResult, DiffResponse } from '../api/rules';

export type CenterMode = 
  | 'empty'           // 空白页
  | 'create'          // 新建规则
  | 'edit'            // 编辑规则
  | 'history_detail'  // 历史详情
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

export interface PageState {
  selectedBaselineId?: string;
  selectedVersionId?: string;
  centerMode: CenterMode;
  rightPanelMode: RightPanelMode;
  draftData: DraftData;
  dirty: boolean;
  validationResult: ValidationResult | null;
  diffData: DiffResponse | null;
}
