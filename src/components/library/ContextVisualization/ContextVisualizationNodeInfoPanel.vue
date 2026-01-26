<template>
  <!-- 右侧信息面板 - 用于显示点击节点的详细信息 -->
  <div v-if="selectedNode" id="nodeInfoPanel" class="absolute top-10 right-4 h-[calc(100%-60px)] w-[16rem] bg-dark/80 backdrop-blur-md z-40 border-l border-primary/20 flex flex-col transform transition-transform duration-300 rounded-[20px] overflow-hidden">
    <div class="p-3 flex justify-between items-center border-b border-primary/20">
      <h2 class="text-lg font-bold text-primary">节点信息</h2>
      <button
        class="w-8 h-8 p-1.5 flex items-center justify-center text-neutral hover:text-primary hover:bg-primary/10 rounded-full transition-colors"
        title="关闭信息面板"
        @click="onCloseModal"
      >
        <i class="fa-solid fa-xmark"></i>
      </button>
    </div>

    <div class="overflow-y-auto flex-1 p-4 space-y-6">
      <!-- 节点名称和描述 -->
      <div class="mb-6">
        <h3 class="text-xl font-bold text-primary mb-2">{{ selectedNode.name }}</h3>
        <p class="text-gray-300 text-sm">{{ selectedNode.description }}</p>
      </div>
      
      <!-- 节点属性 -->
      <div class="mb-6 border-b border-gray-700/50 pb-4">
        <h4 class="text-primary font-semibold mb-2">节点属性</h4>
        <div class="space-y-2 text-sm">
          <div class="flex justify-between">
            <span class="text-gray-400">ID:</span>
            <span class="text-gray-200">{{ selectedNode.id }}</span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-400">组:</span>
            <span class="text-gray-200 flex items-center">
              <span class="w-2 h-2 rounded-full mr-2" :style="{ backgroundColor: getNodeColor(selectedNode.group) }"></span>
              {{ selectedNode.group }}
            </span>
          </div>
          <div class="flex justify-between">
            <span class="text-gray-400">大小:</span>
            <span class="text-gray-200">{{ selectedNode.size }}</span>
          </div>
        </div>
      </div>
      
      <!-- 相关节点 -->
      <div class="mb-6 border-b border-gray-700/50 pb-4">
        <h4 class="text-primary font-semibold mb-2">相关节点 ({{ relatedNodes.length }})</h4>
        <div class="space-y-2 text-sm">
          <div v-for="node in relatedNodes" :key="node.id" class="flex items-center justify-between">
            <div class="flex items-center">
              <span class="w-2 h-2 rounded-full mr-2" :style="{ backgroundColor: getNodeColor(node.group) }"></span>
              <span class="text-gray-200">{{ node.name }}</span>
            </div>
            <button 
              class="text-xs text-primary hover:bg-primary/10 px-2 py-1 rounded"
              @click="onShowNodeDetails(node)"
            >
              查看
            </button>
          </div>
        </div>
      </div>
      
      <!-- 节点操作 -->
      <div>
        <h4 class="text-primary font-semibold mb-2">节点操作</h4>
        <div class="flex flex-col gap-2">
          <button 
            class="text-sm py-2 bg-primary/20 hover:bg-primary/30 text-primary rounded-lg transition-colors flex items-center justify-center"
            @click="onFocusOnNode(selectedNode.id)"
          >
            <i class="fa-solid fa-search-plus mr-2"></i> 聚焦节点
          </button>
          <button 
            class="text-sm py-2 bg-gray-800 hover:bg-gray-700 text-neutral rounded-lg transition-colors flex items-center justify-center"
            @click="onToggleNodeVisibility(selectedNode.id)"
          >
            <i class="fa-solid fa-eye-slash mr-2"></i> 隐藏节点
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
// 定义组件的props
const props = defineProps({
  selectedNode: {
    type: Object,
    default: null
  },
  relatedNodes: {
    type: Array,
    default: () => []
  },
  nodeMaterials: {
    type: Array,
    default: () => []
  }
});

// 定义组件的emits
const emit = defineEmits(['closeModal', 'showNodeDetails', 'focusOnNode', 'toggleNodeVisibility']);

// 获取节点颜色
const getNodeColor = (group) => {
  if (!props.nodeMaterials.length) return '#6366f1';
  return props.nodeMaterials[(group - 1) % props.nodeMaterials.length].color.getStyle();
};

// 处理关闭模态框事件
const onCloseModal = () => {
  emit('closeModal');
};

// 处理显示节点详情事件
const onShowNodeDetails = (node) => {
  emit('showNodeDetails', node);
};

// 处理聚焦节点事件
const onFocusOnNode = (nodeId) => {
  emit('focusOnNode', nodeId);
};

// 处理切换节点可见性事件
const onToggleNodeVisibility = (nodeId) => {
  emit('toggleNodeVisibility', nodeId);
};
</script>

<style scoped>
/* 自定义设置面板内部滚动条样式 - 隐藏滚动条但保持滚动功能 */
#nodeInfoPanel .overflow-y-auto {
  /* Firefox */
  scrollbar-width: none;
  -ms-overflow-style: none;
}

/* Chrome, Edge, and Safari */
#nodeInfoPanel .overflow-y-auto::-webkit-scrollbar {
  display: none;
}
</style>