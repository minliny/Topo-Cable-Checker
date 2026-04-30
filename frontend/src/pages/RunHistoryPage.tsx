// pages/RunHistoryPage.tsx
// P0 CONSTRAINT: RunHistory ONLY shows historical runs
// P0 CONSTRAINT: No execution, no baseline editing, no rule editing, no version management
// P0 CONSTRAINT: No UI diff computation on this page
// P0 CONSTRAINT: Drilldown to Workbench and DiffCompare via App state

import React, { useState, useMemo } from 'react';
import { CheckResultBundle, RunHistoryEntry, SeveritySummary } from '../models/execution';

export interface RunHistoryPageProps {
  runs: CheckResultBundle[];
  onNavigateToWorkbench: (runId: string) => void;
  onNavigateToDiff: (runId: string) => void;
}

type StatusFilter = 'all' | 'completed' | 'running' | 'failed';

const STATUS_LABELS: Record<string, string> = {
  pending: '等待中',
  running: '运行中',
  completed: '已完成',
  failed: '失败',
};

const STATUS_COLORS: Record<string, string> = {
  pending: 'status-pending',
  running: 'status-running',
  completed: 'status-completed',
  failed: 'status-failed',
};

function createRunHistoryEntry(run: CheckResultBundle): RunHistoryEntry {
  const critical = run.issues.filter(i => i.severity === 'critical').length;
  const warning = run.issues.filter(i => i.severity === 'warning').length;
  const info = run.issues.filter(i => i.severity === 'info').length;
  
  return {
    run_id: run.id,
    baseline_id: run.baseline_id,
    baseline_version: run.baseline_version,
    scenario_id: run.scenario_id,
    scenario_name: run.scenario,
    status: 'completed',
    started_at: run.time,
    completed_at: run.time,
    data_source_id: run.data_source ?? '',
    scope_id: run.execution_scope ?? '',
    issue_total: run.issues.length,
    severity_summary: { critical, warning, info },
    category_summary: undefined,
    check_result_bundle_id: run.id,
  };
}

