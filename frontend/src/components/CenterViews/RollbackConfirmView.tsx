import React from 'react';
import { Card, Typography, Button, Space, Alert, Spin, Divider } from 'antd';
import { RotateCcw, AlertTriangle } from 'lucide-react';
import { DiffSourceTargetDTO, DiffFieldChangeDTO } from '../../types/dto';

const { Title, Text } = Typography;

interface RollbackConfirmViewProps {
  versionId?: string;
  rollbackEffectDiff?: DiffSourceTargetDTO | null;
  loadingRollbackEffectDiff?: boolean;
  onRollbackConfirmRequest: () => void;
  onCancelRollback: () => void;
}

const RollbackConfirmView: React.FC<RollbackConfirmViewProps> = ({
  versionId,
  rollbackEffectDiff,
  loadingRollbackEffectDiff,
  onRollbackConfirmRequest,
  onCancelRollback
}) => {
  const diffData = rollbackEffectDiff;
  const addedRules = diffData?.rules.filter(r => r.change_type === 'added') || [];
  const removedRules = diffData?.rules.filter(r => r.change_type === 'removed') || [];
  const modifiedRules = diffData?.rules.filter(r => r.change_type === 'modified') || [];

  return (
    <div className="h-full flex flex-col items-center justify-center bg-gray-50">
      <Card className="w-full max-w-lg shadow-lg border-orange-200 rounded-xl overflow-hidden p-6 text-center bg-orange-50/30">
        <RotateCcw size={48} className="text-orange-500 mx-auto mb-4" />
        <Title level={3} className="!m-0 mb-2 text-gray-800">Confirm Rollback</Title>
        
        <Alert
          message="Rollback Action Warning"
          description={
            <div>
              You are about to rollback to version <Text strong className="text-blue-600">{versionId}</Text>.
              <br/><br/>
              This will <b>NOT</b> immediately publish the old rules. Instead, it will <b>generate a new Draft</b> based on the contents of version {versionId}. You can review and edit it before publishing.
            </div>
          }
          type="warning"
          showIcon
          icon={<AlertTriangle size={20} />}
          className="mb-6 text-left"
        />

        <Divider className="my-4" />
        <div className="text-left">
          <Text strong className="text-gray-700">Rollback Effect Preview</Text>
          <div className="mt-3">
            {loadingRollbackEffectDiff ? (
              <div className="flex justify-center py-6">
                <Spin />
              </div>
            ) : !diffData ? (
              <Text type="secondary">No rollback preview available.</Text>
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
            Create Rollback Draft
          </Button>
        </Space>
      </Card>
    </div>
  );
};

export default RollbackConfirmView;
