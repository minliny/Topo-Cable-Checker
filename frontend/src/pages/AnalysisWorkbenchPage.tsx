// pages/AnalysisWorkbenchPage.tsx
// P0 CONSTRAINT: Workbench ONLY consumes CheckResultBundle
// P0 CONSTRAINT: No baseline editing, rule editing, version management, execution config
// P0 CONSTRAINT: No UI diff recomputation
// P0 CONSTRAINT: drilldown context display with empty state when issue not found

import React, { useState, useEffect, useCallback } from 'react';
import { WorkbenchDrilldownContext, RecheckDiffType, RecheckIssueDiffItem } from '../models/diff';
import { CheckResultBundle, IssueItem } from '../models/execution';

export interface AnalysisWorkbenchPageProps {
  run: CheckResultBundle;
  drilldown: WorkbenchDrilldownContext | null;
  onNavigate: (nav: { section: 'diff'; sub: 'compare'; ctx?: { runId?: string } }) => void;
}

type SeverityFilter = 'all' | 'critical' | 'warning' | 'info';
type DetailTab = 'detail' | 'evidence' | 'context' | 'diff';

const SEVERITY_ORDER = ['critical', 'warning', 'info'] as const;

const DIFF_TYPE_HINT: Record<RecheckDiffType, string> = {
  new:              '此 issue 在 Run B 中首次出现（新增）',
  resolved:         '此 issue 在 Run B 中已消失（来自 Run A）',
  remaining:        '此 issue 在两次运行中持续存在',
  severity_changed: '此 issue 严重度发生变化',
  regression:       '此 issue 曾消除后再次出现（回归）',
};

function scoreColor(score: number): string {
  if (score >= 80) return 'score-good';
  if (score >= 50) return 'score-mid';
  return 'score-bad';
}

