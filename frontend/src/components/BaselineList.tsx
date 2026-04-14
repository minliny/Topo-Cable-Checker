import React, { useMemo } from 'react';
import { Tree, Spin, Typography } from 'antd';
import { Database, GitBranch, Edit3, Archive, History } from 'lucide-react';
import { BaselineNodeDTO } from '../types/dto';
import { BaselineTreeNode, BaselineNodeType } from '../types/ui';
import type { DataNode } from 'antd/es/tree';

interface BaselineListProps {
  baselines: BaselineNodeDTO[];
  loading: boolean;
  selectedKey?: string;
  selectedNodeType?: BaselineNodeType;
  onSelect: (node: BaselineTreeNode) => void;
}

const BaselineList: React.FC<BaselineListProps> = ({ 
  baselines, 
  loading, 
  selectedKey, 
  selectedNodeType,
  onSelect 
}) => {
  
  // Transform flat baselines array into tree data
  const treeData = useMemo(() => {
    // 1. Group nodes by baseline_id
    const grouped = new Map<string, BaselineTreeNode>();
    
    baselines.forEach(node => {
      if (node.type === 'baseline_root') {
        grouped.set(node.id, {
          key: node.id,
          title: node.name,
          type: 'baseline_root',
          baselineId: node.baseline_id,
          versionId: 'root',
          children: []
        });
      }
    });

    baselines.forEach(node => {
      if (node.type !== 'baseline_root' && node.parent_id) {
        const parent = grouped.get(node.parent_id);
        if (parent) {
          parent.children!.push({
            key: node.id,
            title: node.name,
            type: node.type as BaselineNodeType,
            isLeaf: true,
            baselineId: node.baseline_id,
            parentId: node.parent_id,
            versionId: node.version_id,
            restoredFromVersionId: node.restored_from_version_id,
            restoredFromVersionLabel: node.restored_from_version_label,
            status: node.status as any
          });
        }
      }
    });

    return Array.from(grouped.values());
  }, [baselines]);

  // Recursively map our Custom Tree Nodes to Ant Design Tree DataNodes
  const renderTreeNodes = (data: BaselineTreeNode[]): DataNode[] => {
    return data.map((item) => {
      let icon = <Database size={14} className="text-gray-500" />;
      if (item.type === 'working_draft') icon = <Edit3 size={14} className="text-orange-500" />;
      else if (item.type === 'restored_draft') icon = <History size={14} className="text-purple-500" />;
      else if (item.type === 'published_version') icon = <Archive size={14} className="text-green-600" />;
      else icon = <GitBranch size={14} className="text-blue-600" />;

      return {
        key: item.key,
        title: (
          <span className="flex items-center text-sm gap-2">
            {icon}
            <span className="truncate w-full">{item.title}</span>
          </span>
        ),
        isLeaf: item.isLeaf,
        children: item.children ? renderTreeNodes(item.children) : undefined,
        // attach original node info for event handling
        _originalNode: item 
      } as DataNode & { _originalNode: BaselineTreeNode };
    });
  };

  const handleSelect = (selectedKeys: React.Key[], info: any) => {
    if (selectedKeys.length === 0) return; // Prevent deselecting
    
    const nodeData = info.node._originalNode as BaselineTreeNode;
    if (nodeData) {
      onSelect(nodeData);
    }
  };

  // Determine actual selected key based on node type and version
  const activeKey = selectedNodeType === 'restored_draft' 
    ? `${selectedKey?.split('-')[0]}-draft` 
    : selectedKey;

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
        <div className="flex-1 overflow-y-auto custom-scrollbar">
          <Tree
            showLine
            defaultExpandAll
            selectedKeys={activeKey ? [activeKey] : []}
            onSelect={handleSelect}
            treeData={renderTreeNodes(treeData)}
            className="text-gray-700 bg-transparent"
          />
        </div>
      )}
    </div>
  );
};

export default BaselineList;
