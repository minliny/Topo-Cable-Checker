// models/diff.ts
// RecheckDiffSnapshot, RecheckIssueDiffItem, WorkbenchDrilldownContext

import { SeverityLevel } from './profile';

export type RecheckDiffType =
  | 'new'
  | 'resolved'
  | 'remaining'
  | 'severity_changed'
  | 'regression';

export interface RecheckIssueDiffItem {
  issue_id: string;
  diff_type: RecheckDiffType;
  severity_before: SeverityLevel | null;
  severity_after: SeverityLevel | null;
  summary: string;
}

export interface RecheckDiffSummary {
  trend: 'degraded' | 'improved' | 'stable';
  total_before: number;
  total_after: number;
  delta: number;
  severity_diff: Partial<Record<SeverityLevel, number>>;
}

export interface RecheckDiffSnapshot {
  diff_id: string;
  base_run_id: string;
  target_run_id: string;
  summary: RecheckDiffSummary;
  issue_changes: RecheckIssueDiffItem[];
}

// ── Workbench Drilldown Context ────────────────────────────────────────────
// Passed from DiffComparePage → AnalysisWorkbenchPage via App state
export interface WorkbenchDrilldownContext {
  source: 'recheck_diff';
  diff_id: string;
  from_run_id: string;
  to_run_id: string;
  run_id: string;
  issue_id: string;
  diff_type: RecheckDiffType;
  issue_diff_item: RecheckIssueDiffItem;
}