export const RunHistoryPage: React.FC<RunHistoryPageProps> = ({
  runs,
  onNavigateToWorkbench,
  onNavigateToDiff,
}) => {
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedRun, setSelectedRun] = useState<string | null>(null);

  const historyEntries = useMemo(() => {
    return runs.map(createRunHistoryEntry);
  }, [runs]);

  const filteredEntries = useMemo(() => {
    return historyEntries.filter(entry => {
      if (statusFilter !== 'all' && entry.status !== statusFilter) return false;
      if (!searchQuery) return true;
      const q = searchQuery.toLowerCase();
      return (
        entry.run_id.toLowerCase().includes(q) ||
        entry.baseline_id.toLowerCase().includes(q) ||
        entry.scenario_name.toLowerCase().includes(q)
      );
    });
  }, [historyEntries, statusFilter, searchQuery]);

  const selectedEntry = selectedRun
    ? historyEntries.find(e => e.run_id === selectedRun)
    : null;

  const selectedBundle = selectedRun
    ? runs.find(r => r.id === selectedRun)
    : null;

  return (
    <div className="page run-history-page">
      <div className="page-header">
        <div>
          <div className="page-title">运行历史</div>
          <div className="page-sub">历次检查结果，点击查看详情</div>
        </div>
      </div>

      {/* Filter bar */}
      <div className="filter-bar">
        <input
          className="search-input"
          placeholder="搜索 run_id、baseline_id 或场景..."
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
        />
        <div className="status-filters">
          {(['all', 'completed', 'running', 'failed'] as StatusFilter[]).map(status => (
            <button
              key={status}
              className={`filter-btn ${statusFilter === status ? 'active' : ''}`}
              onClick={() => setStatusFilter(status)}
            >
              {status === 'all' ? '全部' : STATUS_LABELS[status]}
            </button>
          ))}
        </div>
        <span className="entry-count">{filteredEntries.length} 条记录</span>
      </div>

      <div className="history-content">
        {/* Run list */}
        <div className={`run-list ${selectedRun ? 'split' : 'wide'}`}>
          <table className="run-table">
            <thead>
              <tr>
                <th>运行 ID</th>
                <th>基线</th>
                <th>场景</th>
                <th>时间</th>
                <th>风险分数</th>
                <th>严重</th>
                <th>警告</th>
                <th>提示</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {filteredEntries.map(entry => {
                const run = runs.find(r => r.id === entry.run_id);
                return (
                  <tr
                    key={entry.run_id}
                    className={`run-row ${selectedRun === entry.run_id ? 'selected' : ''}`}
                    onClick={() => setSelectedRun(prev => prev === entry.run_id ? null : entry.run_id)}
                  >
                    <td className="col-runid">
                      <code>{entry.run_id.replace('run-', '')}</code>
                    </td>
                    <td className="col-baseline">
                      <span>{entry.baseline_id}</span>
                      <span className="version">{entry.baseline_version}</span>
                    </td>
                    <td className="col-scenario">{entry.scenario_name}</td>
                    <td className="col-time">{entry.completed_at}</td>
                    <td className={`col-score ${run?.score !== undefined && run.score < 50 ? 'score-low' : ''}`}>
                      {run?.score ?? '-'}
                    </td>
                    <td className="col-sev critical">{entry.severity_summary.critical}</td>
                    <td className="col-sev warning">{entry.severity_summary.warning}</td>
                    <td className="col-sev info">{entry.severity_summary.info}</td>
                    <td className="col-actions">
                      <button
                        className="action-btn workbench-btn"
                        onClick={e => {
                          e.stopPropagation();
                          onNavigateToWorkbench(entry.run_id);
                        }}
                      >
                        工作台
                      </button>
                      <button
                        className="action-btn diff-btn"
                        onClick={e => {
                          e.stopPropagation();
                          onNavigateToDiff(entry.run_id);
                        }}
                      >
                        对比
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Detail panel */}
        {selectedRun && (
          <div className="detail-panel">
            <div className="detail-header">
              <div className="detail-title-row">
                <span className={`status-tag ${STATUS_COLORS[selectedEntry?.status ?? 'completed']}`}>
                  {STATUS_LABELS[selectedEntry?.status ?? 'completed']}
                </span>
                <code className="run-id">{selectedEntry?.run_id}</code>
              </div>
              <div className="detail-subtitle">运行详情</div>
              <button className="close-btn" onClick={() => setSelectedRun(null)}>×</button>
            </div>

            <div className="detail-content">
              {/* Basic info */}
              <div className="info-section">
                <h4>基本信息</h4>
                <dl className="kv-grid">
                  <dt>运行 ID</dt><dd><code>{selectedEntry?.run_id}</code></dd>
                  <dt>基线 ID</dt><dd><code>{selectedEntry?.baseline_id}</code></dd>
                  <dt>基线版本</dt><dd>{selectedEntry?.baseline_version}</dd>
                  <dt>场景</dt><dd>{selectedEntry?.scenario_name}</dd>
                  <dt>数据源</dt><dd>{selectedEntry?.data_source_id || '-'}</dd>
                  <dt>执行范围</dt><dd>{selectedEntry?.scope_id || '-'}</dd>
                  <dt>开始时间</dt><dd>{selectedEntry?.started_at}</dd>
                  <dt>完成时间</dt><dd>{selectedEntry?.completed_at}</dd>
                </dl>
              </div>

              {/* Score */}
              {selectedBundle && (
                <div className="score-section">
                  <div className="score-display">
                    <span className={`score-value ${selectedBundle.score >= 80 ? 'score-good' : selectedBundle.score >= 50 ? 'score-mid' : 'score-bad'}`}>
                      {selectedBundle.score}
                    </span>
                    <span className="score-label">风险分数</span>
                  </div>
                </div>
              )}

              {/* Issue summary */}
              <div className="issue-summary-section">
                <h4>问题统计</h4>
                <div className="sev-summary">
                  <div className="sev-item critical">
                    <span className="sev-count">{selectedEntry?.severity_summary.critical}</span>
                    <span className="sev-label">严重</span>
                  </div>
                  <div className="sev-item warning">
                    <span className="sev-count">{selectedEntry?.severity_summary.warning}</span>
                    <span className="sev-label">警告</span>
                  </div>
                  <div className="sev-item info">
                    <span className="sev-count">{selectedEntry?.severity_summary.info}</span>
                    <span className="sev-label">提示</span>
                  </div>
                </div>
                <div className="total-count">
                  总计: {selectedEntry?.issue_total} 个问题
                </div>
              </div>

              {/* Actions */}
              <div className="action-section">
                <button
                  className="primary-btn"
                  onClick={() => onNavigateToWorkbench(selectedRun)}
                >
                  ◈ 查看分析工作台
                </button>
                <button
                  className="secondary-btn"
                  onClick={() => onNavigateToDiff(selectedRun)}
                >
                  ⊕ 用于差异对比
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default RunHistoryPage;