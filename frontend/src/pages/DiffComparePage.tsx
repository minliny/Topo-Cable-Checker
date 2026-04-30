// pages/DiffComparePage.tsx
// P0 CONSTRAINT: diff MUST come from RecheckDiffSnapshot, never UI-computed
// P0 CONSTRAINT: forbidden: set-based diff, Run-A diff_summary reuse
// P0 CONSTRAINT: diff_summary comes from snapshot matching current A→B pair

import React, { useState, useEffect } from 'react';
import { RecheckDiffSnapshot, RecheckIssueDiffItem, RecheckDiffType, WorkbenchDrilldownContext } from '../models/diff';
import { CheckResultBundle } from '../models/execution';
import { getRecheckDiff } from '../api';

const DIFF_TYPE_LABEL: Record<RecheckDiffType, string> = {
  new:              '＋ 新增',
  resolved:         '− 消除',
  remaining:        '→ 持续',
  severity_changed: '~ 级别变化',
  regression:       '↩ 回归',
};

const TREND_LABEL = { degraded: '↑ 恶化', improved: '↓ 改善', stable: '→ 稳定' };

export interface DiffComparePageProps {
  runs: CheckResultBundle[];
  initialRunId?: string;
  onDrilldownToWorkbench: (ctx: WorkbenchDrilldownContext) => void;
}

