import React, { useEffect, useState } from 'react';
import { Card, Typography, Button, Space, Alert, Spin, Table, Tag } from 'antd';
import { RotateCcw, AlertTriangle } from 'lucide-react';
import { rulesApi } from '../../api';
import { DiffSourceTargetDTO } from '../../types/dto';

const { Title, Text } = Typography;

interface RollbackConfirmViewProps {
  baselineId?: string;
  versionId?: string;
  onRollbackConfirmRequest: () => void;
  onCancelRollback: () => void;
}

const RollbackConfirmView: React.FC<RollbackConfirmViewProps> = ({
  baselineId,
  versionId,
  onRollbackConfirmRequest,
  onCancelRollback
}) => {
  const [loading, setLoading] = useState(false);
  const [diffData, setDiffData] = useState<DiffSourceTargetDTO | null>(null);

  useEffect(() => {
    if (baselineId && versionId) {
      setLoading(true);
      // Compare the historical version against the current production version
      rulesApi.getBaselineDiff(baselineId, versionId, 'previous_version')
        .then(data => setDiffData(data))
        .catch(err => console.error("Failed to load diff for rollback", err))
        .finally(() => setLoading(false));
    }
  }, [baselineId, versionId]);

  const columns = [
    {
      title: 'Rule ID',
      dataIndex: 'rule_id',
      key: 'rule_id',
    },
    {
      title: 'Action',
      dataIndex: 'change_type',
      key: 'change_type',
      render: (type: string) => {
        const color = type === 'added' ? 'green' : type === 'removed' ? 'red' : 'orange';
        return <Tag color={color}>{type.toUpperCase()}</Tag>;
      }
    }
  ];

  return (
    <div className="h-full flex flex-col p-6 bg-gray-50 overflow-y-auto">
      <div className="flex flex-col items-center justify-center mb-6">
        <RotateCcw size={48} className="text-orange-500 mx-auto mb-4" />
        <Title level={3} className="!m-0 mb-2 text-gray-800">Confirm Rollback</Title>

        <Alert
          message="Rollback Action Warning"
          description={
            <div>
              You are about to rollback to version <Text strong className="text-blue-600">{versionId}</Text>.
              <br/>
              This will <b>NOT</b> immediately publish the old rules. Instead, it will <b>generate a new Draft</b> based on the contents of version {versionId}. You can review and edit it before publishing.
            </div>
          }
          type="warning"
          showIcon
          icon={<AlertTriangle size={20} />}
          className="mb-6 w-full max-w-2xl text-left"
        />

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
      </div>

      {loading ? (
        <div className="flex justify-center p-8"><Spin /></div>
      ) : diffData ? (
        <Card className="w-full max-w-4xl mx-auto shadow-sm border-gray-200 rounded-lg">
          <Title level={5}>Changes to be applied (Current Prod &rarr; Version {versionId})</Title>
          <Text type="secondary" className="block mb-4">
            {diffData.human_readable_summary || 
             `Added: ${diffData.diff_summary.added}, Removed: ${diffData.diff_summary.removed}, Modified: ${diffData.diff_summary.modified}`}
          </Text>
          <Table 
            dataSource={diffData.rules} 
            columns={columns} 
            rowKey="rule_id"
            pagination={{ pageSize: 10 }}
            size="small"
          />
        </Card>
      ) : null}
    </div>
  );
};

export default RollbackConfirmView;
