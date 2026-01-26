import { defineStore } from 'pinia';

// 定义节点和连接的类型
/**
 * @typedef {Object} ContextNode
 * @property {number} id - 节点ID
 * @property {string} name - 节点名称
 * @property {number} group - 节点分组
 * @property {number} size - 节点大小
 * @property {string} description - 节点描述
 */

/**
 * @typedef {Object} ContextLink
 * @property {number} source - 源节点ID
 * @property {number} target - 目标节点ID
 * @property {number} value - 连接权重
 */

export const useContextVisualizationStore = defineStore('contextVisualization', {
  state: () => ({
    // 上下文可视化数据（硬编码，暂时未接入数据库）
    graphData: {
      nodes: [
        { id: 1, name: "人工智能", group: 1, size: 25, description: "研究如何使计算机模拟人类智能的科学与工程" },
        { id: 2, name: "机器学习", group: 1, size: 20, description: "使计算机能够从数据中学习并改进的AI分支" },
        { id: 3, name: "深度学习", group: 1, size: 18, description: "基于人工神经网络的机器学习方法" },
        { id: 4, name: "神经网络", group: 1, size: 16, description: "受大脑结构启发的计算模型" },
        { id: 5, name: "计算机视觉", group: 2, size: 20, description: "使计算机能够理解图像内容的AI领域" },
        { id: 6, name: "自然语言处理", group: 3, size: 20, description: "处理和理解人类语言的AI技术" },
        { id: 7, name: "语音识别", group: 3, size: 16, description: "将语音转换为文本的技术" },
        { id: 8, name: "知识图谱", group: 4, size: 22, description: "表示实体和关系的结构化数据" },
        { id: 9, name: "数据挖掘", group: 5, size: 18, description: "从大量数据中发现模式和知识" },
        { id: 10, name: "大数据", group: 5, size: 20, description: "处理和分析海量数据的技术" },
        { id: 11, name: "云计算", group: 6, size: 20, description: "通过网络提供计算资源和服务" },
        { id: 12, name: "边缘计算", group: 6, size: 16, description: "在网络边缘处理数据的计算范式" },
        { id: 13, name: "物联网", group: 7, size: 22, description: "连接物理设备的网络系统" },
        { id: 14, name: "区块链", group: 8, size: 20, description: "分布式账本技术" },
        { id: 15, name: "增强现实", group: 9, size: 20, description: "将虚拟信息叠加到现实世界" },
        { id: 16, name: "虚拟现实", group: 9, size: 20, description: "创建沉浸式虚拟环境" },
        { id: 17, name: "量子计算", group: 10, size: 22, description: "利用量子力学原理的计算技术" },
        { id: 18, name: "机器人学", group: 11, size: 20, description: "设计、构建和操作机器人的领域" },
        { id: 19, name: "自动化", group: 11, size: 18, description: "使过程或系统自动运行的技术" },
        { id: 20, name: "数字孪生", group: 12, size: 18, description: "物理实体的虚拟副本" }
      ],
      links: [
        { source: 1, target: 2, value: 1 },
        { source: 2, target: 3, value: 1 },
        { source: 3, target: 4, value: 1 },
        { source: 1, target: 5, value: 1 },
        { source: 1, target: 6, value: 1 },
        { source: 6, target: 7, value: 1 },
        { source: 1, target: 8, value: 1 },
        { source: 2, target: 9, value: 1 },
        { source: 9, target: 10, value: 1 },
        { source: 10, target: 11, value: 1 },
        { source: 11, target: 12, value: 1 },
        { source: 12, target: 13, value: 1 },
        { source: 13, target: 14, value: 1 },
        { source: 1, target: 15, value: 1 },
        { source: 15, target: 16, value: 1 },
        { source: 1, target: 17, value: 1 },
        { source: 1, target: 18, value: 1 },
        { source: 18, target: 19, value: 1 },
        { source: 13, target: 20, value: 1 },
        { source: 5, target: 15, value: 1 },
        { source: 10, target: 8, value: 1 },
        { source: 17, target: 11, value: 1 },
        { source: 14, target: 10, value: 1 },
        { source: 9, target: 8, value: 1 }
      ]
    },
    // 加载状态
    loading: false,
    // 错误信息
    error: null
  }),

  getters: {
    // 获取所有节点
    nodes: (state) => state.graphData.nodes,
    
    // 获取所有连接
    links: (state) => state.graphData.links,
    
    // 获取节点总数
    nodeCount: (state) => state.graphData.nodes.length,
    
    // 获取连接总数
    linkCount: (state) => state.graphData.links.length,
    
    // 根据ID获取节点
    getNodeById: (state) => (id) => {
      return state.graphData.nodes.find(node => node.id === id);
    },
    
    // 根据分组获取节点
    getNodesByGroup: (state) => (group) => {
      return state.graphData.nodes.filter(node => node.group === group);
    }
  },

  actions: {
    // 设置错误信息
    setError(error) {
      this.error = error;
    },

    // 清空错误信息
    clearError() {
      this.error = null;
    },

    // 设置加载状态
    setLoading(loading) {
      this.loading = loading;
    },

    // 更新节点数据
    updateNode(nodeId, updates) {
      const nodeIndex = this.graphData.nodes.findIndex(node => node.id === nodeId);
      if (nodeIndex !== -1) {
        this.graphData.nodes[nodeIndex] = { ...this.graphData.nodes[nodeIndex], ...updates };
      }
    },

    // 添加新节点
    addNode(node) {
      // 确保ID唯一
      const maxId = Math.max(...this.graphData.nodes.map(n => n.id), 0);
      const newNode = {
        id: node.id || maxId + 1,
        name: node.name || '未命名节点',
        group: node.group || 0,
        size: node.size || 16,
        description: node.description || ''
      };
      this.graphData.nodes.push(newNode);
      return newNode;
    },

    // 添加新连接
    addLink(link) {
      // 检查连接是否已存在
      const existingLink = this.graphData.links.find(
        l => l.source === link.source && l.target === link.target
      );
      if (!existingLink) {
        this.graphData.links.push({
          source: link.source,
          target: link.target,
          value: link.value || 1
        });
      }
    },

    // 未来可以添加从API获取数据的方法
    // async loadGraphData() {
    //   this.setLoading(true);
    //   this.clearError();
    //   
    //   try {
    //     // 当接入数据库后，可以从API获取数据
    //     // const response = await apiService.getKnowledgeGraphData();
    //     // this.graphData = response.data;
    //   } catch (error) {
    //     console.error('加载知识图谱数据失败:', error);
    //     this.setError(`加载失败: ${error.message || '未知错误'}`);
    //   } finally {
    //     this.setLoading(false);
    //   }
    // }
  }
});