import React, { useEffect, useState } from 'react';
import { Card, Tag, Collapse, Spin, Empty, Typography, Badge } from 'antd';
import { GitCommit, Plus, Minus, Edit3 } from 'lucide-react';
import { rulesApi } from '../api/rules';
import { DiffSourceTargetDTO, DiffRuleDTO, DiffFieldChangeDTO } from '../types/dto';

const { Panel } = Collapse;
const { Title, Text } = Typography;

interface DiffPanelProps {
  baselineId?: string;
  refreshTrigger?: number; // Used to trigger refresh after publish
}

const DiffPanel: React.FC<DiffPanelProps> = ({ baselineId, refreshTrigger = 0 }) => {
  const [loading, setLoading] = useState(false);
  const [diffData, setDiffData] = useState<DiffSourceTargetDTO | null>(null);

  useEffect(() => {
    if (!baselineId) return;

    const fetchDiff = async () => {
      setLoading(true);
      try {
        const data = await rulesApi.getBaselineDiff(baselineId, 'draft', 'previous_version');
        setDiffData(data);
      } catch (error) {
        console.error('Failed to fetch diff', error);
        setDiffData(null);
      } finally {
        setLoading(false);
      }
    };

    fetchDiff();
  }, [baselineId, refreshTrigger]);

  if (!baselineId) {
    return (
      <div className="h-full bg-white border-l border-gray-200 flex flex-col items-center justify-center p-6">
        <Empty description="Select a baseline to view diff" />
      </div>
    );
  }

  // P1.1-2: Separate rules by change type from unified rules array
  const addedRules = diffData?.rules.filter(r => r.change_type === 'added') || [];
  const removedRules = diffData?.rules.filter(r => r.change_type === 'removed') || [];
  const modifiedRules = diffData?.rules.filter(r => r.change_type === 'modified') || [];

  return (
    <div className="h-full bg-white border-l border-gray-200 overflow-y-auto p-4">
      <div className="flex items-center space-x-2 mb-4 pb-2 border-b border-gray-100">
        <GitCommit size={20} className="text-blue-600" />
        <Title level={5} className="!m-0">Baseline Diff</Title>
      </div>

      {/* P1.1-2: Human-readable summary banner */}
      {diffData?.human_readable_summary && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md text-sm text-blue-800">
          {diffData.human_readable_summary}
        </div>
      )}

      {loading ? (
        <div className="flex justify-center items-center py-10">
          <Spin />
        </div>
      ) : !diffData ? (
        <Empty description="No diff data available" />
      ) : (
        <div className="space-y-4">
          {/* Added Rules */}
          {addedRules.length > 0 && (
            <Card
              size="small"
              title={<span className="text-green-600 flex items-center gap-2"><Plus size={14} /> Added ({addedRules.length})</span>}
              className="border-green-200 bg-green-50 shadow-sm"
            >
              <ul className="list-disc pl-5 m-0 text-sm text-green-800">
                {addedRules.map((rule, i) => (
                  <li key={i} className="mb-1">
                    <span className="font-medium">{rule.rule_id}</span>
                    {rule.human_summary && <span className="ml-2 text-green-600 text-xs">{rule.human_summary}</span>}
                  </li>
                ))}
              </ul>
            </Card>
          )}

          {/* Removed Rules */}
          {removedRules.length > 0 && (
            <Card
              size="small"
              title={<span className="text-red-600 flex items-center gap-2"><Minus size={14} /> Removed ({removedRules.length})</span>}
              className="border-red-200 bg-red-50 shadow-sm"
            >
              <ul className="list-disc pl-5 m-0 text-sm text-red-800">
                {removedRules.map((rule, i) => (
                  <li key={i} className="mb-1">
                    <span className="font-medium">{rule.rule_id}</span>
                    {rule.human_summary && <span className="ml-2 text-red-600 text-xs">{rule.human_summary}</span>}
                  </li>
                ))}
              </ul>
            </Card>
          )}

          {/* Modified Rules — P1.1-2: Show per-field before/after */}
          {modifiedRules.length > 0 && (
            <div className="mt-4">
              <div className="flex items-center gap-2 mb-3 text-orange-600 font-medium">
                <Edit3 size={16} /> Modified ({modifiedRules.length})
              </div>
              <Collapse expandIconPosition="end" ghost className="bg-orange-50 border border-orange-200 rounded-md">
                {modifiedRules.map((rule, i) => (
                  <Panel
                    key={i}
                    header={
                      <div className="flex items-center gap-2">
                        <Text strong className="text-orange-700">{rule.rule_id}</Text>
                        {rule.human_summary && (
                          <Text className="text-xs text-gray-500 truncate max-w-[300px]" title={rule.human_summary}>
                            {rule.human_summary}
                          </Text>
                        )}
                      </div>
                    }
                    className="border-b border-orange-100 last:border-b-0"
                  >
                    <div className="mb-3">
                      <Text type="secondary" className="text-xs uppercase tracking-wider block mb-1">Changed Fields</Text>
                      <div className="bg-white p-2 rounded border border-orange-100">
                        {/* P1.1-2: Use field_changes for before/after display */}
                        {(rule.field_changes && rule.field_changes.length > 0)
                          ? rule.field_changes.map((fc: DiffFieldChangeDTO) => (
                            <div key={fc.field_name} className="text-sm font-mono flex items-center flex-wrap mb-1 last:mb-0">
                              <span className="text-gray-500 w-44 truncate" title={fc.field_name}>{fc.field_name}:</span>
                              <span className="text-red-500 line-through mr-2">{JSON.stringify(fc.old_value)}</span>
                              <span className="text-gray-400 mx-1">→</span>
                              <span className="text-green-600 ml-2">{JSON.stringify(fc.new_value)}</span>
                            </div>
                          ))
                          : (rule.changed_fields || []).map((field: string) => (
                            <div key={field} className="text-sm font-mono text-gray-500 mb-1">{field}</div>
                          ))
                        }
                      </div>
                    </div>
                  </Panel>
                ))}
              </Collapse>
            </div>
          )}

          {addedRules.length === 0 && removedRules.length === 0 && modifiedRules.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              No changes detected in this baseline.
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DiffPanel;