export const AnalysisWorkbenchPage: React.FC<AnalysisWorkbenchPageProps> = ({
  run,
  drilldown,
  onNavigate,
}) => {
  const [sevFilter, setSevFilter] = useState<SeverityFilter>('all');
  const [search, setSearch] = useState('');
  const [selIssue, setSelIssue] = useState<IssueItem | null>(null);
  const [activeTab, setActiveTab] = useState<DetailTab>('detail');

  const issues = run.issues ?? [];

  const filteredIssues = issues
    .filter(i => {
      if (sevFilter !== 'all' && i.severity !== sevFilter) return false;
      if (search) {
        const q = search.toLowerCase();
        if (!i.title.toLowerCase().includes(q) && !i.ruleId.toLowerCase().includes(q)) return false;
      }
      return true;
    })
    .sort((a, b) => SEVERITY_ORDER.indexOf(a.severity) - SEVERITY_ORDER.indexOf(b.severity));

  const criticalCount = issues.filter(i => i.severity === 'critical').length;
  const warningCount = issues.filter(i => i.severity === 'warning').length;
  const infoCount = issues.filter(i => i.severity === 'info').length;

  // Auto-select issue from drilldown
  useEffect(() => {
    if (!drilldown || !run) return;
    const target = issues.find(i => i.id === drilldown.issue_id);
    if (target) {
      setSelIssue(target);
    } else {
      setSelIssue(null);
    }
  }, [drilldown?.issue_id, run?.id]);

  // Reset tab when issue changes
  useEffect(() => {
    if (selIssue) setActiveTab('detail');
  }, [selIssue?.id]);

  const handleNavigateBack = useCallback(() => {
    if (drilldown) {
      onNavigate({ section: 'diff', sub: 'compare', ctx: { runId: drilldown.from_run_id } });
    } else {
      onNavigate({ section: 'diff', sub: 'compare' });
    }
  }, [drilldown, onNavigate]);

  if (!run) {
    return (
      <div className="page workbench-page">
        <div className="empty-state">
          <div className="empty-icon">◎</div>
          <div className="empty-title">暂无分析结果</div>
          <div className="empty-desc">请先执行检查</div>
        </div>
      </div>
    );
  }

  const drilldownNotFound = drilldown && !selIssue;

  return (
    <div className="page workbench-page">
      {/* Drilldown context banner */}
      {drilldown && (
        <div className="drilldown-banner">
          <span className="drilldown-label">◈ 差异下钻</span>
          <span className="drilldown-meta">{drilldown.diff_id}</span>
          <span className="drilldown-run">{drilldown.from_run_id.replace('run-', '')} → {drilldown.to_run_id.replace('run-', '')}</span>
          <span className={`drilldown-type diff-type-${drilldown.diff_type}`}>{drilldown.diff_type}</span>
          <span className="drilldown-hint">{DIFF_TYPE_HINT[drilldown.diff_type]}</span>
          <button className="drilldown-back-btn" onClick={handleNavigateBack}>← 返回差异对比</button>
        </div>
      )}

      {/* Run summary ribbon */}
      <div className="page-header">
        <div className="header-left">
          <div className="page-title">分析工作台</div>
          <div className="page-sub">{run.scenario} · v{run.baseline_version} · {run.time}</div>
        </div>
      </div>

      <div className="run-ribbon">
        <div className="score-block">
          <span className={`score-num ${scoreColor(run.score)}`}>{run.score}</span>
          <span className="score-label">风险分数</span>
        </div>
        <div className="ribbon-sep" />
        <div className="severity-cards">
          {(['critical', 'warning', 'info'] as const).map(sev => {
            const count = sev === 'critical' ? criticalCount : sev === 'warning' ? warningCount : infoCount;
            const label = sev === 'critical' ? '严重' : sev === 'warning' ? '警告' : '提示';
            const cls = sev === 'critical' ? 'crit' : sev === 'warning' ? 'warn' : 'info';
            return (
              <div
                key={sev}
                className={`sev-card ${cls} ${sevFilter === sev ? 'active' : ''}`}
                onClick={() => setSevFilter(prev => prev === sev ? 'all' : sev)}
              >
                <span className="sc-n">{count}</span>
                <span className="sc-l">{label}</span>
              </div>
            );
          })}
        </div>
        <div className="ribbon-sep" />
        <div className="run-meta">
          <div className="run-scenario">{run.scenario}</div>
          <div className="run-time">{run.time} · v{run.baseline_version}</div>
        </div>
      </div>

      {/* Main work area */}
      <div className="work-area">
        {/* Issue list pane */}
        <div className={`issue-pane ${selIssue ? 'split' : 'wide'}`}>
          <div className="toolbar">
            <input
              className="search-input"
              placeholder="搜索问题…"
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
            <div className="filter-buttons">
              {(['all', 'critical', 'warning', 'info'] as const).map(s => (
                <button
                  key={s}
                  className={`filter-btn ${sevFilter === s ? 'active' : ''}`}
                  onClick={() => setSevFilter(s)}
                >
                  {s === 'all' ? '全部' : s === 'critical' ? '严重' : s === 'warning' ? '警告' : '提示'}
                </button>
              ))}
            </div>
            <span className="issue-count">{filteredIssues.length}/{issues.length}</span>
          </div>

          <div className="issue-scroll">
            {filteredIssues.map(iss => (
              <div
                key={iss.id}
                className={`issue-row ${selIssue?.id === iss.id ? 'selected' : ''}`}
                onClick={() => setSelIssue(prev => prev?.id === iss.id ? null : iss)}
              >
                <span className={`sev-dot ${iss.severity}`} />
                <div className="issue-body">
                  <div className="issue-title">{iss.title}</div>
                  <div className="issue-meta">
                    <span className="rule-id">{iss.ruleId}</span>
                    <span className="anchor-id">{iss.anchor_id}</span>
                  </div>
                </div>
                <SevTag sev={iss.severity} />
              </div>
            ))}
          </div>
        </div>

        {/* Detail pane */}
        {selIssue ? (
          <IssueDetailPanel
            issue={selIssue}
            activeTab={activeTab}
            onTabChange={setActiveTab}
            onClose={() => setSelIssue(null)}
            drilldown={drilldown}
          />
        ) : (
          <div className="detail-pane empty-detail">
            {drilldownNotFound ? (
              <div className="empty-state drilldown-empty">
                <div className="empty-icon warn-icon">⊕</div>
                <div className="empty-title">当前运行结果中未找到该 issue</div>
                <div className="empty-desc">
                  issue_id: {drilldown?.issue_id}<br />
                  可能属于已消失 / 范围变化 / 历史差异项
                </div>
                {drilldown?.issue_diff_item && (
                  <DrilldownIssueDiffSummary diffItem={drilldown.issue_diff_item} diffType={drilldown.diff_type} />
                )}
              </div>
            ) : (
              <div className="empty-state">
                <div className="empty-icon">◈</div>
                <div className="empty-title">请选择左侧问题以查看详情</div>
                <div className="empty-desc">问题详情 · 证据说明 · 上下文 · 差异对比</div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

interface IssueDetailPanelProps {
  issue: IssueItem;
  activeTab: DetailTab;
  onTabChange: (tab: DetailTab) => void;
  onClose: () => void;
  drilldown: WorkbenchDrilldownContext | null;
}

function IssueDetailPanel({ issue, activeTab, onTabChange, onClose, drilldown }: IssueDetailPanelProps) {
  return (
    <div className="detail-pane">
      <div className="detail-header">
        <div className="detail-title-row">
          <SevTag sev={issue.severity} />
          <code className="rule-id">{issue.ruleId}</code>
          {issue.rule_category && <span className="cat-tag">{issue.rule_category}</span>}
        </div>
        <div className="detail-title">{issue.title}</div>
      </div>

      <div className="detail-tabs">
        {(['detail', 'evidence', 'context', 'diff'] as DetailTab[]).map(id => (
          <button
            key={id}
            className={`tab-btn ${activeTab === id ? 'active' : ''}`}
            onClick={() => onTabChange(id)}
          >
            {id === 'detail' ? '问题详情' : id === 'evidence' ? '证据说明' : id === 'context' ? '上下文' : '差异对比'}
          </button>
        ))}
        <button className="close-btn" onClick={onClose}>×</button>
      </div>

      <div className="detail-body">
        {activeTab === 'detail' && <TabDetail issue={issue} />}
        {activeTab === 'evidence' && <TabEvidence issue={issue} />}
        {activeTab === 'context' && <TabContext issue={issue} />}
        {activeTab === 'diff' && <TabDiff issue={issue} drilldown={drilldown} />}
      </div>
    </div>
  );
}

function TabDetail({ issue }: { issue: IssueItem }) {
  return (
    <div className="tab-content">
      <div className="d-block">
        <h4>基本信息</h4>
        <dl className="kv-grid">
          <dt>规则 ID</dt><dd><code>{issue.rule_id}</code></dd>
          <dt>规则名称</dt><dd>{issue.rule_name}</dd>
          <dt>类别</dt><dd>{issue.rule_category}</dd>
          <dt>锚点类型</dt><dd>{issue.anchor_type}</dd>
          <dt>锚点 ID</dt><dd><code>{issue.anchor_id}</code></dd>
        </dl>
      </div>
      <div className="d-block">
        <h4>来源 / 目标</h4>
        <dl className="kv-grid">
          <dt>来源设备</dt><dd>{issue.source_device}</dd>
          <dt>来源端口</dt><dd>{issue.source_port}</dd>
          <dt>目标设备</dt><dd>{issue.target_device}</dd>
          <dt>目标端口</dt><dd>{issue.target_port}</dd>
        </dl>
      </div>
      <div className="d-block">
        <h4>问题说明</h4>
        <p className="plain-text">{issue.description}</p>
      </div>
      <div className="d-block">
        <h4>修复建议</h4>
        <p className="plain-text">{issue.remediation}</p>
      </div>
    </div>
  );
}

function TabEvidence({ issue }: { issue: IssueItem }) {
  const ev = issue.evidence;
  if (!ev) {
    return (
      <div className="empty-state">
        <div className="empty-icon">○</div>
        <div className="empty-title">暂无证据数据</div>
      </div>
    );
  }
  return (
    <div className="tab-content">
      <div className="ev-compare">
        <div className="ev-cell expected">
          <div className="ev-lbl">期望值</div>
          <div className="ev-val">{ev.expected_value}</div>
        </div>
        <div className="ev-cell mid">{ev.comparison_operator}</div>
        <div className="ev-cell actual">
          <div className="ev-lbl">实际值</div>
          <div className="ev-val">{ev.actual_value}</div>
        </div>
      </div>
      <div className="d-block">
        <h4>证据元数据</h4>
        <dl className="kv-grid">
          <dt>证据类型</dt><dd>{ev.evidence_type}</dd>
          <dt>字段名</dt><dd>{ev.field_name}</dd>
        </dl>
      </div>
      {ev.related_values && Object.keys(ev.related_values).length > 0 && (
        <div className="d-block">
          <h4>相关值</h4>
          <dl className="kv-grid">
            {Object.entries(ev.related_values).map(([k, v]) => (
              <React.Fragment key={k}>
                <dt>{k}</dt><dd>{v}</dd>
              </React.Fragment>
            ))}
          </dl>
        </div>
      )}
    </div>
  );
}

function TabContext({ issue }: { issue: IssueItem }) {
  const ctx = issue._review_context;
  if (!ctx) {
    return (
      <div className="empty-state">
        <div className="empty-icon">○</div>
        <div className="empty-title">暂无上下文信息</div>
      </div>
    );
  }
  return (
    <div className="tab-content">
      {ctx.related_devices && ctx.related_devices.length > 0 && (
        <div className="d-block">
          <h4>关联设备 ({ctx.related_devices.length})</h4>
          <div className="ctx-list">
            {ctx.related_devices.map(d => (
              <div key={d.id} className="ctx-row">
                <span className="ctx-dot unknown" />
                <span className="ctx-name">{d.id}</span>
                <span className="ctx-meta">{d.role}</span>
                <span className="ctx-meta" style={{ marginLeft: 8 }}>{d.firmware}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      {ctx.related_ports && ctx.related_ports.length > 0 && (
        <div className="d-block">
          <h4>关联端口 ({ctx.related_ports.length})</h4>
          <div className="ctx-list">
            {ctx.related_ports.map((p, i) => (
              <div key={i} className="ctx-row">
                <span className={`ctx-dot ${p.status === 'up' ? 'up' : p.status === 'down' ? 'down' : 'unknown'}`} />
                <span className="ctx-name">{p.device} · {p.port}</span>
                <span className="ctx-meta">{p.speed}</span>
                <span className="ctx-meta" style={{ marginLeft: 8 }}>{p.peer}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      {ctx.related_links && ctx.related_links.length > 0 && (
        <div className="d-block">
          <h4>关联链路 ({ctx.related_links.length})</h4>
          <div className="ctx-list">
            {ctx.related_links.map(l => (
              <div key={l.id} className="ctx-row">
                <span className={`ctx-dot ${l.status === 'up' ? 'up' : l.status === 'down' ? 'down' : 'unknown'}`} />
                <span className="ctx-name">{l.from} → {l.to}</span>
                <span className="ctx-meta">{l.utilization}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function TabDiff({ issue, drilldown }: { issue: IssueItem; drilldown: WorkbenchDrilldownContext | null }) {
  const diffItems = issue._diff_items ?? [];
  return (
    <div className="tab-content">
      {drilldown?.issue_diff_item && (
        <div className="d-block">
          <h4>来自 RecheckIssueDiffItem</h4>
          <dl className="kv-grid">
            <dt>diff_type</dt>
            <dd className={`diff-type-${drilldown.diff_type}`}>{drilldown.diff_type}</dd>
            <dt>severity_before</dt><dd>{drilldown.issue_diff_item.severity_before ?? '—'}</dd>
            <dt>severity_after</dt><dd>{drilldown.issue_diff_item.severity_after ?? '—'}</dd>
            <dt>summary</dt><dd>{drilldown.issue_diff_item.summary}</dd>
          </dl>
        </div>
      )}
      {diffItems.length > 0 && (
        <div className="d-block">
          <h4>Issue 级 Diff</h4>
          <div className="diff-item-list">
            {diffItems.map((d, i) => (
              <div key={i} className="diff-item-row">
                <span className={`diff-item-type diff-${d.type}`}>{d.type}</span>
                <span className="diff-item-field">{d.field}</span>
                <span className="diff-item-old">{d.old ?? '—'}</span>
                <span className="diff-item-arrow">→</span>
                <span className="diff-item-new">{d.new ?? '—'}</span>
              </div>
            ))}
          </div>
        </div>
      )}
      {diffItems.length === 0 && !drilldown?.issue_diff_item && (
        <div className="empty-state">
          <div className="empty-icon">○</div>
          <div className="empty-title">暂无差异对比数据</div>
        </div>
      )}
    </div>
  );
}

function DrilldownIssueDiffSummary({ diffItem, diffType }: { diffItem: RecheckIssueDiffItem; diffType: RecheckDiffType }) {
  return (
    <div className="drilldown-issue-summary">
      <div className="summary-label">来自 RecheckIssueDiffItem</div>
      <dl className="kv-grid">
        <dt>diff_type</dt>
        <dd className={`diff-type-${diffType}`}>{diffType}</dd>
        <dt>severity_before</dt><dd>{diffItem.severity_before ?? '—'}</dd>
        <dt>severity_after</dt><dd>{diffItem.severity_after ?? '—'}</dd>
        <dt>summary</dt><dd>{diffItem.summary}</dd>
      </dl>
    </div>
  );
}

function SevTag({ sev }: { sev: 'critical' | 'warning' | 'info' }) {
  const labels = { critical: '严重', warning: '警告', info: '提示' };
  return <span className={`sev-tag sev-${sev}`}>{labels[sev]}</span>;
}

export default AnalysisWorkbenchPage;