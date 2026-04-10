import { PageState, CenterMode, RightPanelMode, DraftData, BaselineNodeType } from './types/ui';

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
  | { type: 'GO_TO_HISTORY', payload: { versionId: string } }
  | { type: 'REQUEST_DIFF' }
  | { type: 'DIFF_SUCCESS', payload: { diffData: any } }
  | { type: 'DIFF_FAILED' }
  | { type: 'REQUEST_ROLLBACK_CONFIRM' }
  | { type: 'CANCEL_ROLLBACK' }
  | { type: 'REQUEST_ROLLBACK' }
  | { type: 'ROLLBACK_READY', payload: { draftData: DraftData; sourceVersionId: string; sourceVersionLabel: string } }
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
      };

    case 'UPDATE_DRAFT':
      return {
        ...state,
        draftData: action.payload.draftData,
        dirty: action.payload.dirty,
        targetFieldPath: undefined,
      };

    case 'REQUEST_VALIDATION':
      return { ...state }; // Side effect handles loading

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
      return {
        ...state,
        centerMode: 'publish_confirm',
        rightPanelMode: 'publish_check',
      };

    case 'CANCEL_PUBLISH':
      return {
        ...state,
        centerMode: 'edit',
        rightPanelMode: 'validation',
      };

    case 'REQUEST_PUBLISH':
      return {
        ...state,
        centerMode: 'publish_checking',
      };

    case 'PUBLISH_BLOCKED':
      return {
        ...state,
        centerMode: 'publish_blocked',
        publishBlockedIssues: action.payload.issues,
      };

    case 'PUBLISH_SUCCESS':
      // The requirement states "dirty clears after publish success + new version node placed"
      return {
        ...state,
        centerMode: 'published',
        dirty: false,
      };

    case 'GO_TO_HISTORY':
      return {
        ...state,
        selectedVersionId: action.payload.versionId,
        centerMode: 'history_detail',
        rightPanelMode: 'version_meta',
        validationResult: null,
        diffData: null,
      };

    case 'REQUEST_DIFF':
      return { ...state };

    case 'DIFF_SUCCESS':
      return {
        ...state,
        diffData: action.payload.diffData,
        centerMode: 'diff',
        rightPanelMode: 'diff_summary',
      };

    case 'DIFF_FAILED':
      return { ...state };

    case 'REQUEST_ROLLBACK_CONFIRM':
      return {
        ...state,
        centerMode: 'rollback_confirm',
      };

    case 'CANCEL_ROLLBACK':
      return {
        ...state,
        centerMode: 'history_detail',
      };

    case 'REQUEST_ROLLBACK':
      return {
        ...state,
        centerMode: 'rollback_preparing',
      };

    case 'ROLLBACK_READY':
      return {
        ...state,
        centerMode: 'rollback_ready_edit',
        rightPanelMode: 'help',
        draftData: action.payload.draftData,
        dirty: true,
        selectedNodeType: 'rollback_candidate',
      };

    case 'JUMP_TO_FIELD':
      return {
        ...state,
        targetFieldPath: action.payload.fieldPath,
        centerMode: state.centerMode === 'publish_blocked' ? 'edit' : state.centerMode,
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
