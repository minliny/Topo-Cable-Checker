// pages/VersionManagementPage.tsx
// P2 CONSTRAINT: changes must come from VERSION_CHANGE_SUMMARIES (structured)
// P2 CONSTRAINT: version diff must come from VERSION_DIFF_SNAPSHOTS, never UI set-computed
// P2 CONSTRAINT: no Set-based rule diff, no UI-derived rule categorization

import React, { useState, useEffect } from 'react';
import { VersionChangeSummary, VersionSnapshot, VersionDiffSnapshot, VersionChangeItem, VersionDiffFieldChange } from '../models/version';
import { Baseline } from '../models/baseline';
import { getVersionList, getVersionSnapshot, getVersionDiff } from '../api';
import { VERSION_CHANGE_SUMMARIES } from '../mocks/version.mock';

const CHANGE_TYPE_LABEL: Record<string, string> = {
  rule_added: '规则新增', rule_removed: '规则删除', rule_modified: '规则修改',
  param_changed: '参数变更', threshold_changed: '阈值变更',
  scope_changed: '范围变更', ruleset_changed: '规则集变更',
};

export interface VersionEntry {
  version: string;
  status: 'published' | 'draft' | 'deprecated';
  rule_count: number;
  published_at: string | null;
}

export interface VersionManagementPageProps {
  baseline: Baseline;
  versions: VersionEntry[];
}

