import React, { useEffect, useState } from 'react';
import { List, Tag, Spin, Typography } from 'antd';
import { rulesApi, Baseline } from '../api/rules';
import { Database } from 'lucide-react';

interface BaselineListProps {
  onSelect: (id: string) => void;
  selectedId?: string;
}

const BaselineList: React.FC<BaselineListProps> = ({ onSelect, selectedId }) => {
  const [baselines, setBaselines] = useState<Baseline[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchBaselines = async () => {
      try {
        const data = await rulesApi.getBaselines();
        setBaselines(data);
        if (data.length > 0 && !selectedId) {
          onSelect(data[0].id);
        }
      } catch (error) {
        console.error('Failed to load baselines', error);
      } finally {
        setLoading(false);
      }
    };
    fetchBaselines();
  }, [onSelect, selectedId]);

  return (
    <div className="h-full bg-white border-r border-gray-200 overflow-y-auto p-4 flex flex-col">
      <div className="flex items-center space-x-2 mb-6 pb-2 border-b border-gray-100">
        <Database size={20} className="text-blue-600" />
        <Typography.Title level={5} className="!m-0">Baselines</Typography.Title>
      </div>

      {loading ? (
        <div className="flex justify-center items-center flex-1">
          <Spin />
        </div>
      ) : (
        <List
          itemLayout="horizontal"
          dataSource={baselines}
          renderItem={(item) => (
            <List.Item
              onClick={() => onSelect(item.id)}
              className={`cursor-pointer rounded-md mb-2 px-3 py-2 transition-colors ${
                selectedId === item.id 
                  ? 'bg-blue-50 border border-blue-200' 
                  : 'hover:bg-gray-50 border border-transparent'
              }`}
            >
              <List.Item.Meta
                title={
                  <div className="font-medium text-gray-800">
                    {item.name}
                  </div>
                }
                description={
                  <div className="mt-1">
                    <Tag color={item.status === 'published' ? 'green' : item.status === 'draft' ? 'orange' : 'blue'}>
                      {item.status.toUpperCase()}
                    </Tag>
                  </div>
                }
              />
            </List.Item>
          )}
        />
      )}
    </div>
  );
};

export default BaselineList;
