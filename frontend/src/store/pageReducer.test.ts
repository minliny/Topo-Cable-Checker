import { pageReducer, initialDraftState } from './pageReducer';
import { PageState } from '../types/ui';

describe('pageReducer PAIN-005', () => {
  it('clears validationResult when UPDATE_DRAFT sets dirty=true', () => {
    const initialState: PageState = {
      centerMode: 'edit',
      rightPanelMode: 'validation',
      validationResult: { valid: true, errors: [] },
      publishBlockedIssues: [],
      dirty: false,
      draftData: initialDraftState
    };

    const action: any = {
      type: 'UPDATE_DRAFT',
      payload: {
        draftData: { rule_set: { "r1": {} } },
        dirty: true
      }
    };

    const nextState = pageReducer(initialState, action);

    expect(nextState.validationResult).toBeNull();
    expect(nextState.publishBlockedIssues).toBeNull();
    expect(nextState.dirty).toBe(true);
  });
});
