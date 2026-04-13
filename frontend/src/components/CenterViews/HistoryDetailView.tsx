import React, { useEffect, useState } from 'react';
import { Card, Typography, Button, Descriptions, Tag, Space, Spin, message } from 'antd';
import { Archive, GitCommit, RotateCcw } from 'lucide-react';
import { rulesApi } from '../../api';
import { VersionMetaDTO } from '../../types/dto';

const { Title } = Typography;

interface HistoryDetailViewProps {
  baselineId?: string;
  versionId?: string;
  onRequestDiff: () => void;
  onRequestRollback: () => void;
}

const HistoryDetailView: React.FC<HistoryDetailViewProps> = ({
  baselineId,
  versionId,
  onRequestDiff,
  onRequestRollback
}) => {
  const [loading, setLoading] = useState(false);
  const [meta, setMeta] = useState<VersionMetaDTO | null>(null);

  useEffect(() => {
    if (baselineId && versionId && versionId !== 'draft') {
      setLoading(true);
      rulesApi.getVersionMeta(baselineId, versionId)
        .then(data => {
          setMeta(data);
        })
        .catch(err => {
          console.error("Failed to load version meta", err);
          message.error("Failed to load version metadata");
        })
        .finally(() => {
          setLoading(false);
        });
    }
  }, [baselineId, versionId]);

  if (loading) {
    return (
      <div className="h-full flex items-center justify-center bg-gray-50">
        <Spin size="large" />
      </div>
    );
  }

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
            <Tag color="blue">{meta?.version_label || versionId || 'Unknown'}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Status">
            <Tag color="green">PUBLISHED</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Published At">
            {meta?.published_at ? new Date(meta.published_at).toLocaleString() : 'Unknown'}
          </Descriptions.Item>
          <Descriptions.Item label="Operator">
            {meta?.publisher || 'System'}
          </Descriptions.Item>
          <Descriptions.Item label="Summary" span={2}>
            {meta?.summary || 'No summary available for this version.'}
          </Descriptions.Item>
        </Descriptions>
      </Card>
    </div>
  );
};

export default HistoryDetailView;
