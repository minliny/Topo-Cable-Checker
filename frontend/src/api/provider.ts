// api/provider.ts
// API Client Provider
// Controls which ApiClient implementation is used (mock or real)
// Default is mock - real client requires explicit configuration via config.ts
//
// SECURITY: Real client is only returned if:
//   1. mode is 'real' AND
//   2. baseUrl is a valid local URL (localhost/127.0.0.1)
// This prevents accidental real API calls in production

import { ApiClient } from './client';
import { mockApiClient } from './mockClient';
import { realApiClient } from './realClient';
import { isMockMode, isLocalBaseUrl } from './config';

let apiClientInstance: ApiClient | null = null;

function createApiClient(): ApiClient {
  if (isMockMode()) {
    return mockApiClient;
  }
  if (!isLocalBaseUrl()) {
    return mockApiClient;
  }
  return realApiClient;
}

export function getApiClient(): ApiClient {
  if (!apiClientInstance) {
    apiClientInstance = createApiClient();
  }
  return apiClientInstance;
}

export function resetApiClient(): void {
  apiClientInstance = null;
}

export const apiClient = getApiClient();
