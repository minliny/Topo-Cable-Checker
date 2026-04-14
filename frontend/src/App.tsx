import React, { useEffect, useState, useReducer } from 'react';
import { Layout, Typography, ConfigProvider, Modal, message } from 'antd';
import { DatabaseZap } from 'lucide-react';
import BaselineList from './components/BaselineList';
import CenterContainer from './components/CenterViews';
import RightPanel from './components/RightPanel';
import { rulesApi } from './api/rules';
import { PageState, DraftData, BaselineTreeNode } from './types/ui';
import { pageReducer } from './store/pageReducer';
import { BaselineNodeDTO, DiffSourceTargetDTO, BaselineVersionRuleSetDTO } from './types/dto';
import './api/mock';

const { Header, Content } = Layout;
const { Title } = Typography;

function App() {
  // --- 1. State Machine (Page Level) ---
  const [pageState, dispatch] = useReducer(pageReducer, {
    selectedBaselineId: undefined,
    selectedVersionId: undefined,
    
    centerMode: 'empty',
    rightPanelMode: 'help',
    
    draftData: {},
    dirty: false,
    
    validationResult: null,
    publishBlockedIssues: null,
    diffData: null,
  });

  const [baselines, setBaselines] = useState<BaselineNodeDTO[]>([]);
  const [loadingBaselines, setLoadingBaselines] = useState(true);
  
  // Local Loading States
  const [loadingDiff, setLoadingDiff] = useState(false);
  const [validating, setValidating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [loadingRollbackEffectDiff, setLoadingRollbackEffectDiff] = useState(false);
  const [rollbackEffectDiff, setRollbackEffectDiff] = useState<DiffSourceTargetDTO | null>(null);
  const [loadingTargetRuleSet, setLoadingTargetRuleSet] = useState(false);
  const [targetRuleSet, setTargetRuleSet] = useState<BaselineVersionRuleSetDTO | null>(null);
  const [targetRuleSetError, setTargetRuleSetError] = useState<string | null>(null);

  // --- 2. Initialization ---
  useEffect(() => {
    const fetchBaselines = async () => {
      setLoadingBaselines(true);
      try {
        const data = await rulesApi.getBaselines();
        // Ensure data is an array before setting baselines and checking length
        const baselinesList = Array.isArray(data) ? data : (data as any)?.baselines || [];
        setBaselines(baselinesList);
        if (baselinesList.length > 0) {
          // Init select first draft
          switchNavContext(baselinesList[0].id, 'draft', 'working_draft');
        }
      } catch (error) {
        console.error('Failed to fetch baselines', error);
        message.error('Failed to load baselines');
      } finally {
        setLoadingBaselines(false);
      }
    };
    fetchBaselines();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // --- 4. Event Handlers (Dispatching Actions) ---

  const switchNavContext = async (baselineId: string, versionId: string, nodeType: string, sourceVersionId?: string, sourceVersionLabel?: string) => {
    const isDraft = versionId === 'draft';
    let draftData = {};
    
    // A1-6: Auto-recover saved draft when entering a baseline editing context
    if (isDraft && baselineId) {
      try {
        const draftResult = await rulesApi.loadDraft(baselineId);
        if (draftResult.has_draft && draftResult.draft_data) {
          // Use the saved working draft
          dispatch({ 
            type: 'SWITCH_CONTEXT', 
            payload: { 
              baselineId, 
              versionId, 
              isDraft, 
              draftData: {
                rule_type: draftResult.draft_data.rule_type || 'threshold',
                params: typeof draftResult.draft_data.params === 'string' 
                  ? draftResult.draft_data.params 
                  : JSON.stringify(draftResult.draft_data.params || {}, null, 2),
                ...(draftResult.draft_data.rule_id ? { rule_id: draftResult.draft_data.rule_id } : {}),
                ...(draftResult.draft_data.target_type ? { target_type: draftResult.draft_data.target_type } : {}),
                ...(draftResult.draft_data.severity ? { severity: draftResult.draft_data.severity } : {}),
              },
              nodeType: nodeType as any,
              sourceVersionId,
              sourceVersionLabel
            } 
          });
          return;
        }
      } catch (error) {
        console.warn('Failed to load saved draft, using default:', error);
      }
    }

    if (isDraft) {
      if (nodeType === 'rollback_candidate') {
        draftData = { rule_type: 'threshold', params: '{\n  "threshold": 10,\n  "severity": "warning",\n  "_comment": "Rolled back from ' + sourceVersionId + '"\n}' };
      } else {
        draftData = { rule_type: 'threshold', params: '{\n  "threshold": 10,\n  "severity": "warning"\n}' };
      }
    }
    dispatch({ 
      type: 'SWITCH_CONTEXT', 
      payload: { 
        baselineId, 
        versionId, 
        isDraft, 
        draftData,
        nodeType: nodeType as any,
        sourceVersionId,
        sourceVersionLabel
      } 
    });
  };

  // Left Nav Tree Selection (With Dirty Guard)
  const handleNavSelect = (node: BaselineTreeNode) => {
    const isSameContext = node.baselineId === pageState.selectedBaselineId && node.versionId === pageState.selectedVersionId;
    if (isSameContext) return;

    if (pageState.dirty) {
      Modal.confirm({
        title: 'Unsaved Changes',
        content: 'You have unsaved changes in the current draft. Do you want to discard them?',
        okText: 'Discard',
        okType: 'danger',
        cancelText: 'Cancel',
        onOk: () => {
          switchNavContext(node.baselineId, node.versionId, node.type, node.sourceVersionId, node.sourceVersionLabel);
        }
      });
    } else {
      switchNavContext(node.baselineId, node.versionId, node.type, node.sourceVersionId, node.sourceVersionLabel);
    }
  };

  // Center Column: Data Change
  const handleDraftChange = (data: DraftData) => {
    dispatch({ type: 'UPDATE_DRAFT', payload: { draftData: data, dirty: pageState.dirty } });
  };

  const handleDirtyChange = (dirty: boolean) => {
    dispatch({ type: 'UPDATE_DRAFT', payload: { draftData: pageState.draftData, dirty } });
  };

  // Action Requests (State machine signals)
  const requestValidation = async () => {
    dispatch({ type: 'REQUEST_VALIDATION' });
    setValidating(true);
    try {
      let parsedParams = {};
      try {
        parsedParams = JSON.parse(pageState.draftData.params || '{}');
      } catch (err) {
        message.error('Params must be valid JSON');
        setValidating(false);
        dispatch({ type: 'VALIDATION_FAILED' });
        return;
      }

      const res = await rulesApi.validateDraft({
        rule_type: pageState.draftData.rule_type || 'threshold',
        params: parsedParams,
      });

      dispatch({ type: 'VALIDATION_SUCCESS', payload: { result: res } });

      if (res.valid) {
        message.success('Validation passed!');
      } else {
        message.error('Validation failed');
      }
    } catch (error) {
      console.error(error);
      message.error('Error during validation');
      dispatch({ type: 'VALIDATION_FAILED' });
    } finally {
      setValidating(false);
    }
  };

  const requestPublishConfirm = () => {
    dispatch({ type: 'PREPARE_PUBLISH' });
  };

  const requestPublish = async () => {
    dispatch({ type: 'REQUEST_PUBLISH' });
    
    try {
      // P1.0-1: Send explicit PublishRequest body matching backend PublishRequestDTO
      const draftPayload = {
        rule_type: pageState.draftData.rule_type || 'threshold',
        target_type: 'devices',
        severity: 'warning',
        params: pageState.draftData.params ? JSON.parse(pageState.draftData.params) : {}
      };
      
      const res = await rulesApi.publishRules(pageState.selectedBaselineId!, draftPayload);
      
      if (!res.success) {
        dispatch({ type: 'PUBLISH_BLOCKED', payload: { issues: res.blocked_issues || [] } });
        message.error('Publish blocked by validation rules');
        return;
      }

      message.success(`Published version ${res.version_label}: ${res.summary}`);
      dispatch({ type: 'PUBLISH_SUCCESS', payload: { versionId: res.version_id! } });
      
      // After a short delay to show "published" success view, auto-navigate to history
      setTimeout(() => {
         dispatch({ type: 'TRIGGER_POST_PUBLISH_NAVIGATION', payload: { versionId: res.version_id! } });
      }, 1500);
      
    } catch (error) {
      console.error(error);
      message.error('Failed to publish rules');
      dispatch({ type: 'CANCEL_PUBLISH' });
    }
  };

  const cancelPublish = () => {
    dispatch({ type: 'CANCEL_PUBLISH' });
  };

  const requestDiff = async () => {
    const sourceVersionId = pageState.selectedNodeType === 'working_draft' || pageState.selectedNodeType === 'rollback_candidate' 
      ? pageState.selectedVersionId || 'draft' 
      : pageState.selectedVersionId!;
    const targetVersionId = 'previous_version'; // Simplified for MVP

    dispatch({ type: 'REQUEST_DIFF', payload: { sourceVersionId, targetVersionId } });
    setLoadingDiff(true);
    try {
      const data = await rulesApi.getBaselineDiff(pageState.selectedBaselineId!, sourceVersionId, targetVersionId);
      dispatch({ type: 'DIFF_SUCCESS', payload: { diffData: data } });
    } catch (error) {
      console.error('Failed to fetch diff', error);
      message.error('Failed to load diff data');
      dispatch({ type: 'DIFF_FAILED' });
    } finally {
      setLoadingDiff(false);
    }
  };

  useEffect(() => {
    if (pageState.centerMode !== 'rollback_confirm') {
      if (rollbackEffectDiff) setRollbackEffectDiff(null);
      if (loadingRollbackEffectDiff) setLoadingRollbackEffectDiff(false);
      return;
    }

    if (!pageState.selectedBaselineId || !pageState.selectedVersionId) return;

    const baselineId = pageState.selectedBaselineId;
    const targetVersionId = pageState.selectedVersionId;

    let cancelled = false;
    const fetchRollbackEffectDiff = async () => {
      setLoadingRollbackEffectDiff(true);
      try {
        const data = await rulesApi.getRollbackEffectDiff(baselineId, targetVersionId);
        if (!cancelled) setRollbackEffectDiff(data);
      } catch (error) {
        console.error('Failed to fetch rollback effect diff', error);
        if (!cancelled) setRollbackEffectDiff(null);
      } finally {
        if (!cancelled) setLoadingRollbackEffectDiff(false);
      }
    };

    fetchRollbackEffectDiff();

    return () => {
      cancelled = true;
    };
  }, [pageState.centerMode, pageState.selectedBaselineId, pageState.selectedVersionId]);

  useEffect(() => {
    if (pageState.centerMode !== 'rollback_confirm') {
      if (targetRuleSet) setTargetRuleSet(null);
      if (targetRuleSetError) setTargetRuleSetError(null);
      if (loadingTargetRuleSet) setLoadingTargetRuleSet(false);
      return;
    }

    if (!pageState.selectedBaselineId || !pageState.selectedVersionId) return;

    const baselineId = pageState.selectedBaselineId;
    const targetVersionId = pageState.selectedVersionId;

    let cancelled = false;
    const fetchTargetRuleSet = async () => {
      setLoadingTargetRuleSet(true);
      setTargetRuleSetError(null);
      try {
        const data = await rulesApi.getBaselineVersionRuleSet(baselineId, targetVersionId);
        if (!cancelled) setTargetRuleSet(data);
      } catch (error) {
        console.error('Failed to fetch target version rule_set', error);
        if (!cancelled) {
          setTargetRuleSet(null);
          setTargetRuleSetError('Failed to load target version rule_set');
        }
      } finally {
        if (!cancelled) setLoadingTargetRuleSet(false);
      }
    };

    fetchTargetRuleSet();

    return () => {
      cancelled = true;
    };
  }, [pageState.centerMode, pageState.selectedBaselineId, pageState.selectedVersionId]);

  const handleRequestRollbackClick = () => {
    // If there is already a draft, prompt user
    const hasDraft = baselines.find(b => b.id === pageState.selectedBaselineId)?.status === 'draft';
    // Simplified logic: assume we warn them
    if (pageState.dirty || hasDraft) {
      Modal.confirm({
        title: 'Draft Conflict',
        content: 'There is an existing working draft. Creating a rollback candidate will overwrite or conflict. Proceed?',
        onOk: () => dispatch({ type: 'REQUEST_ROLLBACK_CONFIRM' })
      });
    } else {
      dispatch({ type: 'REQUEST_ROLLBACK_CONFIRM' });
    }
  };

  const confirmRollback = async () => {
    dispatch({ type: 'REQUEST_ROLLBACK' });
    
    try {
      const res = await rulesApi.createRollbackCandidate(pageState.selectedBaselineId!, pageState.selectedVersionId!);
      
      dispatch({ 
        type: 'ROLLBACK_READY', 
        payload: { 
          draftData: { 
            rule_type: res.draft_data?.rule_type || 'threshold', 
            params: typeof res.draft_data?.params === 'string' ? res.draft_data.params : JSON.stringify(res.draft_data?.params || {}, null, 2)
          },
          sourceVersionId: res.source_version_id,
          sourceVersionLabel: res.source_version_label
        } 
      });
      message.success(`Successfully created rollback candidate from version ${res.source_version_label}`);
    } catch (error) {
      console.error(error);
      message.error('Failed to create rollback candidate');
      dispatch({ type: 'CANCEL_ROLLBACK' });
    }
  };

  const cancelRollback = () => {
    dispatch({ type: 'CANCEL_ROLLBACK' });
  };

  const handleSaveDraft = async () => {
    setSaving(true);
    try {
      // A1-5: Real Save Draft API call — replaces setTimeout mock
      let parsedParams = {};
      try {
        parsedParams = JSON.parse(pageState.draftData.params || '{}');
      } catch (err) {
        message.error('Params must be valid JSON to save');
        setSaving(false);
        return;
      }

      const res = await rulesApi.saveDraft({
        baseline_id: pageState.selectedBaselineId || '',
        rule_id: pageState.draftData.rule_id || '',
        rule_type: pageState.draftData.rule_type || 'threshold',
        target_type: pageState.draftData.target_type || 'devices',
        severity: pageState.draftData.severity || 'warning',
        params: parsedParams,
      });

      if (res.success) {
        dispatch({ type: 'DRAFT_SAVE_SUCCESS', payload: { savedAt: res.saved_at } });
        message.success('Draft saved successfully');
      } else {
        dispatch({ type: 'DRAFT_SAVE_FAILED' });
        message.error(res.message || 'Failed to save draft');
      }
    } catch (error) {
      console.error('Save draft error:', error);
      dispatch({ type: 'DRAFT_SAVE_FAILED' });
      message.error('Failed to save draft');
    } finally {
      setSaving(false);
    }
  };

  const closeDiff = () => {
    dispatch({ type: 'CLOSE_DIFF' });
  };

  const discardRollbackCandidate = () => {
    Modal.confirm({
      title: 'Discard Rollback Candidate',
      content: 'Are you sure you want to discard this rollback candidate? Your changes will be lost.',
      okText: 'Discard',
      okType: 'danger',
      onOk: () => {
        dispatch({ type: 'DISCARD_ROLLBACK_CANDIDATE' });
        message.success('Rollback candidate discarded');
      }
    });
  };

  // Target Jump interactions from Right Panel
  const handleJumpToField = (field: string) => {
    dispatch({ type: 'JUMP_TO_FIELD', payload: { fieldPath: field } });
  };

  const handleJumpToRule = (ruleId: string) => {
    dispatch({ type: 'JUMP_TO_RULE', payload: { ruleId } });
  };

  return (
    <ConfigProvider theme={{ token: { colorPrimary: '#1677ff', borderRadius: 6 } }}>
      <Layout className="h-screen flex flex-col bg-gray-50 overflow-hidden font-sans">
        <Header className="bg-white border-b border-gray-200 px-6 flex items-center shadow-sm z-10 h-14 flex-shrink-0">
          <DatabaseZap className="text-blue-600 mr-3" size={24} />
          <Title level={4} className="!m-0 text-gray-800">Rule Editor MVP</Title>
        </Header>

        {/* 
          Three Column Layout
          Left: Fixed 280px
          Center: 1fr (auto)
          Right: Fixed 420px
        */}
        <Content className="flex flex-1 overflow-hidden">
          
          {/* Left Column (Navigation) */}
          <div className="w-[280px] flex-shrink-0 z-0 bg-white border-r border-gray-200 overflow-hidden shadow-[1px_0_4px_rgba(0,0,0,0.02)]">
            <BaselineList
              baselines={baselines}
              loading={loadingBaselines}
              selectedKey={pageState.selectedVersionId ? `${pageState.selectedBaselineId}-${pageState.selectedVersionId}` : undefined}
              selectedNodeType={pageState.selectedNodeType}
              onSelect={handleNavSelect}
            />
          </div>

          {/* Middle Column (Main Editor / Views) */}
          <div className="flex-1 min-w-[400px] z-10 bg-gray-50 overflow-y-auto p-6 relative custom-scrollbar">
            <CenterContainer
              mode={pageState.centerMode}
              draftData={pageState.draftData}
              dirty={pageState.dirty}
              validating={validating}
              saving={saving}
              publishing={pageState.centerMode === 'publish_checking'}
              validationPassed={pageState.validationResult?.valid ?? false}
              validationResult={pageState.validationResult}
              publishBlockedIssues={pageState.publishBlockedIssues}
              diffData={pageState.diffData}
              rollbackEffectDiff={rollbackEffectDiff}
              loadingRollbackEffectDiff={loadingRollbackEffectDiff}
              targetRuleSet={targetRuleSet}
              loadingTargetRuleSet={loadingTargetRuleSet}
              targetRuleSetError={targetRuleSetError}
              targetFieldPath={pageState.targetFieldPath}
              targetRuleId={pageState.targetRuleId}
              selectedVersionId={pageState.selectedVersionId}
              onChange={handleDraftChange}
              onDirtyChange={handleDirtyChange}
              onValidateRequest={requestValidation}
              onSaveDraft={handleSaveDraft}
              onPublishConfirmRequest={requestPublishConfirm}
              onPublishRequest={requestPublish}
              onCancelPublish={cancelPublish}
              onRequestDiff={requestDiff}
              onCloseDiff={closeDiff}
              onRequestRollback={handleRequestRollbackClick}
              onRollbackConfirmRequest={confirmRollback}
              onCancelRollback={cancelRollback}
              onDiscardRollbackCandidate={discardRollbackCandidate}
            />
          </div>

          {/* Right Column (Assist/Nav) */}
          <div className="w-[420px] flex-shrink-0 z-0 bg-white border-l border-gray-200 overflow-hidden shadow-[-1px_0_4px_rgba(0,0,0,0.02)]">
            <RightPanel
              mode={pageState.rightPanelMode}
              validationResult={pageState.validationResult}
              diffData={pageState.diffData}
              loading={loadingDiff}
              onJumpToField={handleJumpToField}
              onJumpToRule={handleJumpToRule}
              onRequestDiff={requestDiff}
            />
          </div>

        </Content>
      </Layout>
    </ConfigProvider>
  );
}

export default App;
