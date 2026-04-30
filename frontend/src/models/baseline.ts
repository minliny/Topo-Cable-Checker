// models/baseline.ts
// Baseline, RuleSet, RuleDefinition, RuleOverride model types

import { SeverityLevel } from './profile';

export type BaselineStatus = 'published' | 'draft' | 'deprecated';

export interface IdentificationStrategy {
  method: string;
  id_fields: string[];
}

export interface RuleOverride {
  [param_key: string]: number | string | boolean;
}

export interface RuleDefinition {
  id: string;
  name: string;
  enabled: boolean;
  condition: string;       // read-only DSL string
  threshold: string;
  category: string;
  severity: SeverityLevel;
  parameter_profile_id: string;
  threshold_profile_id: string;
  scope_selector_id: string;
  parameters: Record<string, string | number | boolean>; // profile defaults
  rule_overrides?: RuleOverride;
}

export interface RuleSet {
  ruleset_id: string;
  name: string;
  description: string;
  priority: number;
  rule_ids: string[];
}

export interface Baseline {
  id: string;
  name: string;
  version: string;
  status: BaselineStatus;
  description: string;
  created_at: string;
  published_at: string | null;
  rule_count: number;
  enabled_count: number;
  identification_strategy: IdentificationStrategy;
  naming_template: string;
  parameter_profile_id?: string;
  threshold_profile_id?: string;
  scope_selector_id?: string;
  ruleset_ids?: string[];
  // legacy flat params kept for backward compat with prototype
  parameters?: Record<string, string>;
}
