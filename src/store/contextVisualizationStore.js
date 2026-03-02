import { defineStore } from 'pinia';
import { useChatStore } from './chatStore.js';

// 定义节点和连接的类型
/**
 * @typedef {Object} ContextNode
 * @property {number} id - 节点ID
 * @property {string} name - 节点名称
 * @property {number} group - 节点分组
 * @property {number} size - 节点大小
 * @property {string} description - 节点描述
 * @property {string} role - 消息角色
 * @property {number} timestamp - 时间戳
 */

/**
 * @typedef {Object} ContextLink
 * @property {number} source - 源节点ID
 * @property {number} target - 目标节点ID
 * @property {number} value - 连接权重
 */

export const useContextVisualizationStore = defineStore('contextVisualization', {
  state: () => ({
    // 上下文可视化数据
    graphData: {
      nodes: [],
      links: []
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

    // 从聊天消息生成图谱数据
    generateGraphFromChatMessages() {
      const chatStore = useChatStore();
      const messages = chatStore.currentChatMessages;
      
      if (!messages || messages.length === 0) {
        // 如果没有消息，使用默认数据
        this.useDefaultGraphData();
        return;
      }
      
      // 清空现有数据
      this.graphData.nodes = [];
      this.graphData.links = [];
      
      // 为每条消息创建节点
      const messageNodes = [];
      messages.forEach((message, index) => {
        const msgValue = message?.value || message;
        
        // 创建节点
        const node = {
          id: index + 1,
          name: msgValue.role === 'user' ? `用户 ${index + 1}` : `AI ${index + 1}`,
          group: msgValue.role === 'user' ? 1 : 2,
          size: Math.min(20 + (msgValue.content?.length || 0) / 50, 30),
          description: msgValue.content || '',
          role: msgValue.role,
          timestamp: msgValue.timestamp
        };
        
        messageNodes.push(node);
        this.graphData.nodes.push(node);
      });
      
      // 创建消息之间的连接
      for (let i = 0; i < messageNodes.length - 1; i++) {
        this.graphData.links.push({
          source: messageNodes[i].id,
          target: messageNodes[i + 1].id,
          value: 1
        });
      }
    },

    // 使用默认图谱数据
    useDefaultGraphData() {
      this.graphData = {
        nodes: [
          { id: 1, name: "用户 1", group: 1, size: 20, description: "你好", role: "user", timestamp: Date.now() - 3600000 },
          { id: 2, name: "AI 1", group: 2, size: 25, description: "你好！我是你的智能助手，有什么我可以帮助你的吗？", role: "ai", timestamp: Date.now() - 3500000 },
          { id: 3, name: "用户 2", group: 1, size: 20, description: "今天天气怎么样？", role: "user", timestamp: Date.now() - 3400000 },
          { id: 4, name: "AI 2", group: 2, size: 22, description: "抱歉，我无法实时获取天气信息，但你可以通过天气应用或网站查看最新天气。", role: "ai", timestamp: Date.now() - 3300000 }
        ],
        links: [
          { source: 1, target: 2, value: 1 },
          { source: 2, target: 3, value: 1 },
          { source: 3, target: 4, value: 1 }
        ]
      };
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
        description: node.description || '',
        role: node.role || 'ai',
        timestamp: node.timestamp || Date.now()
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
    }
  }
});