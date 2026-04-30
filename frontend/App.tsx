// App.tsx
// Minimal navigation shell for FRONTEND_COMPONENTIZATION_PHASE_1
// Uses local state only — no router library required
// Pages: execution | diff | version (+ future: baseline | rules | history | workbench)

import React, { useState } from 'react';
import { WorkbenchDrilldownContext } from './src/models/diff';
import { CheckResultBundle } from './src/models/execution';
import { Baseline } from './src/models/baseline';
import { ExecutionConfigPage }   from './src/pages/ExecutionConfigPage';
import { DiffComparePage }       from './src/pages/DiffComparePage';
import { VersionManagementPage, VersionEntry } from './src/pages/VersionManagementPage';
import { AnalysisWorkbenchPage } from './src/pages/AnalysisWorkbenchPage';
import { RunHistoryPage }        from './src/pages/RunHistoryPage';
import { BaselineDetailPage }    from './src/pages/BaselineDetailPage';
import { RuleEditorPage }        from './src/pages/RuleEditorPage';
import { INIT_RUNS }             from './src/mocks/execution.mock';
import './src/styles/design-tokens.css';
import './src/styles/app.css';

// ── Stub data for pages not yet backed by real API ─────────────────────────
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

const STUB_VERSIONS: VersionEntry[] = [
  { version: '2.1.0', status: 'published',  rule_count: 24, published_at: '2026-03-15' },
  { version: '2.0.0', status: 'deprecated', rule_count: 22, published_at: '2026-01-20' },
  { version: '1.5.0', status: 'deprecated', rule_count: 18, published_at: '2025-11-10' },
  { version: '1.0.0', status: 'deprecated', rule_count: 12, published_at: '2025-08-01' },
];

// Non-null assertion safe: INIT_RUNS is a non-empty constant defined in mock
const BASE_RUN: CheckResultBundle = INIT_RUNS[0] as CheckResultBundle;
const FALLBACK_BASELINE: Baseline = STUB_BASELINES[0] as Baseline;

type PageKey = 'execution' | 'diff' | 'version' | 'workbench' | 'history' | 'baseline' | 'rule-editor';

const NAV_ITEMS: Array<{ key: PageKey; label: string }> = [
  { key: 'execution',   label: 'Execution' },
  { key: 'diff',        label: 'Diff' },
  { key: 'version',     label: 'Versions' },
  { key: 'history',     label: 'RunHistory' },
  { key: 'baseline',    label: 'BaselineDetail' },
  { key: 'rule-editor', label: 'RuleEditor' },
  { key: 'workbench',   label: 'Workbench' },
];

export const App: React.FC = () => {
  const [activePage, setActivePage] = useState<PageKey>('execution');
  const [runs, setRuns] = useState<CheckResultBundle[]>(INIT_RUNS);
  const [drilldown, setDrilldown] = useState<WorkbenchDrilldownContext | null>(null);

  function handleRunComplete(config: {
    baseline_id: string;
    baseline_version: string;
    scenario_id: string;
    dataset_id: string;
    scope_id: string;
  }): void {
    const newRun: CheckResultBundle = {
      ...BASE_RUN,
      id: `run-${Date.now()}`,
      time: '刚刚',
      baseline_id: config.baseline_id,
      baseline_version: config.baseline_version,
      scenario_id: config.scenario_id,
      scenario: config.scenario_id,
      data_source: config.dataset_id,
      execution_scope: config.scope_id,
    };
    setRuns(prev => [newRun, ...prev]);
    setActivePage('diff');
  }

  function handleDrilldownToWorkbench(ctx: WorkbenchDrilldownContext): void {
    setDrilldown(ctx);
    setActivePage('workbench');
  }

  function renderPage(): React.ReactElement {
    switch (activePage) {
      case 'execution':
        return (
          <ExecutionConfigPage
            baselines={STUB_BASELINES}
            onRunComplete={handleRunComplete}
          />
        );
      case 'diff':
        return (
          <DiffComparePage
            runs={runs}
            onDrilldownToWorkbench={handleDrilldownToWorkbench}
          />
        );
      case 'version':
        return (
          <VersionManagementPage
            baseline={FALLBACK_BASELINE}
            versions={STUB_VERSIONS}
          />
        );
      case 'workbench': {
        const targetRun = drilldown?.run_id
          ? runs.find(r => r.id === drilldown.run_id) ?? BASE_RUN
          : BASE_RUN;
        return (
          <AnalysisWorkbenchPage
            run={targetRun}
            drilldown={drilldown}
            onNavigate={() => {
              setActivePage('diff');
            }}
          />
        );
      }
      case 'history':
        return (
          <RunHistoryPage
            runs={runs}
            onNavigateToWorkbench={(runId) => {
              setDrilldown(null);
              setActivePage('workbench');
            }}
            onNavigateToDiff={(runId) => {
              setActivePage('diff');
            }}
          />
        );
      case 'baseline':
        return (
          <BaselineDetailPage
            baseline={FALLBACK_BASELINE}
          />
        );
      case 'rule-editor':
        return (
          <RuleEditorPage
            baseline={FALLBACK_BASELINE}
          />
        );
      default:
        return <div className="page"><p>未知页面</p></div>;
    }
  }

  return (
    <div className="app-shell">
      <nav className="top-nav">
        <span className="logo">TopoChecker</span>
        <span className="divider" />
        <span className="nav-subtitle">前端组件化 Phase 1</span>
        <div className="nav-items">
          {NAV_ITEMS.map(item => (
            <button
              key={item.key}
              className={`nav-btn ${activePage === item.key ? 'active' : ''}`}
              onClick={() => setActivePage(item.key)}
            >
              {item.label}
            </button>
          ))}
        </div>
      </nav>
      <main className="app-content">
        {renderPage()}
      </main>
    </div>
  );
};

export default App;
