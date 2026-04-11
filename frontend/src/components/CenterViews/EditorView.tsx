import React, { useEffect, useRef } from 'react';
import { Form, Input, Button, Select, Card, Typography, Space, FormInstance } from 'antd';
import { Play, UploadCloud, FileCode, Save, Trash2 } from 'lucide-react';
import { DraftData } from '../types/ui';

const { Option } = Select;
const { TextArea } = Input;
const { Title, Text } = Typography;

interface EditorViewProps {
  draftData: DraftData;
  dirty: boolean;
  validating: boolean;
  validationPassed: boolean;
  saving: boolean;
  targetFieldPath?: string;
  isRollbackCandidate?: boolean;
  onChange: (data: DraftData) => void;
  onDirtyChange: (dirty: boolean) => void;
  onValidateRequest: () => void;
  onSaveDraft: () => void;
  onPublishConfirmRequest: () => void;
  onDiscardRollbackCandidate?: () => void;
}

const EditorView: React.FC<EditorViewProps> = ({
  draftData,
  dirty,
  validating,
  validationPassed,
  saving,
  targetFieldPath,
  isRollbackCandidate,
  onChange,
  onDirtyChange,
  onValidateRequest,
  onSaveDraft,
  onPublishConfirmRequest,
  onDiscardRollbackCandidate
}) => {
  const [form] = Form.useForm();
  const formRef = useRef<FormInstance>(null);

  // Sync external draft data to form
  useEffect(() => {
    form.setFieldsValue({
      rule_type: draftData.rule_type || 'threshold',
      params: draftData.params || '',
    });
  }, [draftData, form]);

  // Scroll to target field if requested
  useEffect(() => {
    if (targetFieldPath) {
      // First attempt to use Ant Design's native scrollToField
      try {
        form.scrollToField(targetFieldPath, { behavior: 'smooth', block: 'center' });
      } catch (e) {
        // Ignore native error if field is not registered natively
      }
      
      // Fallback: Manually try to scroll to the DOM element representing the field 
      // Antd usually prefixes id with the form name or directly uses the field path as id
      // Since our main inputs are "rule_type" and "params", we can target those IDs.
      const elementId = targetFieldPath.includes('.') 
        ? targetFieldPath.split('.')[0]  // "params.threshold" -> "params"
        : targetFieldPath;
        
      const domEl = document.getElementById(elementId) || document.querySelector(`[data-field-path="${elementId}"]`);
      
      if (domEl) {
        domEl.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        // Add a temporary highlight flash effect
        const parentItem = domEl.closest('.ant-form-item');
        if (parentItem) {
          parentItem.classList.add('ring-2', 'ring-red-400', 'ring-offset-2', 'transition-all', 'duration-300');
          setTimeout(() => {
            parentItem.classList.remove('ring-2', 'ring-red-400', 'ring-offset-2');
          }, 1500);
        }
      }
    }
  }, [targetFieldPath, form]);

  const handleValuesChange = (_changedValues: any, allValues: any) => {
    onChange(allValues);
    onDirtyChange(true);
  };

  return (
    <div className="h-full flex flex-col">
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FileCode size={24} className="text-blue-600" />
          <Title level={4} className="!m-0">
            {isRollbackCandidate ? 'Review Rollback Candidate' : 'Edit Rule Draft'}
          </Title>
          {dirty && <Text type="warning" className="ml-2">(Unsaved Changes)</Text>}
          {isRollbackCandidate && (
            <span className="text-purple-600 bg-purple-50 px-2 py-0.5 rounded text-xs ml-2 border border-purple-100">
              Rollback Candidate
            </span>
          )}
        </div>
        
        <Space>
          {isRollbackCandidate && (
             <Button 
               danger 
               icon={<Trash2 size={16} />} 
               onClick={onDiscardRollbackCandidate}
             >
               Discard Candidate
             </Button>
          )}
          <Button 
            icon={<Save size={16} />} 
            onClick={onSaveDraft}
            loading={saving}
            disabled={!dirty}
            className="flex items-center"
          >
            Save Draft
          </Button>
          <Button
            type="primary"
            icon={<Play size={16} />}
            onClick={onValidateRequest}
            loading={validating}
            className="flex items-center"
          >
            Validate
          </Button>
          <Button
            icon={<UploadCloud size={16} />}
            onClick={onPublishConfirmRequest}
            disabled={!validationPassed && !dirty}
            className="flex items-center bg-green-50 text-green-700 border-green-200 hover:bg-green-100"
          >
            Prepare Publish
          </Button>
        </Space>
      </div>

      <Card className="shadow-sm border-gray-200 rounded-lg flex-1 overflow-hidden flex flex-col">
        <Form
          form={form}
          ref={formRef}
          layout="vertical"
          onValuesChange={handleValuesChange}
          className="flex flex-col h-full"
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
            className="flex-1 flex flex-col mb-0"
            wrapperCol={{ className: 'flex-1' }}
          >
            <TextArea
              className={`font-mono text-sm bg-gray-50 flex-1 h-full resize-none min-h-[300px] transition-all duration-300 ${
                targetFieldPath === 'params' ? 'border-red-500 shadow-[0_0_0_2px_rgba(239,68,68,0.2)]' : ''
              }`}
              placeholder='{"key": "value"}'
            />
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default EditorView;
