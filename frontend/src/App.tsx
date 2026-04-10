import React, { useState } from 'react';
import BaselineList from './components/BaselineList';
import RuleEditor from './components/RuleEditor';
import DiffPanel from './components/DiffPanel';
import { Layout, Typography, ConfigProvider } from 'antd';
import { DatabaseZap } from 'lucide-react';
import './api/mock'; // Import mock adapter to enable mock API

const { Header, Content } = Layout;
const { Title } = Typography;

function App() {
  const [selectedBaselineId, setSelectedBaselineId] = useState<string>();
  const [refreshTrigger, setRefreshTrigger] = useState(0);

  const handleSelectBaseline = (id: string) => {
    setSelectedBaselineId(id);
  };

  const handlePublished = () => {
    // Trigger diff panel refresh
    setRefreshTrigger(prev => prev + 1);
  };

  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#1677ff',
          borderRadius: 6,
        },
      }}
    >
      <Layout className="h-screen flex flex-col bg-gray-50 overflow-hidden font-sans">
        <Header className="bg-white border-b border-gray-200 px-6 flex items-center shadow-sm z-10 h-14">
          <DatabaseZap className="text-blue-600 mr-3" size={24} />
          <Title level={4} className="!m-0 text-gray-800">Rule Editor MVP</Title>
        </Header>

        <Content className="flex flex-1 overflow-hidden">
          {/* Left Column: Baseline List (approx 2/10) */}
          <div className="w-64 flex-shrink-0 z-0 shadow-[1px_0_4px_rgba(0,0,0,0.02)]">
            <BaselineList
              onSelect={handleSelectBaseline}
              selectedId={selectedBaselineId}
            />
          </div>

          {/* Middle Column: Rule Editor (approx 5/10) */}
          <div className="flex-1 min-w-[400px] shadow-[1px_0_4px_rgba(0,0,0,0.02)] z-10">
            <RuleEditor
              baselineId={selectedBaselineId}
              onPublished={handlePublished}
            />
          </div>

          {/* Right Column: Diff Panel (approx 3/10) */}
          <div className="w-96 flex-shrink-0 z-0 bg-gray-50 border-l border-gray-200">
            <DiffPanel
              baselineId={selectedBaselineId}
              refreshTrigger={refreshTrigger}
            />
          </div>
        </Content>
      </Layout>
    </ConfigProvider>
  );
}

export default App;
