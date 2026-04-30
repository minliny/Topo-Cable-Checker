// models/scope.ts
// ScopeSelector model type

export type ScopeMethod = 'role_filter' | 'site_filter' | 'tag_filter' | 'explicit_list';

export interface ScopeSelector {
  scope_id: string;
  name: string;
  method: ScopeMethod;
  scope_fields: string[];
  included_groups: string[];
  excluded_groups: string[];
  description: string;
}
