import { pageReducer, PageAction } from '../store/pageReducer';
import { PageState, DraftData } from '../types/ui';
import { describe, it, expect } from 'vitest';

const initialState: PageState = {
  selectedBaselineId: 'b1',
  selectedVersionId: 'draft',
  selectedNodeType: 'working_draft',
  centerMode: 'edit',
  rightPanelMode: 'help',
  draftData: { rule_type: 'test', params: '{}' },
  dirty: true,
  validationResult: null,
  publishBlockedIssues: null,
  diffData: null,
};

describe('pageReducer - State Machine Transitions', () => {
  describe('Publish Flow', () => {
    it('should transition from edit -> publish_confirm -> publish_checking -> published -> history_detail', () => {
      let state = { ...initialState };

      // 1. Prepare Publish
      state = pageReducer(state, { type: 'PREPARE_PUBLISH' });
      expect(state.centerMode).toBe('publish_confirm');
      expect(state.rightPanelMode).toBe('publish_check');

      // 2. Request Publish
      state = pageReducer(state, { type: 'REQUEST_PUBLISH' });
      expect(state.centerMode).toBe('publish_checking');

      // 3. Publish Success
      state = pageReducer(state, { type: 'PUBLISH_SUCCESS', payload: { versionId: 'v1.0' } });
      expect(state.centerMode).toBe('published');
      expect(state.dirty).toBe(false);

      // 4. Trigger Post Publish Navigation
      state = pageReducer(state, { type: 'TRIGGER_POST_PUBLISH_NAVIGATION', payload: { versionId: 'v1.0' } });
      expect(state.centerMode).toBe('history_detail');
      expect(state.selectedVersionId).toBe('v1.0');
      expect(state.selectedNodeType).toBe('published_version');
    });

    it('should block invalid transitions in Publish Flow', () => {
      let state = { ...initialState, centerMode: 'history_detail' as const };
      
      // PREPARE_PUBLISH should fail if not in edit
      const newState = pageReducer(state, { type: 'PREPARE_PUBLISH' });
      expect(newState.centerMode).toBe('history_detail');
    });
  });

  describe('Restore Historical Draft Flow', () => {
    const historyState: PageState = {
      ...initialState,
      centerMode: 'history_detail',
      rightPanelMode: 'version_meta',
      selectedVersionId: 'v1.0',
      selectedNodeType: 'published_version',
      dirty: false,
    };

    it('should transition from history_detail -> restore_confirm -> restore_preparing -> restored_draft_edit', () => {
      let state = { ...historyState };

      state = pageReducer(state, { type: 'REQUEST_RESTORE_CONFIRM' });
      expect(state.centerMode).toBe('restore_confirm');

      state = pageReducer(state, { type: 'REQUEST_RESTORE' });
      expect(state.centerMode).toBe('restore_preparing');

      const mockDraft = { rule_type: 'rollback', params: '{}' };
      state = pageReducer(state, { 
        type: 'RESTORE_READY', 
        payload: { draftData: mockDraft, restoredFromVersionId: 'v1.0', restoredFromVersionLabel: 'v1.0' } 
      });
      
      expect(state.centerMode).toBe('restored_draft_edit');
      expect(state.selectedNodeType).toBe('restored_draft');
      expect(state.dirty).toBe(true);
      expect(state.draftData).toEqual(mockDraft);
    });
  });
});
