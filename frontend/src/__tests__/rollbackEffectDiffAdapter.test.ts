import { describe, it, expect } from 'vitest';
import { normalizeRollbackEffectDiffResponse } from '../api/adapters';

describe('normalizeRollbackEffectDiffResponse', () => {
  it('returns rollback_effect_diff with correct added/removed semantics', () => {
    const raw = {
      baseline_id: 'B001',
      current_version_id: 'v2.0',
      target_version_id: 'v1.0',
      rollback_effect_diff: {
        source_version_id: 'v2.0',
        target_version_id: 'v1.0',
        diff_summary: { added: 0, removed: 1, modified: 0 },
        human_readable_summary: '1 rule(s) removed',
        rules: [
          {
            rule_id: 'R2',
            change_type: 'removed',
            changed_fields: [],
            field_changes: [],
            old_value: { rule_type: 'template' },
            new_value: null,
            human_summary: 'threshold rule removed',
          },
        ],
      },
    };

    const result = normalizeRollbackEffectDiffResponse(raw, 'v2.0', 'v1.0');
    expect(result.source_version_id).toBe('v2.0');
    expect(result.target_version_id).toBe('v1.0');
    expect(result.diff_summary.removed).toBe(1);
    expect(result.rules[0].change_type).toBe('removed');
    expect(result.rules[0].rule_id).toBe('R2');
  });
});

