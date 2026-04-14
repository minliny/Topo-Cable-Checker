import React from 'react';
import { CenterMode, DraftData } from '../../types/ui';
import { ValidationResultDTO, DiffSourceTargetDTO, BaselineVersionRuleSetDTO } from '../../types/dto';
import { Spin, Result, Button, Typography, Empty, List } from 'antd';
import { XCircle, CheckCircle } from 'lucide-react';
import EditorView from './EditorView';
import DiffView from './DiffView';
import PublishConfirmView from './PublishConfirmView';
import HistoryDetailView from './HistoryDetailView';
import RollbackConfirmView from './RollbackConfirmView';

interface CenterContainerProps {
  mode: CenterMode;
  draftData: DraftData;
  dirty: boolean;
  validating: boolean;
  saving: boolean;
  publishing: boolean;
  validationPassed: boolean;
  validationResult: ValidationResultDTO | null;
  publishBlockedIssues: any[] | null;
  diffData: DiffSourceTargetDTO | null;
  rollbackEffectDiff?: DiffSourceTargetDTO | null;
  loadingRollbackEffectDiff?: boolean;
  targetRuleSet?: BaselineVersionRuleSetDTO | null;
  loadingTargetRuleSet?: boolean;
  targetRuleSetError?: string | null;
  targetFieldPath?: string;
  targetRuleId?: string;
  selectedVersionId?: string;
  onChange: (data: DraftData) => void;
  onDirtyChange: (dirty: boolean) => void;
  onValidateRequest: () => void;
  onSaveDraft: () => void;
  onPublishConfirmRequest: () => void;
  onPublishRequest: () => void;
  onCancelPublish: () => void;
  onRequestDiff: () => void;
  onCloseDiff: () => void;
  onRequestRestoreDraft: () => void;
  onRestoreDraftConfirmRequest: () => void;
  onCancelRestoreDraft: () => void;
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
  publishBlockedIssues,
  diffData,
  rollbackEffectDiff,
  loadingRollbackEffectDiff,
  targetRuleSet,
  loadingTargetRuleSet,
  targetRuleSetError,
  targetFieldPath,
  targetRuleId,
  selectedVersionId,
  onChange,
  onDirtyChange,
  onValidateRequest,
  onSaveDraft,
  onPublishConfirmRequest,
  onPublishRequest,
  onCancelPublish,
  onRequestDiff,
  onCloseDiff,
  onRequestRestoreDraft,
  onRestoreDraftConfirmRequest,
  onCancelRestoreDraft
}) => {
  switch (mode) {
    case 'empty':
      return (
        <div className="h-full flex items-center justify-center bg-gray-50">
          <Empty description="Select a baseline or version to view" />
        </div>
      );
      
    case 'edit':
    case 'restored_draft_edit':
      return (
        <EditorView
          draftData={draftData}
          dirty={dirty}
          validating={validating}
          validationPassed={validationPassed}
          saving={saving}
          targetFieldPath={targetFieldPath}
          isRestoredDraft={mode === 'restored_draft_edit'}
          onChange={onChange}
          onDirtyChange={onDirtyChange}
          onValidateRequest={onValidateRequest}
          onSaveDraft={onSaveDraft}
          onPublishConfirmRequest={onPublishConfirmRequest}
        />
      );

    case 'diff':
      return <DiffView diffData={diffData} targetRuleId={targetRuleId} onClose={onCloseDiff} />;
      
    case 'publish_confirm':
      return (
        <PublishConfirmView 
          validationResult={validationResult}
          publishing={publishing}
          onPublishConfirmRequest={onPublishRequest}
          onCancelPublish={onCancelPublish}
        />
      );
      
    case 'publish_blocked':
      return (
        <div className="h-full p-8 bg-white rounded-lg shadow-sm border border-red-100 flex flex-col">
          <Result
            status="error"
            title="Publish Blocked"
            subTitle="Your publish request was blocked due to critical validation issues."
            extra={[
              <Button key="fix" type="primary" onClick={onCancelPublish}>
                Return to Editor to Fix
              </Button>
            ]}
          >
            <div className="mt-4">
              <h4 className="text-red-800 font-medium mb-2">Blocking Issues:</h4>
              <List
                size="small"
                dataSource={publishBlockedIssues || []}
                renderItem={(item: any) => (
                  <List.Item>
                    <Typography.Text type="danger" className="flex items-center gap-2">
                      <XCircle size={14} />
                      {item.message}
                    </Typography.Text>
                  </List.Item>
                )}
              />
            </div>
          </Result>
        </div>
      );

    case 'published':
      return (
        <div className="h-full p-8 bg-white rounded-lg shadow-sm border border-green-100 flex items-center justify-center">
          <Result
            status="success"
            title="Successfully Published!"
            subTitle="The new version has been saved and is now active."
          />
        </div>
      );

    case 'history_detail':
      return (
        <HistoryDetailView 
          versionId={selectedVersionId}
          onRequestDiff={onRequestDiff}
          onRequestRestoreDraft={onRequestRestoreDraft}
        />
      );

    case 'restore_confirm':
      return (
        <RollbackConfirmView 
          versionId={selectedVersionId}
          rollbackEffectDiff={rollbackEffectDiff}
          loadingRollbackEffectDiff={loadingRollbackEffectDiff}
          targetRuleSet={targetRuleSet}
          loadingTargetRuleSet={loadingTargetRuleSet}
          targetRuleSetError={targetRuleSetError}
          onRollbackConfirmRequest={onRestoreDraftConfirmRequest}
          onCancelRollback={onCancelRestoreDraft}
        />
      );

    case 'publish_checking':
    case 'publishing':
    case 'restore_preparing':
      return (
        <div className="h-full flex items-center justify-center bg-gray-50 flex-col gap-4">
          <Spin size="large" />
          <span className="text-gray-500 uppercase tracking-widest text-sm">{mode.replace('_', ' ')}...</span>
        </div>
      );
      
    default:
      return <div>Unknown Mode: {mode}</div>;
  }
};

export default CenterContainer;
