export const mockBaselines = [
  { id: 'base-001', name: 'Baseline 1.0 (Prod)', status: 'published' },
  { id: 'base-002', name: 'Baseline 1.1 (Draft)', status: 'draft' },
  { id: 'base-003', name: 'Baseline 2.0 (Testing)', status: 'testing' },
];

export const mockDiffData = {
  added_rules: [
    { id: 'rule-new-1', name: 'New Validation Rule', type: 'threshold' }
  ],
  removed_rules: [
    { id: 'rule-old-1', name: 'Deprecated Check', type: 'pattern' }
  ],
  modified_rules: [
    {
      rule_id: 'rule-mod-1',
      changed_fields: {
        threshold: { old: 10, new: 15 },
        severity: { old: 'warning', new: 'error' }
      },
      evidence: {
        reason: 'Updated policy for stricter security',
        author: 'admin',
        timestamp: '2026-04-10T10:00:00Z'
      }
    }
  ]
};
