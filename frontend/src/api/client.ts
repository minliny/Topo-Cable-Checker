/**
 * P1.0-3: API Client — Real API by default, mock only when explicitly enabled.
 *
 * Behavior:
 * - VITE_USE_MOCK_API is NOT set or is "false" → Real API (default)
 * - VITE_USE_MOCK_API=true → Mock API (explicit opt-in)
 *
 * To use mock: set VITE_USE_MOCK_API=true in .env
 * To use real API: set VITE_USE_MOCK_API=false or leave it unset
 */
import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { mockBaselines, mockDiffData } from './mockData'; // mock data definitions

// P1.0-3: Default to REAL API. Only use mock when explicitly opted in.
const USE_MOCK_API = import.meta.env.VITE_USE_MOCK_API === 'true';

// Create an Axios instance
const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Setup mock adapter only if explicitly enabled
let mock: MockAdapter | null = null;

if (USE_MOCK_API) {
  console.log('🔌 Using MOCK API Channel (VITE_USE_MOCK_API=true)');
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

  // A1-4: Save Draft
  mock.onPost('/rules/draft/save').reply(200, {
    success: true,
    saved_at: new Date().toISOString(),
    message: 'Draft saved successfully (mock)',
    new_revision: 2
  });

  // A1-4: Load Draft (returns no draft by default in mock)
  mock.onGet(new RegExp('/rules/draft/.*')).reply(200, {
    has_draft: false,
    draft_data: null,
    saved_at: null,
    base_revision: 1
  });

  // A1-4: Clear Draft
  mock.onDelete(new RegExp('/rules/draft/.*')).reply(200, {
    success: true,
    message: 'Draft cleared (mock)',
    new_revision: 2
  });
} else {
  console.log('🚀 Using REAL API Channel (default)');
}

// Request interceptor
apiClient.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error)
);

// Response interceptor — unwrap data for convenience
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
