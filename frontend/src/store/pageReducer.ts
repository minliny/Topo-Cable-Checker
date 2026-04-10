import { PageState, CenterMode, RightPanelMode, DraftData, BaselineNodeType } from '../types/ui';

export type PageAction =
  | { type: 'SWITCH_CONTEXT', payload: { baselineId: string; versionId: string; isDraft: boolean; draftData?: DraftData; nodeType?: BaselineNodeType; sourceVersionId?: string; sourceVersionLabel?: string } }
  | { type: 'UPDATE_DRAFT', payload: { draftData: DraftData; dirty: boolean } }
  | { type: 'REQUEST_VALIDATION' }
  | { type: 'VALIDATION_SUCCESS', payload: { result: any } }
  | { type: 'VALIDATION_FAILED' }
  | { type: 'PREPARE_PUBLISH' }
  | { type: 'CANCEL_PUBLISH' }
  | { type: 'REQUEST_PUBLISH' }
  | { type: 'PUBLISH_BLOCKED', payload: { issues: any[] } }
  | { type: 'PUBLISH_SUCCESS', payload: { versionId: string } }
  | { type: 'TRIGGER_POST_PUBLISH_NAVIGATION', payload: { versionId: string } }
  | { type: 'REQUEST_DIFF', payload: { sourceVersionId: string; targetVersionId: string } }
  | { type: 'DIFF_SUCCESS', payload: { diffData: any } }
  | { type: 'DIFF_FAILED' }
  | { type: 'CLOSE_DIFF' }
  | { type: 'REQUEST_ROLLBACK_CONFIRM' }
  | { type: 'CANCEL_ROLLBACK' }
  | { type: 'REQUEST_ROLLBACK' }
  | { type: 'ROLLBACK_READY', payload: { draftData: DraftData; sourceVersionId: string; sourceVersionLabel: string } }
  | { type: 'DISCARD_ROLLBACK_CANDIDATE' }
  | { type: 'JUMP_TO_FIELD', payload: { fieldPath: string } }
  | { type: 'JUMP_TO_RULE', payload: { ruleId: string } }
  | { type: 'CLEAR_DIRTY' };

