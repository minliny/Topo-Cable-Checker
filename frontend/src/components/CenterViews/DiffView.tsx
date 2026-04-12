import React from 'react';
import { Card, Typography, Empty, Button, Tag } from 'antd';
import { GitCommit, ArrowLeft, Plus, Minus, Edit3 } from 'lucide-react';
import { DiffSourceTargetDTO, DiffFieldChangeDTO } from '../../types/dto';

const { Title, Text } = Typography;

interface DiffViewProps {
  diffData: DiffSourceTargetDTO | null;
  targetRuleId?: string;
  onClose?: () => void;
}

const DiffView: React.FC<DiffViewProps> = ({ diffData, targetRuleId, onClose }) => {
  if (!diffData) {
    return <Empty description="No diff data loaded." />;
  }

  // P1.1-2: Separate rules by change type
  const addedRules = diffData.rules.filter(r => r.change_type === 'added');
  const removedRules = diffData.rules.filter(r => r.change_type === 'removed');
  const modifiedRules = diffData.rules.filter(r => r.change_type === 'modified');

  return (
    <div className="h-full flex flex-col">
      <div className="mb-4 flex items-center gap-2">
        {onClose && (
          <Button 
            type="text" 
            icon={<ArrowLeft size={16} />} 
            onClick={onClose}
            className="text-gray-500 hover:text-gray-800"
          />
        )}
        <GitCommit size={24} className="text-blue-600" />
        <Title level={4} className="!m-0">Detailed Diff View</Title>
      </div>

      {/* P1.1-2: Human-readable summary */}
      {diffData.human_readable_summary && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md text-sm text-blue-800">
          {diffData.human_readable_summary}
        </div>
      )}

      <div className="flex-1 overflow-y-auto space-y-4">
        {/* Added Rules */}
        {addedRules.length > 0 && (
          <Card size="small" title={<span className="text-green-600 flex items-center gap-2"><Plus size={14} /> Added ({addedRules.length})</span>} className="border-green-200 bg-green-50 shadow-sm">
            {addedRules.map((rule, idx) => (
              <div key={idx} className={`mb-2 p-2 rounded ${targetRuleId === rule.rule_id ? 'bg-blue-100 border border-blue-300' : ''}`}>
                <Text strong className="text-green-800">{rule.rule_id}</Text>
                {rule.human_summary && <Text className="ml-2 text-xs text-green-600">{rule.human_summary}</Text>}
              </div>
            ))}
          </Card>
        )}

        {/* Removed Rules */}
        {removedRules.length > 0 && (
          <Card size="small" title={<span className="text-red-600 flex items-center gap-2"><Minus size={14} /> Removed ({removedRules.length})</span>} className="border-red-200 bg-red-50 shadow-sm">
            {removedRules.map((rule, idx) => (
              <div key={idx} className={`mb-2 p-2 rounded ${targetRuleId === rule.rule_id ? 'bg-blue-100 border border-blue-300' : ''}`}>
                <Text strong className="text-red-800">{rule.rule_id}</Text>
                {rule.human_summary && <Text className="ml-2 text-xs text-red-600">{rule.human_summary}</Text>}
              </div>
            ))}
          </Card>
        )}

        {/* Modified Rules — P1.1-2: Show per-field before/after */}
        {modifiedRules.map((rule, idx) => (
          <Card 
            key={idx} 
            title={
              <div className="flex items-center gap-2">
                <Edit3 size={14} className="text-orange-600" />
                <span>Rule: {rule.rule_id}</span>
                {rule.human_summary && <Tag color="orange" className="ml-2">{rule.human_summary}</Tag>}
              </div>
            }
            className={`shadow-sm transition-all duration-300 ${
              targetRuleId === rule.rule_id ? 'border-blue-500 shadow-[0_0_0_2px_rgba(59,130,246,0.5)] bg-blue-50' : 'border-gray-200'
            }`}
          >
            <Text type="secondary" className="block mb-2">Changed Fields:</Text>
            {(rule.field_changes && rule.field_changes.length > 0) ? (
              <div className="bg-white p-3 rounded border border-orange-100 space-y-1">
                {rule.field_changes.map((fc: DiffFieldChangeDTO) => (
                  <div key={fc.field_name} className="text-sm font-mono flex items-center flex-wrap">
                    <span className="text-gray-500 w-44 truncate" title={fc.field_name}>{fc.field_name}:</span>
                    <span className="text-red-500 line-through mr-2">{JSON.stringify(fc.old_value)}</span>
                    <span className="text-gray-400 mx-1">→</span>
                    <span className="text-green-600 ml-2">{JSON.stringify(fc.new_value)}</span>
                  </div>
                ))}
              </div>
            ) : (
              <pre className="text-xs bg-white p-3 rounded border border-gray-200 overflow-x-auto font-mono">
                {JSON.stringify(rule.changed_fields, null, 2)}
              </pre>
            )}
          </Card>
        ))}
        
        {addedRules.length === 0 && removedRules.length === 0 && modifiedRules.length === 0 && (
          <Empty description="No differences found between versions." />
        )}
      </div>
    </div>
  );
};

export default DiffView;
