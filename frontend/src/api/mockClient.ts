// api/mockClient.ts
// Implements ApiClient using existing mocks
// Pages may continue to use existing mocks directly; this is for future migration

import { ApiClient } from './client';
import {
  GetBaselineListResponse,
  GetBaselineDetailResponse,
  UpdateBaselineRequest,
  GetBaselineProfileMapEntryResponse,
  GetBaselineVersionSnapshotResponse,
  GetRuleDefinitionsResponse,
  GetRuleSetListResponse,
  UpdateRuleOverrideRequest,
  GetVersionListResponse,
  GetVersionSnapshotResponse,
  GetVersionDiffResponse,
  CreateVersionRequest,
  PublishVersionRequest,
  GetDataSourceListResponse,
  GetScopeListResponse,
  GetRecognitionStatusResponse,
  StartRecognitionRequest,
  ConfirmRecognitionRequest,
  StartCheckRequest,
  GetRunHistoryResponse,
  GetRunDetailResponse,
  GetCheckResultBundleResponse,
  GetIssueDetailResponse,
  GetRecheckDiffResponse,
  GetParameterProfileListResponse,
  GetThresholdProfileListResponse,
  GetScopeSelectorListResponse,
} from './contracts';

// Import existing mocks
import {
  DATA_SOURCES,
  EXECUTION_SCOPES,
  INIT_RUNS,
  RECOGNITION_RESULTS,
} from '../mocks/execution.mock';
import {
  RECHECK_DIFF_SNAPSHOTS,
} from '../mocks/diff.mock';
import {
  VERSION_SNAPSHOTS,
  VERSION_DIFF_SNAPSHOTS,
  BASELINE_VERSION_SNAPSHOTS,
} from '../mocks/version.mock';
import {
  PARAMETER_PROFILES,
  THRESHOLD_PROFILES,
  SCOPE_SELECTORS,
  RULE_SETS,
  BASELINE_PROFILE_MAP,
  PARAMETER_PROFILE_MAP,
  THRESHOLD_PROFILE_MAP,
} from '../mocks/profiles.mock';
import { Baseline, RuleDefinition, RuleSet } from '../models/baseline';

// Stub baseline data from App.tsx
const STUB_BASELINES: Baseline[] = [
  {
    id: 'bl-001', name: '生产环境拓扑基线', version: '2.1.0',
    status: 'published', description: '覆盖 DC-A/DC-B 三层设备，共 24 条规则。',
    created_at: '2026-01-10', published_at: '2026-03-15',
    rule_count: 24, enabled_count: 22,
    identification_strategy: { method: 'device_id', id_fields: ['hostname', 'mgmt_ip'] },
    naming_template: '{site}-{role}-{seq:02d}',
  },
  {
    id: 'bl-002', name: 'DR 站点基线（草稿）', version: '0.3.0',
    status: 'draft', description: '灾备站点轻量化检查基线。',
    created_at: '2026-04-01', published_at: null,
    rule_count: 12, enabled_count: 10,
    identification_strategy: { method: 'device_id', id_fields: ['hostname'] },
    naming_template: '{site}-{role}-{seq:02d}',
  },
];

// Stub rule definitions
const STUB_RULES: RuleDefinition[] = [
  { id: 'R-001', name: 'Core Uplink Redundancy', severity: 'critical', category: 'redundancy', enabled: true, condition: 'device.role=="core" AND count(active_uplinks)>=param.min_uplinks', threshold: '2', parameter_profile_id: 'pp-001', threshold_profile_id: 'tp-001', scope_selector_id: 'sc-001', parameters: { min_uplinks: 2 } },
  { id: 'R-002', name: 'BGP Session Health', severity: 'critical', category: 'routing', enabled: true, condition: 'bgp.session.state=="Established" AND bgp.hold_timer<=param.bgp_hold_timer', threshold: '180s', parameter_profile_id: 'pp-001', threshold_profile_id: 'tp-001', scope_selector_id: 'sc-001', parameters: { bgp_hold_timer: 180 } },
  { id: 'R-003', name: 'OSPF Adjacency', severity: 'warning', category: 'routing', enabled: true, condition: 'ospf.neighbor.count>=param.min_ospf_neighbors', threshold: '1', parameter_profile_id: 'pp-001', threshold_profile_id: 'tp-001', scope_selector_id: 'sc-001', parameters: { min_ospf_neighbors: 1 } },
  { id: 'R-004', name: 'STP Root Bridge', severity: 'warning', category: 'layer2', enabled: true, condition: 'stp.root_bridge==device.id', threshold: '-', parameter_profile_id: 'pp-001', threshold_profile_id: 'tp-001', scope_selector_id: 'sc-001', parameters: {} },
];

