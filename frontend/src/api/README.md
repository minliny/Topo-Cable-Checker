# API Contract Preparation

## Overview

This layer defines the API contract for the TopoChecker frontend without connecting to a real backend. The goal is to:

- Define clear interface contracts for all API interactions
- Provide type-safe mock implementations using existing mock data
- Prepare for future migration to a real backend
- Support switching between mock and real client via a provider pattern

## File Structure

| File | Purpose |
|------|---------|
| `contracts.ts` | TypeScript interface definitions for API requests and responses |
| `client.ts` | `ApiClient` interface definition |
| `mockClient.ts` | Mock implementation using local data |
| `realClient.ts` | Real implementation using native fetch |
| `config.ts` | API mode and baseUrl configuration |
| `provider.ts` | API client factory (default: mock) |
| `services.ts` | Page-level service methods |
| `index.ts` | Centralized exports |
| `README.md` | This document |

## Architecture

```
Frontend Pages
      ↓
services.ts (Page-level service methods)
      ↓
provider.ts (API client factory)
      ↓
config.ts (mode: "mock" | "real", baseUrl)
      ↓
mockClient.ts (default) ←→ realClient.ts (uses native fetch)
      ↓                        ↓
mock data files           [Future: HTTP to backend]
```

## Client Switching Strategy

### Current Default

- **Default mode**: `mock` (set in `config.ts`)
- **Real mode**: Requires explicit configuration via `setApiConfig()`

### Enabling Real Mode

To switch from mock to real backend for local development:

```typescript
import { setApiConfig } from './api';
setApiConfig({ mode: 'real', baseUrl: 'http://localhost:8000' });
```

### SECURITY: Local Only

**Real mode is restricted to localhost/127.0.0.1 only.**

- `setApiConfig()` validates that `baseUrl` must be `localhost` or `127.0.0.1`
- Production URLs (e.g., `https://api.example.com`) are blocked
- If `baseUrl` is not a local URL, `provider.ts` will still return `mockClient`
- Call `resetApiConfig()` to revert to mock mode

### Production Integration

**Production deployment requires a separate integration phase.**

This codebase does NOT contain:
- Production API URLs
- Environment-specific configuration
- Backend deployment credentials

To integrate with a real production backend:
1. This is a separate deployment/integration phase
2. The backend team must provide production API endpoints
3. Configuration management should be handled by deployment infrastructure (not in this codebase)

## Transport Implementation

### realClient.ts

Uses native `fetch` for HTTP transport:

- `requestJson<T>()` - Generic JSON request helper
- Handles Content-Type headers automatically
- Throws `RealApiTransportError` on HTTP errors
- All methods check `isRealMode()` before making requests
- `baseUrl` must be configured before real mode is enabled

### NOT Using

- ❌ `axios`
- ❌ `react-query`
- ❌ `swr`
- ❌ Any other HTTP library

## Config API

| Function | Purpose |
|----------|---------|
| `getApiConfig()` | Get current API configuration |
| `setApiConfig(config)` | Set API configuration (validates baseUrl for real mode) |
| `isMockMode()` | Returns true if current mode is mock |
| `isRealMode()` | Returns true if current mode is real |
| `getBaseUrl()` | Get current baseUrl (undefined if not set) |
| `isLocalBaseUrl()` | Returns true if baseUrl is localhost/127.0.0.1 |
| `resetApiConfig()` | Reset to default mock configuration |
| `DEFAULT_API_MODE` | Export constant for 'mock' |

## Security Features

1. **Default is Mock**: No real HTTP calls can be made accidentally
2. **Localhost Validation**: `setApiConfig` throws if baseUrl is not localhost/127.0.0.1
3. **Provider Fallback**: `provider.ts` returns mockClient if baseUrl is not local
4. **Reset Capability**: `resetApiConfig()` reverts to mock mode immediately

## Rules & Constraints

### Current Phase

- **Default is MOCK**: No real backend is connected
- **Real mode requires config**: Must call `setApiConfig()` to enable
- **No production URLs**: Production HTTP/HTTPS URLs are blocked in config validation
- **No forbidden libraries**: No axios, react-query, swr

### Constraints

- **NO FORBIDDEN LIBS**: No `axios`/`react-query`/`swr` in any file
- **NO PRODUCTION URLs**: No hardcoded production HTTP/HTTPS URLs
- **NO ROUTER/STATE LIBS**: No React Router or state management dependencies
- **NO BUSINESS LOGIC IN UI**: UI must not compute diffs (use pre-computed snapshots only)
- **NO `any` TYPES**: All types must be explicitly defined

## Existing Mocks Used

| File | Data |
|------|------|
| `mocks/execution.mock.ts` | Data sources, scopes, recognition, runs |
| `mocks/diff.mock.ts` | Pre-computed diff snapshots |
| `mocks/version.mock.ts` | Version snapshots and diffs |
| `mocks/profiles.mock.ts` | Parameter profiles, threshold profiles, scopes, rule sets |

## Service Layer

`services.ts` provides page-level service methods that wrap the API client. Pages should use these services instead of calling the client directly:

```typescript
// Instead of calling apiClient directly:
const result = await apiClient.getVersionList(baselineId);

// Use the service:
const versions = await getVersionList(baselineId);
```

Services are currently implemented as async wrappers around the client. This prepares for both:
- Synchronous mock returns (current)
- Asynchronous real API calls (future)

## Migration Guidance

### For New Features

- Use services from `services.ts`
- Import types from `contracts.ts`
- Do NOT import from `mocks/*` directly in pages

### For Existing Pages

- Prefer using services over direct mock imports
- Services maintain the same return types as direct mock access
- Switching from mock to real is transparent to pages
