import apiClient from './client';

export interface ValidateRequest {
  rule_type: string;
  params: Record<string, any>;
}

export interface ValidationResult {
  valid: boolean;
  errors?: string[];
  evidence?: any;
}

export interface ValidateResponse {
  validation_result: ValidationResult;
}

export interface PublishResponse {
  version: string;
  summary: string;
}

export interface ModifiedRule {
  rule_id: string;
  changed_fields: Record<string, any>;
  evidence?: any;
}

export interface DiffResponse {
  added_rules: any[];
  removed_rules: any[];
  modified_rules: ModifiedRule[];
}

export interface Baseline {
  id: string;
  name: string;
  status: string;
}

export const rulesApi = {
  // Get all baselines
  getBaselines: (): Promise<Baseline[]> => {
    return apiClient.get('/baselines');
  },

  // Validate rule draft
  validateDraft: (data: ValidateRequest): Promise<ValidateResponse> => {
    return apiClient.post('/rules/draft/validate', data);
  },

  // Publish baseline rules
  publishRules: (baselineId: string): Promise<PublishResponse> => {
    return apiClient.post(`/rules/publish/${baselineId}`);
  },

  // Get baseline diff
  getBaselineDiff: (baselineId: string): Promise<DiffResponse> => {
    return apiClient.get(`/baselines/${baselineId}/diff`);
  }
};