// Convert CheckResultBundle to RunHistoryEntry format
function makeRunHistoryEntry(bundle: any) {
  return {
    run_id: bundle.id,
    baseline_id: bundle.baseline_id,
    baseline_version: bundle.baseline_version,
    scenario_id: bundle.scenario_id,
    scenario_name: bundle.scenario,
    status: 'completed' as const,
    started_at: new Date().toISOString(),
    completed_at: new Date().toISOString(),
    data_source_id: bundle.data_source || 'ds-prod-20260420',
    scope_id: bundle.execution_scope || 'scope-all',
    issue_total: bundle.issues.length,
    severity_summary: {
      critical: bundle.issues.filter((i: any) => i.severity === 'critical').length,
      warning: bundle.issues.filter((i: any) => i.severity === 'warning').length,
      info: bundle.issues.filter((i: any) => i.severity === 'info').length,
    },
  };
}

export const mockApiClient: ApiClient = {
  // ── Baseline ───────────────────────────────────────────────────────────
  async getBaselineList(): Promise<GetBaselineListResponse> {
    return { baselines: STUB_BASELINES };
  },

  async getBaselineDetail(baseline_id: string): Promise<GetBaselineDetailResponse> {
    const baseline = STUB_BASELINES.find(b => b.id === baseline_id) || STUB_BASELINES[0];
    const binding = BASELINE_PROFILE_MAP[baseline_id] || {
      parameter_profile_id: 'pp-001', threshold_profile_id: 'tp-001',
      scope_selector_id: 'sc-001', ruleset_ids: ['rs-001', 'rs-002', 'rs-003', 'rs-004'],
    };
    return {
      baseline,
      rulesets: RULE_SETS.filter(rs => binding.ruleset_ids.includes(rs.ruleset_id)),
      rules: STUB_RULES,
      parameter_profile: PARAMETER_PROFILE_MAP[binding.parameter_profile_id],
      threshold_profile: THRESHOLD_PROFILE_MAP[binding.threshold_profile_id],
      scope_selector: SCOPE_SELECTORS.find(s => s.scope_id === binding.scope_selector_id),
    };
  },

  async updateBaseline(baseline_id: string, request: UpdateBaselineRequest): Promise<void> {
    // No-op for mock
  },

  async getBaselineProfileMapEntry(baseline_id: string): Promise<{ parameter_profile_id: string; threshold_profile_id: string; scope_selector_id: string; ruleset_ids: string[] }> {
    return BASELINE_PROFILE_MAP[baseline_id] || { parameter_profile_id: 'pp-001', threshold_profile_id: 'tp-001', scope_selector_id: 'sc-001', ruleset_ids: ['rs-001', 'rs-002', 'rs-003', 'rs-004'] };
  },

  async getBaselineVersionSnapshot(baseline_id: string): Promise<{ baseline_id: string; current_version: string; previous_version: string | null; rule_added_count: number; rule_removed_count: number; parameter_changed_count: number; threshold_changed_count: number } | null> {
    return BASELINE_VERSION_SNAPSHOTS[baseline_id] ?? null;
  },

  // ── Rules / Rule Editor ─────────────────────────────────────────────────
  async getRuleDefinitions(): Promise<GetRuleDefinitionsResponse> {
    return { rules: STUB_RULES };
  },

  async getRuleSetList(): Promise<GetRuleSetListResponse> {
    return { rulesets: RULE_SETS };
  },

  async updateRuleOverride(request: UpdateRuleOverrideRequest): Promise<void> {
    // No-op for mock
  },

  // ── Version Management ──────────────────────────────────────────────────
  async getVersionList(baseline_id: string): Promise<GetVersionListResponse> {
    const versions = Object.values(VERSION_SNAPSHOTS).filter(v => v.baseline_id === baseline_id);
    return { versions };
  },

  async getVersionSnapshot(version_id: string): Promise<GetVersionSnapshotResponse> {
    const [baseline_id, version] = version_id.split('|');
    const key = `${baseline_id}|${version}`;
    const snapshot = VERSION_SNAPSHOTS[key];
    return { snapshot: snapshot || Object.values(VERSION_SNAPSHOTS)[0] };
  },

  async getVersionDiff(from_version: string, to_version: string): Promise<GetVersionDiffResponse> {
    const key = `bl-001|${from_version}|${to_version}`;
    const diff = VERSION_DIFF_SNAPSHOTS[key];
    return { diff: diff || Object.values(VERSION_DIFF_SNAPSHOTS)[0] };
  },

  async createVersion(baseline_id: string, request: CreateVersionRequest): Promise<{ version_id: string }> {
    return { version_id: `${baseline_id}|0.4.0` };
  },

  async publishVersion(request: PublishVersionRequest): Promise<void> {
    // No-op for mock
  },

  // ── Execution Config ────────────────────────────────────────────────────
  async getDataSourceList(): Promise<GetDataSourceListResponse> {
    return { data_sources: DATA_SOURCES };
  },

  async getScopeList(): Promise<GetScopeListResponse> {
    return { scopes: EXECUTION_SCOPES };
  },

  async getRecognitionStatus(): Promise<GetRecognitionStatusResponse> {
    return { status: 'not_started' };
  },

  async startRecognition(request: StartRecognitionRequest): Promise<{ recognition_id: string }> {
    return { recognition_id: `rec-${Date.now()}` };
  },

  async confirmRecognition(request: ConfirmRecognitionRequest): Promise<void> {
    // No-op for mock
  },

  async startCheck(request: StartCheckRequest): Promise<{ run_id: string }> {
    return { run_id: `run-${Date.now()}` };
  },

  // ── Run History ─────────────────────────────────────────────────────────
  async getRunHistory(): Promise<GetRunHistoryResponse> {
    const runs = INIT_RUNS.map(makeRunHistoryEntry);
    return { runs };
  },

  async getRunDetail(run_id: string): Promise<GetRunDetailResponse> {
    const bundle = INIT_RUNS.find(r => r.id === run_id) || INIT_RUNS[0];
    return { run: makeRunHistoryEntry(bundle), bundle };
  },

  // ── Analysis Workbench ──────────────────────────────────────────────────
  async getCheckResultBundle(bundle_id: string): Promise<GetCheckResultBundleResponse> {
    const bundle = INIT_RUNS.find(r => r.id === bundle_id) || INIT_RUNS[0];
    return { bundle };
  },

  async getIssueDetail(issue_id: string): Promise<GetIssueDetailResponse> {
    const issue = INIT_RUNS[0].issues.find(i => i.id === issue_id) || INIT_RUNS[0].issues[0];
    return { issue };
  },

  // ── Diff Compare ─────────────────────────────────────────────────────────
  async getRecheckDiff(base_run_id: string, target_run_id: string): Promise<GetRecheckDiffResponse> {
    const key = `${base_run_id}|${target_run_id}`;
    const diff = RECHECK_DIFF_SNAPSHOTS[key] || Object.values(RECHECK_DIFF_SNAPSHOTS)[0];
    return { diff };
  },

  // ── Profiles / Selectors ─────────────────────────────────────────────────
  async getParameterProfileList(): Promise<GetParameterProfileListResponse> {
    return { profiles: PARAMETER_PROFILES };
  },

  async getThresholdProfileList(): Promise<GetThresholdProfileListResponse> {
    return { profiles: THRESHOLD_PROFILES };
  },

  async getScopeSelectorList(): Promise<GetScopeSelectorListResponse> {
    return { selectors: SCOPE_SELECTORS };
  },
};

