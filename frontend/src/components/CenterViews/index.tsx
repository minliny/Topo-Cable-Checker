import React from 'react';
import { CenterMode, DraftData } from '../../types/ui';
import { ValidationResult, DiffResponse } from '../../api/rules';
import { Empty } from 'antd';
import EditorView from './EditorView';
import DiffView from './DiffView';
import PublishConfirmView from './PublishConfirmView';

interface CenterContainerProps {
  mode: CenterMode;
  draftData: DraftData;
  dirty: boolean;
  validating: boolean;
  saving: boolean;
  publishing: boolean;
  validationPassed: boolean;
  validationResult: ValidationResult | null;
  diffData: DiffResponse | null;
  targetFieldPath?: string;
  targetRuleId?: string;
  onChange: (data: DraftData) => void;
  onDirtyChange: (dirty: boolean) => void;
  onValidateRequest: () => void;
  onSaveDraft: () => void;
  onPublishConfirmRequest: () => void;
  onCancelPublish: () => void;
}

const CenterContainer: React.FC<CenterContainerProps> = ({
  mode,
  draftData,
  dirty,
  validating,
  saving,
  publishing,
  validationPassed,
  validationResult,
  diffData,
  targetFieldPath,
  targetRuleId,
  onChange,
  onDirtyChange,
  onValidateRequest,
  onSaveDraft,
  onPublishConfirmRequest,
  onCancelPublish
}) => {
  switch (mode) {
    case 'empty':
      return (
        <div className="h-full flex items-center justify-center bg-gray-50">
          <Empty description="Select a baseline or version to view" />
        </div>
      );
      
    case 'edit':
      return (
        <EditorView
          draftData={draftData}
          dirty={dirty}
          validating={validating}
          validationPassed={validationPassed}
          saving={saving}
          targetFieldPath={targetFieldPath}
          onChange={onChange}
          onDirtyChange={onDirtyChange}
          onValidateRequest={onValidateRequest}
          onSaveDraft={onSaveDraft}
          onPublishConfirmRequest={onPublishConfirmRequest}
        />
      );

    case 'diff':
      return <DiffView diffData={diffData} targetRuleId={targetRuleId} />;
      
    case 'publish_confirm':
      return (
        <PublishConfirmView 
          validationResult={validationResult}
          publishing={publishing}
          onPublishConfirmRequest={onPublishConfirmRequest}
          onCancelPublish={onCancelPublish}
        />
      );
      
    case 'history_detail':
      return (
        <div className="h-full flex items-center justify-center bg-gray-50">
          <Empty description="History detail view is read-only. Switch to 'diff' mode to see changes." />
        </div>
      );
      
    default:
      return <div>Unknown Mode: {mode}</div>;
  }
};

export default CenterContainer;
