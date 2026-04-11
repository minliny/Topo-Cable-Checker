import React from 'react';
import { Card, Typography, Button, Descriptions, Tag, Space } from 'antd';
import { Archive, GitCommit, RotateCcw } from 'lucide-react';

const { Title } = Typography;

interface HistoryDetailViewProps {
  versionId?: string;
  onRequestDiff: () => void;
  onRequestRollback: () => void;
}

const HistoryDetailView: React.FC<HistoryDetailViewProps> = ({
  versionId,
  onRequestDiff,
  onRequestRollback
}) => {
  return (
    <div className="h-full flex flex-col p-6 bg-gray-50">
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Archive size={24} className="text-green-600" />
          <Title level={4} className="!m-0">Historical Version Details</Title>
        </div>
        <Space>
          <Button icon={<GitCommit size={16} />} onClick={onRequestDiff}>
            Compare Changes
          </Button>
          <Button 
            danger 
            icon={<RotateCcw size={16} />} 
            onClick={onRequestRollback}
            className="flex items-center"
          >
            Rollback to this version
          </Button>
        </Space>
      </div>

      <Card className="shadow-sm border-gray-200 rounded-lg">
        <Descriptions title="Version Metadata" bordered column={2}>
          <Descriptions.Item label="Version Number">
            <Tag color="blue">{versionId || 'Unknown'}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Status">
            <Tag color="green">PUBLISHED</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Published At">
            2026-04-10 10:00:00 (Mock)
          </Descriptions.Item>
          <Descriptions.Item label="Operator">
            admin@system.local
          </Descriptions.Item>
          <Descriptions.Item label="Summary" span={2}>
            This version contains major updates to the threshold limits and pattern matching regular expressions.
          </Descriptions.Item>
        </Descriptions>
      </Card>
    </div>
  );
};

export default HistoryDetailView;
