import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';

// Create an Axios instance
const apiClient = axios.create({
  baseURL: '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Setup mock adapter
const mock = new MockAdapter(apiClient, { delayResponse: 500 });

// Mock data
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

// 1. Get baselines list (for mock UI)
mock.onGet('/baselines').reply(200, mockBaselines);

// 2. Validate rule draft
mock.onPost('/rules/draft/validate').reply((config) => {
  const data = JSON.parse(config.data);
  const isValid = data.params && Object.keys(data.params).length > 0;
  return [200, {
    validation_result: {
      valid: isValid,
      errors: isValid ? undefined : ['Missing required parameters'],
      evidence: { checkedAt: new Date().toISOString(), source: 'mock-engine' }
    }
  }];
});

// 3. Publish baseline
mock.onPost(new RegExp('/rules/publish/.*')).reply(200, {
  version: `v2.${Math.floor(Math.random() * 100)}.0`,
  summary: 'Successfully published new rules to production.'
});

// 4. Get baseline diff
mock.onGet(new RegExp('/baselines/.*/diff')).reply(200, mockDiffData);


// Request interceptor
apiClient.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error)
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => Promise.reject(error)
);

export default apiClient;
