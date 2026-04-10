import React, { useEffect, useState } from 'react';
import { Layout, Typography, ConfigProvider, Modal, message } from 'antd';
import { DatabaseZap } from 'lucide-react';
import BaselineList from './components/BaselineList';
import RuleEditor from './components/RuleEditor';
import RightPanel from './components/RightPanel';
import { rulesApi, Baseline } from './api/rules';
import { PageState, CenterMode, RightPanelMode, DraftData } from './types/ui';
import './api/mock';

const { Header, Content } = Layout;
const { Title } = Typography;

function App() {
  // Page-level unified state
  const [pageState, setPageState] = useState<PageState>({
    selectedBaselineId: undefined,
    centerMode: 'empty',
    rightPanelMode: 'help',
    draftData: {},
    dirty: false,
    validationResult: null,
    diffData: null,
  });

  const [baselines, setBaselines] = useState<Baseline[]>([]);
  const [loadingBaselines, setLoadingBaselines] = useState(true);
  const [loadingDiff, setLoadingDiff] = useState(false);
  const [validating, setValidating] = useState(false);
  const [publishing, setPublishing] = useState(false);
  const [saving, setSaving] = useState(false);

  // Load baselines on mount
  useEffect(() => {
    const fetchBaselines = async () => {
      setLoadingBaselines(true);
      try {
        const data = await rulesApi.getBaselines();
        setBaselines(data);
        if (data.length > 0) {
          // Initialize default selection
          switchBaselineContext(data[0].id);
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

  // Fetch diff when baseline context switches to diff_summary
  useEffect(() => {
    const fetchDiff = async () => {
      if (!pageState.selectedBaselineId) return;
      
      setLoadingDiff(true);
      try {
        const data = await rulesApi.getBaselineDiff(pageState.selectedBaselineId);
        setPageState(prev => ({ ...prev, diffData: data }));
      } catch (error) {
        console.error('Failed to fetch diff', error);
        message.error('Failed to load diff data');
      } finally {
        setLoadingDiff(false);
      }
    };

    if (pageState.rightPanelMode === 'diff_summary') {
      fetchDiff();
    }
  }, [pageState.selectedBaselineId, pageState.rightPanelMode]);

  // Switch Context (Logic without Dirty Guard)
  const switchBaselineContext = (id: string) => {
    setPageState(prev => ({
      ...prev,
      selectedBaselineId: id,
      centerMode: 'edit',
      rightPanelMode: 'diff_summary', // Show diff summary by default when switching
      draftData: { rule_type: 'threshold', params: '{\n  "threshold": 10,\n  "severity": "warning"\n}' }, // Load real data here in future
      dirty: false,
      validationResult: null,
      diffData: null,
    }));
  };

  // Left Nav Click Handler (With Dirty Guard)
  const handleNavChange = (id: string) => {
    if (id === pageState.selectedBaselineId) return;

    if (pageState.dirty) {
      Modal.confirm({
        title: 'Unsaved Changes',
        content: 'You have unsaved changes in the current rule. Do you want to discard them?',
        okText: 'Discard',
        okType: 'danger',
        cancelText: 'Cancel',
        onOk: () => {
          switchBaselineContext(id);
        }
      });
    } else {
      switchBaselineContext(id);
    }
  };

  // Center Column: Data Change
  const handleDraftChange = (data: DraftData) => {
    setPageState(prev => ({ ...prev, draftData: data }));
  };

  const handleDirtyChange = (dirty: boolean) => {
    setPageState(prev => ({ ...prev, dirty }));
  };

  // Action: Save Draft
  const handleSaveDraft = async () => {
    setSaving(true);
    // Simulate save API
    setTimeout(() => {
      setSaving(false);
      setPageState(prev => ({ ...prev, dirty: false }));
      message.success('Draft saved successfully');
    }, 500);
  };

  // Action: Validate
  const handleValidate = async () => {
    setValidating(true);
    try {
      let parsedParams = {};
      try {
        parsedParams = JSON.parse(pageState.draftData.params || '{}');
      } catch (err) {
        message.error('Params must be valid JSON');
        setValidating(false);
        return;
      }

      const res = await rulesApi.validateDraft({
        rule_type: pageState.draftData.rule_type || 'threshold',
        params: parsedParams,
      });

      setPageState(prev => ({ 
        ...prev, 
        validationResult: res.validation_result,
        rightPanelMode: 'validation' // Switch right panel to show validation results
      }));

      if (res.validation_result.valid) {
        message.success('Validation passed!');
      } else {
        message.error('Validation failed');
      }
    } catch (error) {
      console.error(error);
      message.error('Error during validation');
    } finally {
      setValidating(false);
    }
  };

  // Action: Publish
  const handlePublish = async () => {
    if (!pageState.selectedBaselineId) return;
    
    setPublishing(true);
    try {
      const res = await rulesApi.publishRules(pageState.selectedBaselineId);
      message.success(`Published version ${res.version}: ${res.summary}`);
      
      // Post-publish flow: clear dirty, switch right panel to diff summary to see changes
      setPageState(prev => ({
        ...prev,
        dirty: false,
        validationResult: null,
        rightPanelMode: 'diff_summary',
      }));
      
      // Refresh diff data manually
      setLoadingDiff(true);
      const newDiffData = await rulesApi.getBaselineDiff(pageState.selectedBaselineId);
      setPageState(prev => ({ ...prev, diffData: newDiffData }));
      setLoadingDiff(false);

    } catch (error) {
      console.error(error);
      message.error('Failed to publish rules');
    } finally {
      setPublishing(false);
    }
  };

  // Action: Jump from Right to Center (e.g. click error field)
  const handleJumpToField = (field: string) => {
    // Scroll or highlight logic in center column
    message.info(`Navigating to field: ${field}`);
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
              selectedId={pageState.selectedBaselineId}
              onSelect={handleNavChange}
            />
          </div>

          {/* Middle Column (Main Editor) */}
          <div className="flex-1 min-w-[400px] z-10 bg-gray-50 overflow-y-auto p-6 relative">
            <RuleEditor
              mode={pageState.centerMode}
              draftData={pageState.draftData}
              dirty={pageState.dirty}
              onChange={handleDraftChange}
              onDirtyChange={handleDirtyChange}
              onValidate={handleValidate}
              onSaveDraft={handleSaveDraft}
              onPublish={handlePublish}
              validating={validating}
              publishing={publishing}
              saving={saving}
              validationPassed={pageState.validationResult?.valid ?? false}
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
            />
          </div>

        </Content>
      </Layout>
    </ConfigProvider>
  );
}

export default App;
