/**
 * P1.0-3: Shadow mock interceptor — DISABLED by default.
 *
 * This file previously registered response interceptors that would
 * intercept failed real-API requests and return mock data instead,
 * effectively masking real backend failures.
 *
 * This shadow mock behavior is now disabled unless VITE_USE_MOCK_API=true.
 * When mock mode is active, client.ts already sets up MockAdapter,
 * so this file is a no-op.
 *
 * If you need the old shadow-mock behavior for offline development,
 * set VITE_USE_MOCK_API=true in your .env file.
 */

// Only register shadow mock interceptors when mock mode is explicitly enabled
const USE_MOCK_API = import.meta.env.VITE_USE_MOCK_API === 'true';

if (USE_MOCK_API) {
  // When VITE_USE_MOCK_API=true, MockAdapter in client.ts handles everything.
  // No additional interceptors needed here.
  console.log('[mock.ts] MockAdapter is active in client.ts, shadow interceptors skipped.');
}
// When VITE_USE_MOCK_API=false (default), this file does nothing —
// all requests go directly to the real backend.
