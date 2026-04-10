import React, { useEffect, useState } from 'react';
import { Card, Tag, Collapse, Spin, Empty, Typography } from 'antd';
import { GitCommit, Plus, Minus, Edit3 } from 'lucide-react';
import { rulesApi, DiffResponse } from '../api/rules';

const { Panel } = Collapse;
const { Title, Text } = Typography;

interface DiffPanelProps {
  baselineId?: string;
  refreshTrigger?: number; // Used to trigger refresh after publish
}

const DiffPanel: React.FC<DiffPanelProps> = ({ baselineId, refreshTrigger = 0 }) => {
  const [loading, setLoading] = useState(false);
  const [diffData, setDiffData] = useState<DiffResponse | null>(null);

  useEffect(() => {
    if (!baselineId) return;

    const fetchDiff = async () => {
      setLoading(true);
      try {
        const data = await rulesApi.getBaselineDiff(baselineId);
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

  return (
    <div className="h-full bg-white border-l border-gray-200 overflow-y-auto p-4">
      <div className="flex items-center space-x-2 mb-6 pb-2 border-b border-gray-100">
        <GitCommit size={20} className="text-blue-600" />
        <Title level={5} className="!m-0">Baseline Diff</Title>
      </div>

      {loading ? (
        <div className="flex justify-center items-center py-10">
          <Spin />
        </div>
      ) : !diffData ? (
        <Empty description="No diff data available" />
      ) : (
        <div className="space-y-4">
          {/* Added Rules */}
          {diffData.added_rules?.length > 0 && (
            <Card
              size="small"
              title={<span className="text-green-600 flex items-center gap-2"><Plus size={14} /> Added ({diffData.added_rules.length})</span>}
              className="border-green-200 bg-green-50 shadow-sm"
            >
              <ul className="list-disc pl-5 m-0 text-sm text-green-800">
                {diffData.added_rules.map((rule: any, i: number) => (
                  <li key={i}>{rule.name || rule.id} <Tag className="ml-2" color="green">{rule.type}</Tag></li>
                ))}
              </ul>
            </Card>
          )}

          {/* Removed Rules */}
          {diffData.removed_rules?.length > 0 && (
            <Card
              size="small"
              title={<span className="text-red-600 flex items-center gap-2"><Minus size={14} /> Removed ({diffData.removed_rules.length})</span>}
              className="border-red-200 bg-red-50 shadow-sm"
            >
              <ul className="list-disc pl-5 m-0 text-sm text-red-800">
                {diffData.removed_rules.map((rule: any, i: number) => (
                  <li key={i}>{rule.name || rule.id} <Tag className="ml-2" color="red">{rule.type}</Tag></li>
                ))}
              </ul>
            </Card>
          )}

          {/* Modified Rules */}
          {diffData.modified_rules?.length > 0 && (
            <div className="mt-4">
              <div className="flex items-center gap-2 mb-3 text-orange-600 font-medium">
                <Edit3 size={16} /> Modified ({diffData.modified_rules.length})
              </div>
              <Collapse expandIconPosition="end" ghost className="bg-orange-50 border border-orange-200 rounded-md">
                {diffData.modified_rules.map((rule, i) => (
                  <Panel
                    key={i}
                    header={<Text strong className="text-orange-700">{rule.rule_id}</Text>}
                    className="border-b border-orange-100 last:border-b-0"
                  >
                    <div className="mb-3">
                      <Text type="secondary" className="text-xs uppercase tracking-wider block mb-1">Changed Fields</Text>
                      <div className="bg-white p-2 rounded border border-orange-100">
                        {Object.entries(rule.changed_fields).map(([field, changes]: [string, any]) => (
                          <div key={field} className="text-sm font-mono flex items-center flex-wrap mb-1 last:mb-0">
                            <span className="text-gray-500 w-24 truncate" title={field}>{field}:</span>
                            <span className="text-red-500 line-through mr-2">{JSON.stringify(changes.old)}</span>
                            <span className="text-gray-400 mx-1">→</span>
                            <span className="text-green-600 ml-2">{JSON.stringify(changes.new)}</span>
                          </div>
                        ))}
                      </div>
                    </div>

                    {rule.evidence && (
                      <div>
                        <Text type="secondary" className="text-xs uppercase tracking-wider block mb-1">Evidence</Text>
                        <pre className="bg-gray-800 text-gray-200 p-2 rounded text-xs font-mono overflow-x-auto m-0 shadow-inner">
                          {JSON.stringify(rule.evidence, null, 2)}
                        </pre>
                      </div>
                    )}
                  </Panel>
                ))}
              </Collapse>
            </div>
          )}

          {diffData.added_rules?.length === 0 && diffData.removed_rules?.length === 0 && diffData.modified_rules?.length === 0 && (
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
