import React from 'react';
import { Card, Typography, Button, Space, Alert } from 'antd';
import { UploadCloud, CheckCircle } from 'lucide-react';
import { ValidationResult } from '../../api/rules';

const { Title, Text } = Typography;

interface PublishConfirmViewProps {
  validationResult: ValidationResult | null;
  publishing: boolean;
  onPublishConfirmRequest: () => void;
  onCancelPublish: () => void;
}

const PublishConfirmView: React.FC<PublishConfirmViewProps> = ({
  validationResult,
  publishing,
  onPublishConfirmRequest,
  onCancelPublish
}) => {
  return (
    <div className="h-full flex flex-col items-center justify-center bg-gray-50">
      <Card className="w-full max-w-lg shadow-lg border-gray-200 rounded-xl overflow-hidden p-6 text-center">
        <UploadCloud size={48} className="text-blue-500 mx-auto mb-4" />
        <Title level={3} className="!m-0 mb-2 text-gray-800">Ready to Publish</Title>
        <Text type="secondary" className="block mb-6">
          You are about to publish the current draft as a new baseline version. 
          This action will create a new snapshot and may affect downstream systems.
        </Text>

        {validationResult?.valid ? (
          <Alert
            message="Pre-flight checks passed"
            description="The rule draft is valid and ready to be deployed."
            type="success"
            showIcon
            icon={<CheckCircle size={20} />}
            className="mb-6 text-left"
          />
        ) : (
          <Alert
            message="Pre-flight checks failed"
            description="The rule draft has validation errors. Please return to edit mode and fix them before publishing."
            type="error"
            showIcon
            className="mb-6 text-left"
          />
        )}

        <Space size="large" className="mt-4">
          <Button size="large" onClick={onCancelPublish}>
            Back to Edit
          </Button>
          <Button 
            type="primary" 
            size="large" 
            icon={<UploadCloud size={16} />}
            onClick={onPublishConfirmRequest}
            loading={publishing}
            disabled={!validationResult?.valid}
            className="bg-green-600 hover:bg-green-500 border-green-600"
          >
            Confirm Publish
          </Button>
        </Space>
      </Card>
    </div>
  );
};

export default PublishConfirmView;
