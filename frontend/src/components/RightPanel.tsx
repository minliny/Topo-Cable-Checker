import React from 'react';
import { Card, Tag, Collapse, Spin, Empty, Typography, Alert, Divider, Button } from 'antd';
import { GitCommit, Plus, Minus, Edit3, HelpCircle, CheckCircle, FileSearch, Archive, UploadCloud } from 'lucide-react';
import { ValidationResult, DiffResponse } from '../api/rules';
import { RightPanelMode } from '../types/ui';

const { Panel } = Collapse;
const { Title, Text } = Typography;

interface RightPanelProps {
  mode: RightPanelMode;
  validationResult: ValidationResult | null;
  diffData: DiffResponse | null;
  loading: boolean;
  onJumpToField?: (field: string) => void;
  onJumpToRule?: (ruleId: string) => void;
  onRequestDiff?: () => void;
}

const RightPanel: React.FC<RightPanelProps> = ({
  mode,
  validationResult,
  diffData,
  loading,
  onJumpToField,
  onJumpToRule,
  onRequestDiff
}) => {

  const renderHelp = () => (
    <div className="space-y-4">
      <Alert
        title="Editing Rules"
        description="Select a rule type and input the parameters in JSON format. The required parameters depend on the selected rule type."
        type="info"
        showIcon
      />
      <Card size="small" title="Threshold Rule Example" className="shadow-sm">
        <pre className="text-xs bg-gray-50 p-2 rounded font-mono">
{`{
  "threshold": 10,
  "severity": "warning"
}`}
        </pre>
      </Card>
      <Card size="small" title="Pattern Match Example" className="shadow-sm">
        <pre className="text-xs bg-gray-50 p-2 rounded font-mono">
{`{
  "regex": "^[a-z]+$",
  "field": "username"
}`}
        </pre>
      </Card>
    </div>
  );

  const renderValidation = () => {
    if (!validationResult) {
      return <Empty description="No validation result yet. Click Validate to check the rule." />;
    }

    return (
      <Card title="Validation Result" size="small" className="shadow-sm border-gray-200">
        {validationResult.valid ? (
          <Alert title="Rule is valid" type="success" showIcon className="mb-4" />
        ) : (
          <Alert
            title="Validation Errors"
            description={
              <ul className="list-disc pl-4 m-0">
                {validationResult.errors?.map((err, i) => (
                  <li 
                    key={i} 
                    className="cursor-pointer hover:underline text-red-600 hover:text-red-800 transition-colors" 
                    onClick={() => {
                      // Try to extract field name from error message (e.g. "Missing params")
                      const fieldMatch = err.match(/parameters|params|rule_type/i);
                      if (fieldMatch) {
                         onJumpToField?.(fieldMatch[0] === 'rule_type' ? 'rule_type' : 'params');
                      } else {
                         onJumpToField?.('params'); // default jump
                      }
                    }}
                  >
                    {err} <span className="text-xs ml-1 opacity-60">(click to locate)</span>
                  </li>
                ))}
              </ul>
            }
            type="error"
            showIcon
            className="mb-4"
          />
        )}
        
        {validationResult.evidence && (
          <div>
            <Divider className="my-3" />
            <Text strong className="block mb-2 text-gray-600">Evidence:</Text>
            <pre className="bg-gray-100 p-3 rounded-md overflow-x-auto text-xs font-mono text-gray-700">
              {JSON.stringify(validationResult.evidence, null, 2)}
            </pre>
          </div>
        )}
      </Card>
    );
  };

  const renderDiffSummary = () => {
    if (loading) {
      return <div className="flex justify-center py-10"><Spin /></div>;
    }
    
    if (!diffData) {
      return <Empty description="No diff data available" />;
    }

    return (
      <div className="space-y-4">
        {/* Added Rules */}
        {diffData.added_rules?.length > 0 && (
          <Card size="small" title={<span className="text-green-600 flex items-center gap-2"><Plus size={14} /> Added ({diffData.added_rules.length})</span>} className="border-green-200 bg-green-50 shadow-sm">
            <ul className="list-disc pl-5 m-0 text-sm text-green-800">
              {diffData.added_rules.map((rule: any, i: number) => (
                <li key={i}>{rule.name || rule.id} <Tag className="ml-2" color="green">{rule.type}</Tag></li>
              ))}
            </ul>
          </Card>
        )}

        {/* Removed Rules */}
        {diffData.removed_rules?.length > 0 && (
          <Card size="small" title={<span className="text-red-600 flex items-center gap-2"><Minus size={14} /> Removed ({diffData.removed_rules.length})</span>} className="border-red-200 bg-red-50 shadow-sm">
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
                  header={
                    <div 
                      className="flex items-center justify-between w-full hover:bg-orange-100 px-2 rounded cursor-pointer group"
                      onClick={(e) => {
                        e.stopPropagation();
                        onJumpToRule?.(rule.rule_id);
                      }}
                    >
                      <Text strong className="text-orange-700">{rule.rule_id}</Text>
                      <FileSearch size={14} className="text-orange-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </div>
                  } 
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
    );
  };

  const renderVersionMeta = () => {
    // Attempt to extract metadata from diffData or validationResult if available? No, wait. 
    // We don't have versionMeta data directly in RightPanelProps.
    // The App.ts doesn't fetch or pass versionMeta to RightPanel right now.
    // It's a bit larger change than a 1-line string replace, because we'd need to fetch or pass the meta.
    // I'll skip changing it and just write it down in the Next Actions!
    return (
      <Card className="shadow-sm border-gray-200">
        <Alert title="Viewing Historical Version" type="info" showIcon className="mb-4" />
        <Button block type="primary" icon={<GitCommit size={16} />} onClick={onRequestDiff}>
          View Full Diff Analysis
        </Button>
      </Card>
    );
  };

  const getTitleIcon = () => {
    switch (mode) {
      case 'help': return <HelpCircle size={20} className="text-blue-600" />;
      case 'validation': return <CheckCircle size={20} className="text-blue-600" />;
      case 'diff_summary': return <GitCommit size={20} className="text-blue-600" />;
      case 'version_meta': return <Archive size={20} className="text-blue-600" />;
      case 'publish_check': return <UploadCloud size={20} className="text-blue-600" />;
      default: return <HelpCircle size={20} className="text-blue-600" />;
    }
  };

  const getTitleText = () => {
    switch (mode) {
      case 'help': return 'Assistant / Help';
      case 'validation': return 'Validation Results';
      case 'diff_summary': return 'Baseline Diff Summary';
      case 'version_meta': return 'Version Info';
      case 'publish_check': return 'Publish Check';
      default: return 'Assistant';
    }
  };

  return (
    <div className="h-full bg-white flex flex-col p-4">
      <div className="flex items-center space-x-2 mb-6 pb-2 border-b border-gray-100">
        {getTitleIcon()}
        <Title level={5} className="!m-0">{getTitleText()}</Title>
      </div>

      <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar">
        {mode === 'help' && renderHelp()}
        {mode === 'validation' && renderValidation()}
        {mode === 'diff_summary' && renderDiffSummary()}
        {mode === 'version_meta' && renderVersionMeta()}
      </div>
    </div>
  );
};

export default RightPanel;
