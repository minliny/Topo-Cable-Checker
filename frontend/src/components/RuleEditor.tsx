import React, { useEffect } from 'react';
import { Form, Input, Button, Select, Card, Typography, Empty, Space } from 'antd';
import { Play, UploadCloud, FileCode, Save } from 'lucide-react';
import { CenterMode, DraftData } from '../types/ui';

const { Option } = Select;
const { TextArea } = Input;
const { Title, Text } = Typography;

interface RuleEditorProps {
  mode: CenterMode;
  draftData: DraftData;
  onChange: (data: DraftData) => void;
  onDirtyChange: (dirty: boolean) => void;
  onValidate: () => void;
  onSaveDraft: () => void;
  onPublish: () => void;
  validating: boolean;
  publishing: boolean;
  saving: boolean;
  validationPassed: boolean;
  dirty: boolean;
}

const RuleEditor: React.FC<RuleEditorProps> = ({
  mode,
  draftData,
  onChange,
  onDirtyChange,
  onValidate,
  onSaveDraft,
  onPublish,
  validating,
  publishing,
  saving,
  validationPassed,
  dirty,
}) => {
  const [form] = Form.useForm();

  // Sync form with external draftData when it mounts or changes externally
  useEffect(() => {
    const activeRuleId = draftData.active_rule_id;
    const ruleDef = activeRuleId ? draftData.rule_set?.[activeRuleId] : null;
    if (ruleDef) {
      form.setFieldsValue({
        rule_type: ruleDef.template || ruleDef.rule_type || 'threshold',
        params: typeof ruleDef.params === 'string' ? ruleDef.params : JSON.stringify(ruleDef.params || {}, null, 2),
      });
    } else {
      form.setFieldsValue({
        rule_type: 'threshold',
        params: '{\n  \n}',
      });
    }
  }, [draftData, form]);

  const handleValuesChange = (_changedValues: any, allValues: any) => {
    const activeRuleId = draftData.active_rule_id || 'new_rule';
    const existingRule = draftData.rule_set?.[activeRuleId] || {};
    
    let parsedParams = allValues.params;
    try {
      parsedParams = JSON.parse(allValues.params);
    } catch(e) {}

    const newDraftData: DraftData = {
      ...draftData,
      active_rule_id: activeRuleId,
      rule_set: {
        ...(draftData.rule_set || {}),
        [activeRuleId]: {
          ...existingRule,
          template: allValues.rule_type,
          rule_type: 'template',
          params: parsedParams
        }
      }
    };
    
    onChange(newDraftData);
    onDirtyChange(true);
  };

  if (mode === 'empty') {
    return (
      <div className="h-full flex items-center justify-center">
        <Empty description="Select a baseline to start editing rules" />
      </div>
    );
  }

  // Future expansion: diff view or history_detail view can be added here
  // if (mode === 'diff') return <DiffMainView />
  
  return (
    <div className="h-full flex flex-col">
      <div className="mb-6 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <FileCode size={24} className="text-blue-600" />
          <Title level={4} className="!m-0">
            {mode === 'edit' ? 'Edit Rule Draft' : 'Edit Rule Draft'}
          </Title>
          {dirty && <Text type="warning" className="ml-2">(Unsaved Changes)</Text>}
        </div>
        
        <Space>
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
            onClick={onValidate}
            loading={validating}
            className="flex items-center"
          >
            Validate
          </Button>
          <Button
            icon={<UploadCloud size={16} />}
            onClick={onPublish}
            loading={publishing}
            disabled={!validationPassed && !dirty} // Allow if valid or we bypass it, adjust as needed
            className="flex items-center bg-green-50 text-green-700 border-green-200 hover:bg-green-100"
          >
            Publish
          </Button>
        </Space>
      </div>

      <Card className="shadow-sm border-gray-200 rounded-lg flex-1 overflow-hidden flex flex-col">
        <Form
          form={form}
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
              className="font-mono text-sm bg-gray-50 flex-1 h-full resize-none min-h-[300px]"
              placeholder='{"key": "value"}'
            />
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default RuleEditor;