export const VersionManagementPage: React.FC<VersionManagementPageProps> = ({
  baseline,
  versions,
}) => {
  const [snapshotVer, setSnapshotVer] = useState<string | null>(null);
  const [diffFrom, setDiffFrom] = useState('');
  const [diffTo, setDiffTo]   = useState('');
  const [rollbackMsg, setRollbackMsg] = useState<Record<string, string>>({});
  const [snapshotData, setSnapshotData] = useState<VersionSnapshot | null>(null);
  const [diffData, setDiffData] = useState<VersionDiffSnapshot | null>(null);

  useEffect(() => {
    if (snapshotVer) {
      const versionId = `${baseline.id}|${snapshotVer}`;
      getVersionSnapshot(versionId).then(setSnapshotData);
    } else {
      setSnapshotData(null);
    }
  }, [snapshotVer, baseline.id]);

  useEffect(() => {
    if (diffFrom && diffTo) {
      getVersionDiff(diffFrom, diffTo).then(setDiffData);
    } else {
      setDiffData(null);
    }
  }, [diffFrom, diffTo]);

  function nextDraftVersion(v: string): string {
    const parts = v.split('.');
    const major = parts[0] ?? '0';
    const minorRaw = parts[1] ?? '0';
    return `${major}.${parseInt(minorRaw, 10) + 1}.0-draft`;
  }

  function handleRollback(ver: VersionEntry) {
    const draft = nextDraftVersion(ver.version);
    setRollbackMsg(m => ({ ...m, [ver.version]: `将基于 v${ver.version} 创建新草稿，版本号将递增至 ${draft}` }));
    setTimeout(() => {
      setRollbackMsg(m => ({ ...m, [ver.version]: `✓ 回滚草稿已创建（模拟）` }));
    }, 1200);
  }

  const publishedVersions = versions.filter(v => v.status !== 'draft');

  return (
    <div className="page version-management-page">
      <div className="page-header">
        <div>
          <div className="page-title">版本管理 — {baseline.name}</div>
          <div className="page-sub">结构化变更记录 · 版本快照 · 版本间 diff 对比</div>
        </div>
        {baseline.status === 'draft' && (
          <button className="btn btn-primary">发布当前草稿 ({baseline.version})</button>
        )}
      </div>

      {/* ── Version list — structured changes from VERSION_CHANGE_SUMMARIES ── */}
      <section className="version-list-section">
        <h3>版本列表</h3>
        {versions.map((v, i) => {
          const cs: VersionChangeSummary | undefined = VERSION_CHANGE_SUMMARIES[`${baseline.id}|${v.version}`];
          const rb = rollbackMsg[v.version];
          return (
            <div key={v.version} className="version-row">
              <div className="version-main">
                <code className="ver-num">{v.version}</code>
                <span className={`status-badge status-${v.status}`}>{v.status}</span>

                {/* Structured change badges — NOT free text */}
                {cs ? (
                  <div className="change-badges">
                    {cs.rule_added_count    > 0 && <span className="badge added">+{cs.rule_added_count} 规则</span>}
                    {cs.rule_removed_count  > 0 && <span className="badge removed">−{cs.rule_removed_count} 规则</span>}
                    {cs.rule_modified_count > 0 && <span className="badge modified">~{cs.rule_modified_count} 规则修改</span>}
                    {cs.parameter_changed_keys.length > 0 && <span className="badge param">{cs.parameter_changed_keys.length} 参数变更</span>}
                    {cs.threshold_changed_keys.length > 0 && <span className="badge threshold">{cs.threshold_changed_keys.length} 阈值变更</span>}
                    {cs.scope_changed_count > 0 && <span className="badge scope">{cs.scope_changed_count} 范围变更</span>}
                  </div>
                ) : <span className="no-changes">—</span>}

                <span className="rule-count">{v.rule_count} 规则</span>
                <span className="pub-date">{v.published_at ?? '未发布'}</span>

                <div className="version-actions">
                  <button onClick={() => setSnapshotVer(snapshotVer === v.version ? null : v.version)}>
                    {snapshotVer === v.version ? '收起快照' : '查看快照'}
                  </button>
                  {v.status === 'deprecated' && i > 0 && (
                    <button onClick={() => handleRollback(v)}>回滚至此版本</button>
                  )}
                  {v.status === 'published' && <span className="current-badge">✓ 当前版本</span>}
                </div>
              </div>

              {/* Rollback status feedback */}
              {rb && <div className="rollback-feedback">{rb}</div>}

              {/* Version snapshot panel */}
              {snapshotVer === v.version && (
                snapshotData ? (
                  <div className="snapshot-panel">
                    <h4>版本快照 — {snapshotData.version}</h4>
                    <div className="snapshot-grid">
                      <div className="snapshot-block">
                        <h5>基础信息</h5>
                        <dl className="kv-grid">
                          <dt>snapshot_id</dt><dd><code>{snapshotData.snapshot_id}</code></dd>
                          <dt>baseline_id</dt><dd>{snapshotData.baseline_id}</dd>
                          <dt>version</dt><dd>{snapshotData.version}</dd>
                          <dt>status</dt><dd>{snapshotData.status}</dd>
                          <dt>rule_count</dt><dd>{snapshotData.enabled_count} / {snapshotData.rule_count}</dd>
                          <dt>created_at</dt><dd>{snapshotData.created_at}</dd>
                          <dt>published_at</dt><dd>{snapshotData.published_at ?? '未发布'}</dd>
                        </dl>
                      </div>
                      <div className="snapshot-block">
                        <h5>Profile 绑定</h5>
                        <dl className="kv-grid">
                          <dt>parameter_profile_id</dt><dd><code>{snapshotData.parameter_profile_id}</code></dd>
                          <dt>threshold_profile_id</dt><dd><code>{snapshotData.threshold_profile_id}</code></dd>
                          <dt>scope_selector_id</dt><dd><code>{snapshotData.scope_selector_id}</code></dd>
                          <dt>ruleset_ids</dt><dd>{snapshotData.ruleset_ids.join(', ')}</dd>
                        </dl>
                      </div>
                    </div>
                    <p className="snapshot-desc">{snapshotData.description}</p>
                  </div>
                ) : (
                  <div className="snapshot-empty">暂无该版本的完整快照数据</div>
                )
              )}

              {/* Change items detail (collapsible) */}
              {cs && cs.change_items.length > 0 && (
                <details className="change-items-detail">
                  <summary>变更明细（{cs.change_items.length} 项）</summary>
                  <table className="change-items-table">
                    <thead><tr><th>类型</th><th>名称</th><th>ID</th><th>变化前</th><th>变化后</th><th>影响</th></tr></thead>
                    <tbody>
                      {cs.change_items.map((ci: VersionChangeItem) => (
                        <tr key={ci.change_id} className={`impact-${ci.impact_level}`}>
                          <td>{CHANGE_TYPE_LABEL[ci.change_type] ?? ci.change_type}</td>
                          <td>{ci.target_name}</td>
                          <td><code>{ci.target_id}</code></td>
                          <td>{ci.before_summary ? <s>{ci.before_summary}</s> : '—'}</td>
                          <td>{ci.after_summary ?? '—'}</td>
                          <td><span className={`impact impact-${ci.impact_level}`}>{ci.impact_level}</span></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </details>
              )}
            </div>
          );
        })}
      </section>

      {/* ── Version diff — from VERSION_DIFF_SNAPSHOTS only, no UI set-computation ── */}
      <section className="version-diff-section">
        <h3>版本间 RuleSet Diff</h3>
        <div className="diff-selectors">
          <div>
            <label>起始版本</label>
            <select value={diffFrom} onChange={(e: React.ChangeEvent<HTMLSelectElement>) => { setDiffFrom(e.target.value); setDiffTo(''); }}>
              <option value="">— 选择版本 —</option>
              {publishedVersions.map(v => <option key={v.version} value={v.version}>{v.version}</option>)}
            </select>
          </div>
          <span>→</span>
          <div>
            <label>目标版本</label>
            <select value={diffTo} onChange={(e: React.ChangeEvent<HTMLSelectElement>) => setDiffTo(e.target.value)} disabled={!diffFrom}>
              <option value="">— 选择版本 —</option>
              {publishedVersions.filter(v => v.version !== diffFrom).map(v => (
                <option key={v.version} value={v.version}>{v.version}</option>
              ))}
            </select>
          </div>
        </div>

        {!diffFrom || !diffTo ? (
          <p className="hint">请选择两个版本以查看结构化 diff。</p>
        ) : !diffData ? (
          <div className="empty-state">
            <p>暂无该版本对比快照</p>
            <code>{diffFrom} → {diffTo}</code>
          </div>
        ) : (
          <div className="version-diff-result">
            <code className="diff-id">diff_id: {diffData.diff_id}</code>

            {/* Summary stats */}
            <div className="diff-summary-grid">
              {([
                ['新增规则',  diffData.summary.rule_added_count],
                ['删除规则',  diffData.summary.rule_removed_count],
                ['修改规则',  diffData.summary.rule_modified_count],
                ['参数变更',  diffData.summary.parameter_changed_count],
                ['阈值变更',  diffData.summary.threshold_changed_count],
              ] as [string, number][]).map(([label, val]) => (
                <div key={label} className="summary-stat">
                  <span className="stat-val">{val}</span>
                  <span className="stat-label">{label}</span>
                </div>
              ))}
            </div>

            {/* Rule changes */}
            {diffData.rule_changes.length > 0 && (
              <div className="diff-subsection">
                <h4>规则变更</h4>
                {diffData.rule_changes.map(rc => (
                  <div key={rc.change_id} className={`diff-row diff-rule-${rc.change_type}`}>
                    <span className={`diff-badge ${rc.change_type}`}>
                      {rc.change_type === 'added' ? '新增' : rc.change_type === 'removed' ? '删除' : '修改'}
                    </span>
                    <span className="rule-name">{rc.target_name}</span>
                    <code>{rc.target_id}</code>
                    {rc.before_summary && <><s>{rc.before_summary}</s><span>→</span></>}
                    {rc.after_summary && <span className="after">{rc.after_summary}</span>}
                    <span className={`impact impact-${rc.impact_level}`}>{rc.impact_level}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Parameter / threshold / scope / ruleset changes */}
            {([
              ['参数变更', diffData.parameter_changes],
              ['阈值变更', diffData.threshold_changes],
              ['范围变更', diffData.scope_changes],
              ['规则集变更', diffData.ruleset_changes],
            ] as Array<[string, VersionDiffFieldChange[]]>).map(([label, items]) =>
              items.length > 0 && (
                <div key={label} className="diff-subsection">
                  <h4>{label}</h4>
                  {items.map(ch => (
                    <div key={ch.change_id} className="diff-field-row">
                      <code>{ch.target_id}</code>
                      <span>{ch.target_name}</span>
                      {ch.before_summary && <><s>{ch.before_summary}</s><span>→</span></>}
                      {ch.after_summary && <span className="after">{ch.after_summary}</span>}
                    </div>
                  ))}
                </div>
              )
            )}
          </div>
        )}
      </section>

      <p className="footer-note">
        ⚠ 回滚操作将基于选定版本创建新草稿，版本号自动递增。版本间 diff 来自 VERSION_DIFF_SNAPSHOTS，禁止 UI 现场计算。
      </p>
    </div>
  );
};

export default VersionManagementPage;
