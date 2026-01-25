import { ref, computed } from 'vue';
import logger from '../../../shared/utils/logger.js';

/**
 * 知识图谱管理组合函数，统一处理知识图谱相关逻辑
 * @returns {Object} 包含知识图谱管理功能的对象
 */
export function useKnowledgeGraph() {
  /**
   * 根据文件类型获取对应的颜色
   * @param {string} type - 文件类型
   * @returns {string} 颜色值
   */
  const getFileColor = (type) => {
    const colorMap = {
      'pdf': '#FF5733',
      'docx': '#3366FF',
      'doc': '#3366FF',
      'xlsx': '#33FF57',
      'xls': '#33FF57',
      'pptx': '#FF33F5',
      'ppt': '#FF33F5',
      'txt': '#FFC300',
      'md': '#8E44AD'
    };
    return colorMap[type] || '#95A5A6';
  };

  /**
   * 将文件列表转换为知识图谱节点
   * @param {Array} files - 文件列表
   * @param {number} testNodeCount - 测试节点数量
   * @returns {Array} 知识图谱节点列表
   */
  const generateKnowledgeGraphNodes = (files, testNodeCount = 15) => {
    const nodes = [];
    const fileTypes = ['pdf', 'docx', 'xlsx', 'pptx', 'txt', 'md'];
    
    // 为每个文件创建一个节点
    files.forEach((file, index) => {
      const node = {
        id: file.id || file.path || index,
        name: file.name,
        type: file.type,
        radius: 20,
        color: getFileColor(file.type)
      };
      nodes.push(node);
    });
    
    // 增加更多随机测试节点
    for (let i = 0; i < testNodeCount; i++) {
      const randomType = fileTypes[Math.floor(Math.random() * fileTypes.length)];
      const node = {
        id: `test-node-${i}`,
        name: `Test-${i}.${randomType}`,
        type: randomType,
        radius: 20,
        color: getFileColor(randomType)
      };
      nodes.push(node);
    }
    
    return nodes;
  };

  /**
   * 生成知识图谱连线
   * @param {Array} nodes - 知识图谱节点列表
   * @param {number} connectionProbability - 节点间连接概率
   * @returns {Array} 知识图谱连线列表
   */
  const generateKnowledgeGraphLinks = (nodes, connectionProbability = 0.15) => {
    const links = [];
    const nodeCount = nodes.length;
    
    // 生成随机连线
    for (let i = 0; i < nodeCount; i++) {
      for (let j = i + 1; j < nodeCount; j++) {
        if (Math.random() < connectionProbability) {
          links.push({
            source: i,
            target: j
          });
        }
      }
    }
    
    return links;
  };

  /**
   * 处理知识图谱节点点击事件
   * @param {Object} node - 被点击的节点
   */
  const handleNodeClick = (node) => {
    logger.info('知识图谱节点被点击:', node);
  };

  /**
   * 处理知识图谱节点悬停事件
   * @param {Object} node - 被悬停的节点
   */
  const handleNodeHover = (node) => {
    logger.info('知识图谱节点悬停:', node);
  };

  /**
   * 处理知识图谱视图变化事件
   * @param {Object} viewInfo - 视图信息
   */
  const handleViewChanged = (viewInfo) => {
    logger.info('知识图谱视图变化:', viewInfo);
  };

  return {
    // 方法
    getFileColor,
    generateKnowledgeGraphNodes,
    generateKnowledgeGraphLinks,
    handleNodeClick,
    handleNodeHover,
    handleViewChanged
  };
}