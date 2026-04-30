// models/profile.ts
// ParameterProfile and ThresholdProfile model types

export type ParameterType = 'number' | 'string' | 'boolean' | 'enum';
export type SeverityLevel = 'critical' | 'warning' | 'info';
export type ComparisonOperator = '>=' | '<=' | '>' | '<' | '==' | '!=' | 'CONTAINS' | 'IN';

export interface ParameterDefinition {
  key: string;
  label: string;
  type: ParameterType;
  value: number | string | boolean;
  unit?: string;
  description?: string;
  options?: string[]; // for enum type
}

export interface ParameterProfile {
  profile_id: string;
  name: string;
  description: string;
  parameters: ParameterDefinition[];
}

export interface ThresholdDefinition {
  key: string;
  label: string;
  operator: ComparisonOperator;
  value: number | string;
  severity: SeverityLevel;
  description?: string;
}

export interface ThresholdProfile {
  profile_id: string;
  name: string;
  description: string;
  thresholds: ThresholdDefinition[];
}
