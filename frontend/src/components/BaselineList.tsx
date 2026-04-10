import React from 'react';
import { List, Tag, Spin, Typography } from 'antd';
import { Baseline } from '../api/rules';
import { Database } from 'lucide-react';

interface BaselineListProps {
  baselines: Baseline[];
  loading: boolean;
  selectedId?: string;
  onSelect: (id: string) => void;
}

const BaselineList: React.FC<BaselineListProps> = ({ 
  baselines, 
  loading, 
  selectedId, 
  onSelect 
}) => {
  return (
    <div className="h-full bg-white flex flex-col p-4">
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
                  <div className="font-medium text-gray-800 truncate" title={item.name}>
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
