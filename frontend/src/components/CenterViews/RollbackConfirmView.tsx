import React from 'react';
import { Card, Typography, Button, Space, Alert, Spin, Divider, Collapse, Tag } from 'antd';
import { RotateCcw, AlertTriangle } from 'lucide-react';
import { DiffSourceTargetDTO, DiffFieldChangeDTO, BaselineVersionRuleSetDTO } from '../../types/dto';

const { Title, Text } = Typography;
const { Panel } = Collapse;

interface RollbackConfirmViewProps {
  versionId?: string;
  rollbackEffectDiff?: DiffSourceTargetDTO | null;
  loadingRollbackEffectDiff?: boolean;
  targetRuleSet?: BaselineVersionRuleSetDTO | null;
  loadingTargetRuleSet?: boolean;
  targetRuleSetError?: string | null;
  onRollbackConfirmRequest: () => void;
  onCancelRollback: () => void;
}

const RollbackConfirmView: React.FC<RollbackConfirmViewProps> = ({
  versionId,
  rollbackEffectDiff,
  loadingRollbackEffectDiff,
  targetRuleSet,
  loadingTargetRuleSet,
  targetRuleSetError,
  onRollbackConfirmRequest,
  onCancelRollback
}) => {
  const diffData = rollbackEffectDiff;
  const addedRules = diffData?.rules.filter(r => r.change_type === 'added') || [];
  const removedRules = diffData?.rules.filter(r => r.change_type === 'removed') || [];
  const modifiedRules = diffData?.rules.filter(r => r.change_type === 'modified') || [];
  const currentVersionId = diffData?.source_version_id;
  const targetRuleEntries = targetRuleSet?.rule_set ? Object.entries(targetRuleSet.rule_set) : [];

  return (
    <div className="h-full flex flex-col items-center justify-center bg-gray-50">
      <Card className="w-full max-w-3xl shadow-lg border-orange-200 rounded-xl overflow-hidden p-6 text-center bg-orange-50/30">
        <RotateCcw size={48} className="text-orange-500 mx-auto mb-4" />
        <Title level={3} className="!m-0 mb-2 text-gray-800">Restore Historical Version to Draft</Title>
        
        <Alert
          message="Restore to Draft"
          description={
            <div>
              You are about to load version <Text strong className="text-blue-600">{versionId}</Text> into the draft editor.
              <br/><br/>
              This will <b>NOT</b> change the published baseline immediately. It will <b>restore that historical rule set into the current draft</b> so you can review, edit, save, and publish it as a new version.
            </div>
          }
          type="warning"
          showIcon
          icon={<AlertTriangle size={20} />}
          className="mb-6 text-left"
        />

        <div className="text-left mb-4">
          <div className="flex items-center gap-2 flex-wrap">
            <Text strong className="text-gray-700">Current Production:</Text>
            <Tag color="blue">{currentVersionId || 'Unknown'}</Tag>
            <Text strong className="text-gray-700 ml-2">Target Version:</Text>
            <Tag color="purple">{versionId || 'Unknown'}</Tag>
          </div>
        </div>

        <Divider className="my-4" />
        <div className="text-left">
          <Text strong className="text-gray-700">Restore Effect Preview</Text>
          <div className="mt-3">
            {loadingRollbackEffectDiff ? (
              <div className="flex justify-center py-6">
                <Spin />
              </div>
            ) : !diffData ? (
              <Text type="secondary">No restore preview available.</Text>
            ) : (
              <div className="space-y-3">
                {diffData.human_readable_summary && (
                  <div className="p-2 bg-blue-50 border border-blue-200 rounded text-sm text-blue-800">
                    {diffData.human_readable_summary}
                  </div>
                )}

                <div className="grid grid-cols-3 gap-2 text-center">
                  <div className="p-2 bg-green-50 border border-green-200 rounded">
                    <div className="text-xs uppercase tracking-wider text-green-700">Added</div>
                    <div className="text-lg font-semibold text-green-800">{addedRules.length}</div>
                  </div>
                  <div className="p-2 bg-red-50 border border-red-200 rounded">
                    <div className="text-xs uppercase tracking-wider text-red-700">Removed</div>
                    <div className="text-lg font-semibold text-red-800">{removedRules.length}</div>
                  </div>
                  <div className="p-2 bg-orange-50 border border-orange-200 rounded">
                    <div className="text-xs uppercase tracking-wider text-orange-700">Modified</div>
                    <div className="text-lg font-semibold text-orange-800">{modifiedRules.length}</div>
                  </div>
                </div>

                {addedRules.length > 0 && (
                  <div className="p-2 bg-green-50 border border-green-200 rounded">
                    <Text strong className="text-green-800">Added</Text>
                    <ul className="list-disc pl-5 m-0 text-sm text-green-800">
                      {addedRules.map(r => (
                        <li key={r.rule_id}>{r.rule_id}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {removedRules.length > 0 && (
                  <div className="p-2 bg-red-50 border border-red-200 rounded">
                    <Text strong className="text-red-800">Removed</Text>
                    <ul className="list-disc pl-5 m-0 text-sm text-red-800">
                      {removedRules.map(r => (
                        <li key={r.rule_id}>{r.rule_id}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {modifiedRules.length > 0 && (
                  <div className="p-2 bg-orange-50 border border-orange-200 rounded">
                    <Text strong className="text-orange-800">Modified</Text>
                    <div className="mt-2 space-y-2">
                      {modifiedRules.map(r => (
                        <div key={r.rule_id} className="bg-white border border-orange-100 rounded p-2">
                          <Text strong className="text-orange-800">{r.rule_id}</Text>
                          {(r.field_changes && r.field_changes.length > 0) && (
                            <div className="mt-1 space-y-1">
                              {r.field_changes.map((fc: DiffFieldChangeDTO) => (
                                <div key={fc.field_name} className="text-xs font-mono flex items-center flex-wrap">
                                  <span className="text-gray-500 w-40 truncate" title={fc.field_name}>{fc.field_name}:</span>
                                  <span className="text-red-500 line-through mr-2">{JSON.stringify(fc.old_value)}</span>
                                  <span className="text-gray-400 mx-1">→</span>
                                  <span className="text-green-600 ml-2">{JSON.stringify(fc.new_value)}</span>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        <Divider className="my-4" />
        <div className="text-left">
          <Text strong className="text-gray-700">Target Rule Set Preview</Text>
          <div className="mt-3">
            {loadingTargetRuleSet ? (
              <div className="flex justify-center py-6">
                <Spin />
              </div>
            ) : targetRuleSetError ? (
              <Alert message={targetRuleSetError} type="error" showIcon />
            ) : !targetRuleSet ? (
              <Text type="secondary">No target rule_set available.</Text>
            ) : (
              <div>
                <div className="mb-2">
                  <Text type="secondary">Total rules: {targetRuleEntries.length}</Text>
                </div>
                <Collapse className="bg-white">
                  {targetRuleEntries.map(([ruleId, ruleDef]) => {
                    const template = (ruleDef as any)?.template || (ruleDef as any)?.rule_type || 'rule';
                    const params = (ruleDef as any)?.params || {};
                    const paramKeys = (params && typeof params === 'object' && !Array.isArray(params)) ? Object.keys(params) : [];
                    const severity = (ruleDef as any)?.severity;
                    return (
                      <Panel
                        key={ruleId}
                        header={
                          <div className="flex items-center gap-2 flex-wrap">
                            <Text strong>{ruleId}</Text>
                            <Tag>{String(template)}</Tag>
                            {severity && <Tag color="orange">{String(severity)}</Tag>}
                            {paramKeys.length > 0 && (
                              <Text type="secondary" className="text-xs">
                                params: {paramKeys.slice(0, 6).join(', ')}{paramKeys.length > 6 ? '…' : ''}
                              </Text>
                            )}
                          </div>
                        }
                      >
                        <pre className="text-xs bg-gray-50 p-3 rounded border border-gray-200 overflow-x-auto font-mono">
                          {JSON.stringify(ruleDef, null, 2)}
                        </pre>
                      </Panel>
                    );
                  })}
                </Collapse>
              </div>
            )}
          </div>
        </div>

        <Space size="large" className="mt-4">
          <Button size="large" onClick={onCancelRollback}>
            Cancel
          </Button>
          <Button 
            type="primary" 
            danger
            size="large" 
            icon={<RotateCcw size={16} />}
            onClick={onRollbackConfirmRequest}
            className="flex items-center"
          >
            Restore to Draft
          </Button>
        </Space>
      </Card>
    </div>
  );
};

export default RollbackConfirmView;
