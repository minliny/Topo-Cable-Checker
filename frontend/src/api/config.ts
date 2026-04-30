// api/config.ts
// API Configuration
// Controls which API client mode is used (mock or real)
// Default is mock - real client requires explicit configuration
//
// SECURITY: baseUrl validation ensures only localhost/127.0.0.1 is allowed for real mode
// Production URLs are blocked to prevent accidental real API calls

export type ApiMode = 'mock' | 'real';

export interface ApiConfig {
  mode: ApiMode;
  baseUrl?: string;
}

export const DEFAULT_API_MODE: ApiMode = 'mock';

const DEFAULT_CONFIG: ApiConfig = {
  mode: DEFAULT_API_MODE,
  baseUrl: undefined,
};

let currentConfig: ApiConfig = { ...DEFAULT_CONFIG };

export function getApiConfig(): ApiConfig {
  return { ...currentConfig };
}

export function setApiConfig(config: Partial<ApiConfig>): void {
  if (config.mode === 'real' && config.baseUrl !== undefined) {
    validateBaseUrl(config.baseUrl);
  }
  currentConfig = { ...currentConfig, ...config };
}

export function isRealMode(): boolean {
  return currentConfig.mode === 'real';
}

export function isMockMode(): boolean {
  return currentConfig.mode === 'mock';
}

export function getBaseUrl(): string | undefined {
  return currentConfig.baseUrl;
}

export function resetApiConfig(): void {
  currentConfig = { ...DEFAULT_CONFIG };
}

function validateBaseUrl(url: string): void {
  const trimmed = url.trim();
  const isLocalhost = /^https?:\/\/(localhost|127\.0\.0\.1)(\:\d+)?(\/.*)?$/i.test(trimmed);
  if (!isLocalhost) {
    throw new Error(
      `baseUrl "${trimmed}" is not allowed. Real mode only supports localhost or 127.0.0.1. ` +
      `Production URLs are blocked to prevent accidental real API calls. ` +
      `Use setApiConfig({ mode: 'mock' }) to reset.`
    );
  }
}

export function isLocalBaseUrl(): boolean {
  const url = currentConfig.baseUrl;
  if (!url) return false;
  return /^https?:\/\/(localhost|127\.0\.0\.1)(\:\d+)?(\/.*)?$/i.test(url.trim());
}
