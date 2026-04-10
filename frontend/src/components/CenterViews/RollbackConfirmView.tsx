import React from 'react';
import { Card, Typography, Button, Space, Alert } from 'antd';
import { RotateCcw, AlertTriangle } from 'lucide-react';

const { Title, Text } = Typography;

interface RollbackConfirmViewProps {
  versionId?: string;
  onRollbackConfirmRequest: () => void;
  onCancelRollback: () => void;
}

const RollbackConfirmView: React.FC<RollbackConfirmViewProps> = ({
  versionId,
  onRollbackConfirmRequest,
  onCancelRollback
}) => {
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