export const DiffComparePage: React.FC<DiffComparePageProps> = ({
  runs,
  initialRunId,
  onDrilldownToWorkbench,
}) => {
  const [runA, setRunA] = useState(initialRunId ?? runs[0]?.id ?? '');
  const [runB, setRunB] = useState(runs[1]?.id ?? '');
  const [selChange, setSelChange] = useState<RecheckIssueDiffItem | null>(null);
  const [snapshot, setSnapshot] = useState<RecheckDiffSnapshot | null>(null);

  // Clear selection when pair changes
  useEffect(() => { setSelChange(null); }, [runA, runB]);

  // P0: look up snapshot by A→B pair via service; NEVER compute diff in UI
  useEffect(() => {
    if (runA && runB) {
      getRecheckDiff(runA, runB).then(setSnapshot);
    } else {
      setSnapshot(null);
    }
  }, [runA, runB]);

  const ds = snapshot?.summary ?? null;
  const changes = snapshot?.issue_changes ?? [];

  // issue title index for display only — NOT used for diff computation
  const issueIndex: Record<string, CheckResultBundle['issues'][number]> = {};
  runs.forEach(r => r.issues.forEach(i => { issueIndex[i.id] = i; }));

  function handleRowClick(c: RecheckIssueDiffItem) {
    setSelChange(prev => (prev?.issue_id === c.issue_id ? null : c));
  }

  function handleDrilldown(c: RecheckIssueDiffItem) {
    if (!snapshot) return;
    onDrilldownToWorkbench({
      source: 'recheck_diff',
      diff_id: snapshot.diff_id,
      from_run_id: snapshot.base_run_id,
      to_run_id: snapshot.target_run_id,
      run_id: snapshot.target_run_id,
      issue_id: c.issue_id,
      diff_type: c.diff_type,
      issue_diff_item: c,
    });
  }

  return (
    <div className="page diff-compare-page">
      <div className="page-header">
        <div>
          <div className="page-title">差异对比</div>
          <div className="page-sub">数据来源：RecheckDiffSnapshot · 禁止 UI 计算集合差</div>
        </div>
      </div>

      {/* Run selector */}
      <div className="diff-run-selector">
        <div>
          <label>基准 Run（A）</label>
          <select value={runA} onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setRunA(e.target.value)}>
            {runs.map(r => <option key={r.id} value={r.id}>{r.id.replace('run-', '')} — {r.time}</option>)}
          </select>
        </div>
        <span className="arrow">→</span>
        <div>
          <label>对比 Run（B）</label>
          <select value={runB} onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setRunB(e.target.value)}>
            {runs.map(r => <option key={r.id} value={r.id}>{r.id.replace('run-', '')} — {r.time}</option>)}
          </select>
        </div>
      </div>

      {/* No snapshot fallback — do NOT compute diff */}
      {!snapshot ? (
        <div className="empty-state">
          <p className="empty-title">当前 Run 配对暂无差异快照</p>
          <code>{runA} → {runB}</code>
          <p>如需对比，请确保已为此配对生成 RecheckDiffSnapshot。</p>
        </div>
      ) : (
        <div className="diff-content-layout">
          {/* Left: summary + table */}
          <div className="diff-main">
            <div className="diff-meta">
              <code>diff_id: {snapshot.diff_id}</code>
              <span>{snapshot.base_run_id.replace('run-','')} → {snapshot.target_run_id.replace('run-','')}</span>
            </div>

            {ds && (
              <>
                <div className={`trend-badge trend-${ds.trend}`}>{TREND_LABEL[ds.trend]}</div>
                <div className="diff-stat-grid">
                  {[
                    ['Run A 问题数', ds.total_before],
                    ['Run B 问题数', ds.total_after],
                    ['变化量',       ds.delta >= 0 ? `+${ds.delta}` : ds.delta],
                  ].map(([label, val]) => (
                    <div key={String(label)} className="diff-stat">
                      <span className="stat-val">{val}</span>
                      <span className="stat-label">{label}</span>
                    </div>
                  ))}
                  <div className="diff-stat">
                    {Object.entries(ds.severity_diff ?? {}).map(([s, v]) => (
                      <div key={s} className="severity-delta">
                        <span className="sev-name">{s}</span>
                        <span className={`sev-val ${v > 0 ? 'up' : v < 0 ? 'down' : 'eq'}`}>
                          {v > 0 ? '+' : ''}{v}
                        </span>
                      </div>
                    ))}
                    <span className="stat-label">严重度变化</span>
                  </div>
                </div>
              </>
            )}

            {/* Issue changes table — data from snapshot.issue_changes, NEVER recomputed */}
            <table className="diff-table">
              <thead>
                <tr><th>变化类型</th><th>Issue ID</th><th>标题</th><th>变化前</th><th>变化后</th><th>说明</th></tr>
              </thead>
              <tbody>
                {changes.map(c => {
                  const issue = issueIndex[c.issue_id];
                  const isSel = selChange?.issue_id === c.issue_id;
                  return (
                    <tr
                      key={c.issue_id}
                      className={`diff-row diff-type-${c.diff_type}${isSel ? ' selected' : ''}`}
                      onClick={() => handleRowClick(c)}
                      style={{ cursor: 'pointer' }}
                    >
                      <td><span className={`diff-badge diff-${c.diff_type}`}>{DIFF_TYPE_LABEL[c.diff_type]}</span></td>
                      <td><code>{c.issue_id}</code></td>
                      <td>{issue?.title ?? '—'}</td>
                      <td>{c.severity_before ?? '—'}</td>
                      <td>{c.severity_after ?? '—'}</td>
                      <td>{c.summary}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Right: RecheckIssueDiffItem detail panel */}
          {selChange && (
            <aside className="diff-detail-panel">
              <div className="panel-header">
                <span>RecheckIssueDiffItem</span>
                <button onClick={() => setSelChange(null)}>×</button>
              </div>
              <dl className="kv-grid">
                <dt>issue_id</dt><dd><code>{selChange.issue_id}</code></dd>
                <dt>diff_type</dt><dd><code className={`diff-${selChange.diff_type}`}>{selChange.diff_type}</code></dd>
                <dt>severity_before</dt><dd>{selChange.severity_before ?? '—'}</dd>
                <dt>severity_after</dt><dd>{selChange.severity_after ?? '—'}</dd>
              </dl>
              <h4>Summary</h4>
              <p>{selChange.summary}</p>

              {/* Workbench drilldown — structural context, no diff recomputation */}
              <button
                className="btn btn-primary"
                onClick={() => handleDrilldown(selChange)}
              >
                ◈ 查看 Workbench 详情
              </button>

              {/* diff_type display strategy */}
              <div className="drilldown-hint">
                {selChange.diff_type === 'new'              && '此 issue 在 Run B 中首次出现（新增）'}
                {selChange.diff_type === 'resolved'         && '此 issue 在 Run B 中已消失（来自 Run A）'}
                {selChange.diff_type === 'remaining'        && '此 issue 在两次运行中持续存在'}
                {selChange.diff_type === 'severity_changed' && '此 issue 严重度发生变化'}
                {selChange.diff_type === 'regression'       && '此 issue 曾消除后再次出现（回归）'}
              </div>

              {/* Before issue summary */}
              {issueIndex[selChange.issue_id] && (
                <div className="before-issue-summary">
                  <h4>before_issue 摘要</h4>
                  <p>{issueIndex[selChange.issue_id].title}</p>
                  <dl className="kv-grid">
                    <dt>rule_id</dt><dd>{issueIndex[selChange.issue_id].rule_id}</dd>
                    <dt>anchor_id</dt><dd>{issueIndex[selChange.issue_id].anchor_id}</dd>
                  </dl>
                </div>
              )}
            </aside>
          )}
        </div>
      )}
    </div>
  );
};

export default DiffComparePage;
