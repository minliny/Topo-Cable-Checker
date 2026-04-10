import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { mockBaselines, mockDiffData } from './mockData'; // we'll extract mock data to a separate file

// Check environment variable for API source (dual-channel setup)
// e.g. VITE_USE_MOCK_API=true or VITE_USE_MOCK_API=false
const USE_MOCK_API = import.meta.env.VITE_USE_MOCK_API !== 'false'; // Default to true if not specified

// Create an Axios instance
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Setup mock adapter only if enabled
let mock: MockAdapter | null = null;

if (USE_MOCK_API) {
  console.log('🔌 Using MOCK API Channel');
  mock = new MockAdapter(apiClient, { delayResponse: 500 });
  
  // 1. Get baselines list (for mock UI)
  mock.onGet('/baselines').reply(200, mockBaselines);

  // 2. Validate rule draft
  mock.onPost('/rules/draft/validate').reply((config) => {
    const data = JSON.parse(config.data);
    const isValid = data.params && Object.keys(data.params).length > 0 && !JSON.stringify(data.params).includes('error');
    return [200, {
      validation_result: {
        valid: isValid,
        errors: isValid ? [] : [{ field_path: 'params', message: 'Missing or invalid parameters' }],
        evidence: { checkedAt: new Date().toISOString(), source: 'mock-engine' }
      }
    }];
  });

  // 3. Publish baseline
  mock.onPost(new RegExp('/rules/publish/.*')).reply((config) => {
    // Simulate publish blocked
    if (config.data && config.data.includes('block')) {
      return [400, {
        success: false,
        blocked_issues: [{ field_path: 'params', message: 'Contains forbidden keyword block' }]
      }];
    }
    return [200, {
      success: true,
      version_id: `v2.${Math.floor(Math.random() * 100)}.0`,
      version_label: `v2.${Math.floor(Math.random() * 100)}.0`,
      summary: 'Successfully published new rules to production.'
    }];
  });

  // 4. Get baseline diff
  mock.onGet(new RegExp('/baselines/.*/diff')).reply(200, mockDiffData);

  // 5. Rollback Create
  mock.onPost('/rules/rollback').reply(200, {
    baseline_id: 'base-001',
    source_version_id: 'v1.0',
    draft_data: { rule_type: 'threshold', params: '{"_comment": "Mock rollback draft"}' }
  });
} else {
  console.log('🚀 Using REAL API Channel');
}

// Request interceptor
apiClient.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error)
);

// Response interceptor
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    // Basic error normalization for UI layer to consume easily
    if (error.response && error.response.data) {
      return Promise.reject(error.response.data);
    }
    return Promise.reject(error);
  }
);

export default apiClient;
