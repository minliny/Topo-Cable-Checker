import { describe, it, expect } from 'vitest';
import { normalizeBaselineVersionRuleSetResponse } from '../api/adapters';

describe('normalizeBaselineVersionRuleSetResponse', () => {
  it('returns full rule_set without truncation', () => {
    const raw = {
      baseline_id: 'B003',
      version_id: 'v1.0',
      rule_set: {
        R1: { rule_type: 'template', template: 'threshold_check', params: { metric_type: 'count' } },
        R2: { rule_type: 'template', template: 'single_fact', params: { field: 'status' } },
        R3: { rule_type: 'template', template: 'group_consistency', params: { group_key: 'device_type' } },
      },
    };

    const result = normalizeBaselineVersionRuleSetResponse(raw);
    expect(result.baseline_id).toBe('B003');
    expect(result.version_id).toBe('v1.0');
    expect(Object.keys(result.rule_set)).toEqual(['R1', 'R2', 'R3']);
  });

  it('throws when rule_set is missing', () => {
    expect(() => normalizeBaselineVersionRuleSetResponse({ baseline_id: 'B003', version_id: 'v1.0' })).toThrow();
  });
});