export function pageReducer(state: PageState, action: PageAction): PageState {
  switch (action.type) {
    case 'SWITCH_CONTEXT':
      return {
        ...state,
        selectedBaselineId: action.payload.baselineId,
        selectedVersionId: action.payload.versionId,
        selectedNodeType: action.payload.nodeType,
        centerMode: action.payload.isDraft ? 'edit' : 'history_detail',
        rightPanelMode: action.payload.isDraft ? 'help' : 'version_meta',
        draftData: action.payload.draftData || {},
        dirty: false,
        validationResult: null,
        publishBlockedIssues: null,
        diffData: null,
        targetFieldPath: undefined,
        targetRuleId: undefined,
        diffContext: undefined,
      };

    case 'UPDATE_DRAFT':
      if (state.centerMode !== 'edit' && state.centerMode !== 'rollback_ready_edit') return state;
      return {
        ...state,
        draftData: action.payload.draftData,
        dirty: action.payload.dirty,
        targetFieldPath: undefined,
      };

    case 'REQUEST_VALIDATION':
      if (state.centerMode !== 'edit' && state.centerMode !== 'rollback_ready_edit') return state;
      return { ...state }; 

    case 'VALIDATION_SUCCESS':
      return {
        ...state,
        validationResult: action.payload.result,
        rightPanelMode: 'validation',
        targetFieldPath: undefined,
      };

    case 'VALIDATION_FAILED':
      return { ...state };

    case 'PREPARE_PUBLISH':
      if (state.centerMode !== 'edit' && state.centerMode !== 'rollback_ready_edit') return state;
      return {
        ...state,
        centerMode: 'publish_confirm',
        rightPanelMode: 'publish_check',
      };

    case 'CANCEL_PUBLISH':
      if (state.centerMode !== 'publish_confirm' && state.centerMode !== 'publish_blocked') return state;
      return {
        ...state,
        centerMode: state.selectedNodeType === 'rollback_candidate' ? 'rollback_ready_edit' : 'edit',
        rightPanelMode: 'validation',
      };

    case 'REQUEST_PUBLISH':
      if (state.centerMode !== 'publish_confirm') return state;
      return {
        ...state,
        centerMode: 'publish_checking',
      };

    case 'PUBLISH_BLOCKED':
      if (state.centerMode !== 'publish_checking') return state;
      return {
        ...state,
        centerMode: 'publish_blocked',
        publishBlockedIssues: action.payload.issues,
      };

    case 'PUBLISH_SUCCESS':
      if (state.centerMode !== 'publish_checking') return state;
      return {
        ...state,
        centerMode: 'published',
        dirty: false,
      };

    case 'TRIGGER_POST_PUBLISH_NAVIGATION':
      if (state.centerMode !== 'published') return state;
      return {
        ...state,
        selectedVersionId: action.payload.versionId,
        selectedNodeType: 'published_version',
        centerMode: 'history_detail',
        rightPanelMode: 'version_meta',
        validationResult: null,
        diffData: null,
      };

    case 'REQUEST_DIFF':
      return { 
        ...state,
        diffContext: {
          sourceVersionId: action.payload.sourceVersionId,
          targetVersionId: action.payload.targetVersionId
        }
      };

    case 'DIFF_SUCCESS':
      return {
        ...state,
        diffData: action.payload.diffData,
        centerMode: 'diff',
        rightPanelMode: 'diff_summary',
      };

    case 'DIFF_FAILED':
      return { 
        ...state,
        diffContext: undefined 
      };

    case 'CLOSE_DIFF':
      return {
        ...state,
        centerMode: state.selectedNodeType === 'working_draft' || state.selectedNodeType === 'rollback_candidate' ? 'edit' : 'history_detail',
        rightPanelMode: state.selectedNodeType === 'working_draft' || state.selectedNodeType === 'rollback_candidate' ? 'help' : 'version_meta',
        diffData: null,
        diffContext: undefined,
      };

    case 'REQUEST_ROLLBACK_CONFIRM':
      if (state.centerMode !== 'history_detail') return state;
      return {
        ...state,
        centerMode: 'rollback_confirm',
      };

    case 'CANCEL_ROLLBACK':
      if (state.centerMode !== 'rollback_confirm') return state;
      return {
        ...state,
        centerMode: 'history_detail',
      };

    case 'REQUEST_ROLLBACK':
      if (state.centerMode !== 'rollback_confirm') return state;
      return {
        ...state,
        centerMode: 'rollback_preparing',
      };

    case 'ROLLBACK_READY':
      if (state.centerMode !== 'rollback_preparing') return state;
      return {
        ...state,
        centerMode: 'rollback_ready_edit',
        rightPanelMode: 'help',
        draftData: action.payload.draftData,
        dirty: true,
        selectedNodeType: 'rollback_candidate',
        selectedVersionId: 'draft',
      };
      
    case 'DISCARD_ROLLBACK_CANDIDATE':
      return {
        ...state,
        selectedNodeType: 'working_draft',
        dirty: false,
        centerMode: 'empty',
        draftData: {}
      };

    case 'JUMP_TO_FIELD':
      return {
        ...state,
        targetFieldPath: action.payload.fieldPath,
        centerMode: state.centerMode === 'publish_blocked' 
          ? (state.selectedNodeType === 'rollback_candidate' ? 'rollback_ready_edit' : 'edit') 
          : state.centerMode,
      };

    case 'JUMP_TO_RULE':
      return {
        ...state,
        targetRuleId: action.payload.ruleId,
        centerMode: 'diff',
      };

    case 'CLEAR_DIRTY':
      return {
        ...state,
        dirty: false,
      };

    default:
      return state;
  }
}
