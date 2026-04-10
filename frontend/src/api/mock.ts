import apiClient from './client';

// Mock data
const mockBaselines = [
  { id: 'base-001', name: 'Baseline 1.0 (Prod)', status: 'published' },
  { id: 'base-002', name: 'Baseline 1.1 (Draft)', status: 'draft' },
  { id: 'base-003', name: 'Baseline 2.0 (Testing)', status: 'testing' },
];

const mockDiffData = {
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

// Enable mock adapter logic natively in axios
apiClient.interceptors.request.use((config) => {
  // Add a custom flag to bypass real network request if we mock
  (config as any)._isMock = true;
  return config;
});

apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    // If it's our mock intercept, we return the mock response instead of throwing
    const config = error.config;
    if (config && (config as any)._isMock) {
      console.log(`[Mock API] ${config.method?.toUpperCase()} ${config.url}`);
      
      // Mock baselines endpoint
      if (config.url?.includes('/baselines') && !config.url.includes('/diff')) {
        return Promise.resolve(mockBaselines);
      }
      
      // Mock diff endpoint
      if (config.url?.includes('/diff')) {
        return Promise.resolve(mockDiffData);
      }
      
      // Mock validate endpoint
      if (config.url?.includes('/rules/draft/validate')) {
        const data = JSON.parse(config.data || '{}');
        const isValid = data.params && Object.keys(data.params).length > 0;
        return Promise.resolve({
          validation_result: {
            valid: isValid,
            errors: isValid ? [] : ['Missing required parameters'],
            evidence: { checkedAt: new Date().toISOString(), source: 'mock-engine' }
          }
        });
      }
      
      // Mock publish endpoint
      if (config.url?.includes('/rules/publish')) {
        return Promise.resolve({
          version: `v2.${Math.floor(Math.random() * 100)}.0`,
          summary: 'Successfully published new rules to production'
        });
      }
    }
    
    return Promise.reject(error);
  }
);
