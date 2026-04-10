import React, { useEffect, useState } from 'react';
import { Layout, Typography, ConfigProvider, Modal, message } from 'antd';
import { DatabaseZap } from 'lucide-react';
import BaselineList from './components/BaselineList';
import CenterContainer from './components/CenterViews';
import RightPanel from './components/RightPanel';
import { rulesApi, Baseline } from './api/rules';
import { PageState, DraftData, BaselineTreeNode } from './types/ui';
import './api/mock';

const { Header, Content } = Layout;
const { Title } = Typography;

function App() {
  // --- 1. State Machine (Page Level) ---
  const [pageState, setPageState] = useState<PageState>({
    selectedBaselineId: undefined,
    selectedVersionId: undefined,
    
    centerMode: 'empty',
    rightPanelMode: 'help',
    
    draftData: {},
    dirty: false,
    
    validationRequested: false,
    publishRequested: false,
    diffRequested: false,
    
    validationResult: null,
    diffData: null,
  });

  const [baselines, setBaselines] = useState<Baseline[]>([]);
  const [loadingBaselines, setLoadingBaselines] = useState(true);
  
  // Local Loading States
  const [loadingDiff, setLoadingDiff] = useState(false);
  const [validating, setValidating] = useState(false);
  const [publishing, setPublishing] = useState(false);
  const [saving, setSaving] = useState(false);

  // --- 2. Initialization ---
  useEffect(() => {
    const fetchBaselines = async () => {
      setLoadingBaselines(true);
      try {
        const data = await rulesApi.getBaselines();
        setBaselines(data);
        if (data.length > 0) {
          // Init select first draft
          switchNavContext(data[0].id, 'draft');
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

  // --- 3. State Driven Side Effects (The State Machine Engine) ---

  // Side Effect: Validate API
  useEffect(() => {
    if (!pageState.validationRequested) return;

    const runValidation = async () => {
      setValidating(true);
      try {
        let parsedParams = {};
        try {
          parsedParams = JSON.parse(pageState.draftData.params || '{}');
        } catch (err) {
          message.error('Params must be valid JSON');
          setPageState(prev => ({ ...prev, validationRequested: false }));
          setValidating(false);
          return;
        }

        const res = await rulesApi.validateDraft({
          rule_type: pageState.draftData.rule_type || 'threshold',
          params: parsedParams,
        });

        // State transition after validation success
        setPageState(prev => ({ 
          ...prev, 
          validationResult: res.validation_result,
          rightPanelMode: 'validation',
          validationRequested: false, // Reset signal
          targetFieldPath: undefined // Reset target field
        }));

        if (res.validation_result.valid) {
          message.success('Validation passed!');
        } else {
          message.error('Validation failed');
        }
      } catch (error) {
        console.error(error);
        message.error('Error during validation');
        setPageState(prev => ({ ...prev, validationRequested: false }));
      } finally {
        setValidating(false);
      }
    };

    runValidation();
  }, [pageState.validationRequested, pageState.draftData]);

  // Side Effect: Publish API
  useEffect(() => {
    if (!pageState.publishRequested || !pageState.selectedBaselineId) return;

    const runPublish = async () => {
      setPublishing(true);
      try {
        const res = await rulesApi.publishRules(pageState.selectedBaselineId!);
        message.success(`Published version ${res.version}: ${res.summary}`);
        
        // State transition: Publish Success -> History Detail View
        setPageState(prev => ({
          ...prev,
          selectedVersionId: res.version,
          centerMode: 'history_detail',
          rightPanelMode: 'version_meta',
          dirty: false,
          publishRequested: false, // Reset signal
          validationResult: null,
          diffData: null,
        }));
        
      } catch (error) {
        console.error(error);
        message.error('Failed to publish rules');
        setPageState(prev => ({ ...prev, publishRequested: false }));
      } finally {
        setPublishing(false);
      }
    };

    runPublish();
  }, [pageState.publishRequested, pageState.selectedBaselineId]);

  // Side Effect: Diff API
  useEffect(() => {
    if (!pageState.diffRequested || !pageState.selectedBaselineId) return;

    const fetchDiff = async () => {
      setLoadingDiff(true);
      try {
        const data = await rulesApi.getBaselineDiff(pageState.selectedBaselineId!);
        
        // State transition: Diff loaded -> Show Diff Views
        setPageState(prev => ({ 
          ...prev, 
          diffData: data,
          centerMode: 'diff',
          rightPanelMode: 'diff_summary',
          diffRequested: false // Reset signal
        }));
      } catch (error) {
        console.error('Failed to fetch diff', error);
        message.error('Failed to load diff data');
        setPageState(prev => ({ ...prev, diffRequested: false }));
      } finally {
        setLoadingDiff(false);
      }
    };

    fetchDiff();
  }, [pageState.diffRequested, pageState.selectedBaselineId]);


  // --- 4. Event Handlers (Only updating state, no direct API calls) ---

  const switchNavContext = (baselineId: string, versionId: string) => {
    const isDraft = versionId === 'draft';
    setPageState(prev => ({
      ...prev,
      selectedBaselineId: baselineId,
      selectedVersionId: versionId,
      centerMode: isDraft ? 'edit' : 'history_detail',
      rightPanelMode: isDraft ? 'help' : 'version_meta',
      draftData: isDraft 
        ? { rule_type: 'threshold', params: '{\n  "threshold": 10,\n  "severity": "warning"\n}' } 
        : {},
      dirty: false,
      validationResult: null,
      diffData: null,
      targetFieldPath: undefined,
      targetRuleId: undefined,
    }));
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
          switchNavContext(node.baselineId, node.versionId);
        }
      });
    } else {
      switchNavContext(node.baselineId, node.versionId);
    }
  };

  // Center Column: Data Change
  const handleDraftChange = (data: DraftData) => {
    setPageState(prev => ({ ...prev, draftData: data, targetFieldPath: undefined }));
  };

  const handleDirtyChange = (dirty: boolean) => {
    setPageState(prev => ({ ...prev, dirty }));
  };

  // Action Requests (State machine signals)
  const requestValidation = () => {
    setPageState(prev => ({ ...prev, validationRequested: true }));
  };

  const requestPublishConfirm = () => {
    // Transition to publish confirm view
    setPageState(prev => ({
      ...prev,
      centerMode: 'publish_confirm',
      rightPanelMode: 'publish_check'
    }));
  };

  const requestPublish = () => {
    setPageState(prev => ({ ...prev, publishRequested: true }));
  };

  const cancelPublish = () => {
    // Transition back to edit mode
    setPageState(prev => ({
      ...prev,
      centerMode: 'edit',
      rightPanelMode: 'validation' // or help
    }));
  };

  const requestDiff = () => {
    setPageState(prev => ({ ...prev, diffRequested: true }));
  };

  const handleSaveDraft = () => {
    setSaving(true);
    // Simulate save API
    setTimeout(() => {
      setSaving(false);
      setPageState(prev => ({ ...prev, dirty: false }));
      message.success('Draft saved successfully');
    }, 500);
  };

  // Target Jump interactions from Right Panel
  const handleJumpToField = (field: string) => {
    setPageState(prev => ({ ...prev, targetFieldPath: field }));
  };

  const handleJumpToRule = (ruleId: string) => {
    setPageState(prev => ({ ...prev, targetRuleId: ruleId, centerMode: 'diff' }));
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
              publishing={publishing}
              validationPassed={pageState.validationResult?.valid ?? false}
              validationResult={pageState.validationResult}
              diffData={pageState.diffData}
              targetFieldPath={pageState.targetFieldPath}
              targetRuleId={pageState.targetRuleId}
              onChange={handleDraftChange}
              onDirtyChange={handleDirtyChange}
              onValidateRequest={requestValidation}
              onSaveDraft={handleSaveDraft}
              onPublishConfirmRequest={requestPublishConfirm}
              onCancelPublish={cancelPublish}
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
