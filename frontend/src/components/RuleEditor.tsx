import React, { useState } from 'react';
import { Form, Input, Button, Select, Card, Alert, message, Typography, Divider, Space } from 'antd';
import { rulesApi, ValidationResult } from '../api/rules';
import { Play, UploadCloud, FileCode } from 'lucide-react';

const { Option } = Select;
const { TextArea } = Input;
const { Title, Text } = Typography;

interface RuleEditorProps {
  baselineId?: string;
  onPublished?: () => void;
}

const RuleEditor: React.FC<RuleEditorProps> = ({ baselineId, onPublished }) => {
  const [form] = Form.useForm();
  const [validating, setValidating] = useState(false);
  const [publishing, setPublishing] = useState(false);
  const [validationResult, setValidationResult] = useState<ValidationResult | null>(null);

  const handleValidate = async () => {
    try {
      const values = await form.validateFields();
      setValidating(true);
      setValidationResult(null);

      let parsedParams = {};
      try {
        parsedParams = JSON.parse(values.params || '{}');
      } catch (err) {
        message.error('Params must be valid JSON');
        setValidating(false);
        return;
      }

      const res = await rulesApi.validateDraft({
        rule_type: values.rule_type,
        params: parsedParams,
      });

      setValidationResult(res.validation_result);
      if (res.validation_result.valid) {
        message.success('Validation passed!');
      } else {
        message.error('Validation failed');
      }
    } catch (error: any) {
      if (error.errorFields) {
        // Form validation error, ignore
        return;
      }
      message.error('Error during validation');
      console.error(error);
    } finally {
      setValidating(false);
    }
  };

  const handlePublish = async () => {
    if (!baselineId) {
      message.warning('Please select a baseline first');
      return;
    }

    try {
      setPublishing(true);
      const res = await rulesApi.publishRules(baselineId);
      message.success(`Published version ${res.version}: ${res.summary}`);
      if (onPublished) {
        onPublished();
      }
      // Reset after publish
      setValidationResult(null);
      form.resetFields();
    } catch (error) {
      message.error('Failed to publish rules');
      console.error(error);
    } finally {
      setPublishing(false);
    }
  };

  return (
    <div className="h-full bg-gray-50 flex flex-col p-6 overflow-y-auto">
      <div className="mb-6 flex items-center gap-2">
        <FileCode size={24} className="text-blue-600" />
        <Title level={4} className="!m-0">Rule Editor</Title>
      </div>

      <Card className="shadow-sm border-gray-200 rounded-lg mb-6">
        <Form
          form={form}
          layout="vertical"
          initialValues={{
            rule_type: 'threshold',
            params: '{\n  "threshold": 10,\n  "severity": "warning"\n}'
          }}
        >
          <Form.Item
            name="rule_type"
            label={<Text strong>Rule Type</Text>}
            rules={[{ required: true, message: 'Please select a rule type' }]}
          >
            <Select placeholder="Select rule type">
              <Option value="threshold">Threshold</Option>
              <Option value="pattern">Pattern Match</Option>
              <Option value="topology">Topology</Option>
              <Option value="consistency">Group Consistency</Option>
            </Select>
          </Form.Item>

          <Form.Item
            name="params"
            label={<Text strong>Parameters (JSON)</Text>}
            rules={[{ required: true, message: 'Please input rule parameters' }]}
          >
            <TextArea
              rows={8}
              className="font-mono text-sm bg-gray-50"
              placeholder='{"key": "value"}'
            />
          </Form.Item>

          <div className="flex gap-4 pt-2">
            <Button
              type="primary"
              icon={<Play size={16} />}
              onClick={handleValidate}
              loading={validating}
              className="flex items-center"
            >
              Validate Draft
            </Button>
            <Button
              icon={<UploadCloud size={16} />}
              onClick={handlePublish}
              loading={publishing}
              disabled={!validationResult?.valid}
              className="flex items-center"
            >
              Publish to Baseline
            </Button>
          </div>
        </Form>
      </Card>

      {validationResult && (
        <Card title="Validation Result" size="small" className="shadow-sm border-gray-200">
          {validationResult.valid ? (
            <Alert
              message="Rule is valid"
              type="success"
              showIcon
              className="mb-4"
            />
          ) : (
            <Alert
              message="Validation Errors"
              description={
                <ul className="list-disc pl-4 m-0">
                  {validationResult.errors?.map((err, i) => (
                    <li key={i}>{err}</li>
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
      )}
    </div>
  );
};

export default RuleEditor;
