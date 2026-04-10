import React from 'react';
import { Card, Typography, Empty } from 'antd';
import { GitCommit } from 'lucide-react';
import { DiffResponse } from '../../api/rules';

const { Title, Text } = Typography;

interface DiffViewProps {
  diffData: DiffResponse | null;
  targetRuleId?: string;
}

const DiffView: React.FC<DiffViewProps> = ({ diffData, targetRuleId }) => {
  if (!diffData) {
    return <Empty description="No diff data loaded." />;
  }

  return (
    <div className="h-full flex flex-col">
      <div className="mb-6 flex items-center gap-2">
        <GitCommit size={24} className="text-blue-600" />
        <Title level={4} className="!m-0">Detailed Diff View</Title>
      </div>

      <div className="flex-1 overflow-y-auto space-y-4">
        {/* Simple rendering for now. In a real app, this would show complex side-by-side diffs. */}
        {diffData.modified_rules.map((rule, idx) => (
          <Card 
            key={idx} 
            title={`Rule: ${rule.rule_id}`} 
            className={`shadow-sm transition-all duration-300 ${
              targetRuleId === rule.rule_id ? 'border-blue-500 shadow-[0_0_0_2px_rgba(59,130,246,0.5)] bg-blue-50' : 'border-gray-200'
            }`}
          >
            <Text type="secondary" className="block mb-2">Changed Fields:</Text>
            <pre className="text-xs bg-white p-3 rounded border border-gray-200 overflow-x-auto font-mono">
              {JSON.stringify(rule.changed_fields, null, 2)}
            </pre>
            
            {rule.evidence && (
              <div className="mt-4">
                <Text type="secondary" className="block mb-2">Evidence:</Text>
                <pre className="text-xs bg-gray-800 text-gray-200 p-3 rounded overflow-x-auto font-mono">
                  {JSON.stringify(rule.evidence, null, 2)}
                </pre>
              </div>
            )}
          </Card>
        ))}
        
        {diffData.modified_rules.length === 0 && (
          <Empty description="No modified rules detail available." />
        )}
      </div>
    </div>
  );
};

export default DiffView;
