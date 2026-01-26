<template>
  <!-- 上下文可视化主容器 - 调整样式使其与ChatMessagesContainer风格一致 -->
  <div ref="contextVisualizationContainer" class="relative flex-1 w-full bg-gradient-subtle text-light overflow-hidden font-inter scrollbar-thin">
    <!-- 左侧设置面板组件 -->
    <ContextVisualizationSettingsPanel
      :showSettingsPanel="showSettingsPanel"
      :settings="settings"
      :activeTooltip="activeTooltip"
      :tooltipStyle="tooltipStyle"
      @toggleSettingsPanel="toggleSettingsPanel"
      @handleParticleCountChange="handleParticleCountChange"
      @handleParticleSizeChange="handleParticleSizeChange"
      @handleParticleOpacityChange="handleParticleOpacityChange"
      @handleRotationSpeedChange="handleRotationSpeedChange"
      @resetSettings="resetSettings"
      @showTooltip="showTooltip"
      @hideTooltip="hideTooltip"
    />
      <!-- 导航栏组件 -->
      <ContextVisualizationNavigation 
        :selectedNode="selectedNode" 
        @settingsClick="toggleSettingsPanel" 
        @menuClick="selectedNode ? closeModal() : showNodeDetails(contextStore.graphData.nodes[0])" 
      />
      
      <!-- 3D上下文可视化渲染组件 -->
      <ContextVisualizationRenderer />
      
      <!-- 右侧信息面板组件 -->
      <ContextVisualizationNodeInfoPanel
        :selectedNode="selectedNode"
        :relatedNodes="relatedNodes"
        :nodeMaterials="nodeMaterials"
        @closeModal="closeModal"
        @showNodeDetails="showNodeDetails"
        @focusOnNode="focusOnNode"
        @toggleNodeVisibility="toggleNodeVisibility"
      />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, reactive, provide } from 'vue';

// 导入本地存储管理工具
import { StorageManager } from '../../../store/utils.js';

// 引入上下文可视化相关组件
import ContextVisualizationNavigation from './ContextVisualizationNavigation.vue';
import ContextVisualizationSettingsPanel from './ContextVisualizationSettingsPanel.vue';
import ContextVisualizationNodeInfoPanel from './ContextVisualizationNodeInfoPanel.vue';

import ContextVisualizationRenderer from './ContextVisualizationRenderer.vue';

// 引入 Three.js 库（仅用于材质定义）
import * as THREE from 'three';

// 导入上下文存储
import { useContextVisualizationStore } from '../../../store/contextVisualizationStore.js';

// 创建星空背景函数
const createStars = (scene, config) => {
  // 如果已经存在星空，先移除
  if (starsRef.value && scene) {
    scene.remove(starsRef.value);
  }
  
  const geometry = new THREE.BufferGeometry();
  const count = config.particleCount;
  const positions = new Float32Array(count * 3);
  
  for (let i = 0; i < count; i++) {
    const i3 = i * 3;
    positions[i3] = (Math.random() - 0.5) * 2000;
    positions[i3 + 1] = (Math.random() - 0.5) * 2000;
    positions[i3 + 2] = (Math.random() - 0.5) * 2000;
  }
  
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  
  const material = new THREE.PointsMaterial({
    color: 0xffffff,
    size: config.particleSize,
    transparent: true,
    opacity: config.particleOpacity
  });
  
  const stars = new THREE.Points(geometry, material);
  
  // 根据配置决定是否显示星空
  if (config.showBackground && scene) {
    scene.add(stars);
  }
  
  return stars;
};

// 初始化上下文存储
const contextStore = useContextVisualizationStore();

// 响应式状态
const selectedNode = ref(null);
const relatedNodes = ref([]);
const nodeMaterials = ref([]);
const contextVisualizationContainer = ref(null);
const infoPanel = ref(null);
const showSettingsPanel = ref(false);
const activeTooltip = ref('');
const tooltipStyle = ref({});
const hiddenNodes = ref(new Set()); // 用于跟踪隐藏的节点
const starsRef = ref(null); // 用于跟踪星空粒子系统

// 存储键名常量
const STORAGE_KEY = 'contextVisualizationBackgroundSettings';

const defaultSettings = {
  particleCount: 2000,
  particleSize: 1.5,
  particleOpacity: 0.8,
  rotationSpeed: 0.0001,
  showBackground: true
};
// 从本地存储加载设置（如果有），否则使用默认设置
const savedSettings = StorageManager.getItem(STORAGE_KEY, {});
const settings = reactive({ ...defaultSettings, ...savedSettings });

// 保存设置到本地存储
const saveSettingsToStorage = () => {
  StorageManager.setItem(STORAGE_KEY, { ...settings });
};
const starsConfig = reactive({
  rotationSpeed: settings.rotationSpeed
});



// 关闭模态框 - 恢复节点材质，与text2.vue保持一致
const closeModal = () => {
  selectedNode.value = null;
  relatedNodes.value = [];
};

// 显示节点详情
const showNodeDetails = (node) => {
  selectedNode.value = node;
  
  // 找到相关节点
  const relatedNodeIds = contextStore.graphData.links
    .filter(link => link.source === node.id || link.target === node.id)
    .map(link => link.source === node.id ? link.target : link.source);
  
  relatedNodes.value = relatedNodeIds
    .map(id => contextStore.graphData.nodes.find(n => n.id === id))
    .filter(Boolean);
};

// 初始化节点材质
const initNodeMaterials = () => {
  nodeMaterials.value = [
    new THREE.MeshStandardMaterial({
      color: 0x6366f1,
      emissive: new THREE.Color(0x6366f1).multiplyScalar(0.3),
      emissiveIntensity: 0.3,
      roughness: 0.2,
      metalness: 0.8,
      transparent: true,
      opacity: 0.9
    }),
    new THREE.MeshStandardMaterial({
      color: 0x8b5cf6,
      emissive: new THREE.Color(0x8b5cf6).multiplyScalar(0.3),
      emissiveIntensity: 0.3,
      roughness: 0.2,
      metalness: 0.8,
      transparent: true,
      opacity: 0.9
    }),
    new THREE.MeshStandardMaterial({
      color: 0xec4899,
      emissive: new THREE.Color(0xec4899).multiplyScalar(0.3),
      emissiveIntensity: 0.3,
      roughness: 0.2,
      metalness: 0.8,
      transparent: true,
      opacity: 0.9
    }),
    new THREE.MeshStandardMaterial({
      color: 0x10b981,
      emissive: new THREE.Color(0x10b981).multiplyScalar(0.3),
      emissiveIntensity: 0.3,
      roughness: 0.2,
      metalness: 0.8,
      transparent: true,
      opacity: 0.9
    }),
    new THREE.MeshStandardMaterial({
      color: 0x3b82f6,
      emissive: new THREE.Color(0x3b82f6).multiplyScalar(0.3),
      emissiveIntensity: 0.3,
      roughness: 0.2,
      metalness: 0.8,
      transparent: true,
      opacity: 0.9
    }),
    new THREE.MeshStandardMaterial({
      color: 0xf59e0b,
      emissive: new THREE.Color(0xf59e0b).multiplyScalar(0.3),
      emissiveIntensity: 0.3,
      roughness: 0.2,
      metalness: 0.8,
      transparent: true,
      opacity: 0.9
    }),
    new THREE.MeshStandardMaterial({
      color: 0xef4444,
      emissive: new THREE.Color(0xef4444).multiplyScalar(0.3),
      emissiveIntensity: 0.3,
      roughness: 0.2,
      metalness: 0.8,
      transparent: true,
      opacity: 0.9
    }),
    new THREE.MeshStandardMaterial({
      color: 0x6366f1,
      emissive: new THREE.Color(0x6366f1).multiplyScalar(0.3),
      emissiveIntensity: 0.3,
      roughness: 0.2,
      metalness: 0.8,
      transparent: true,
      opacity: 0.9
    }),
    new THREE.MeshStandardMaterial({
      color: 0x8b5cf6,
      emissive: new THREE.Color(0x8b5cf6).multiplyScalar(0.3),
      emissiveIntensity: 0.3,
      roughness: 0.2,
      metalness: 0.8,
      transparent: true,
      opacity: 0.9
    }),
    new THREE.MeshStandardMaterial({
      color: 0xec4899,
      emissive: new THREE.Color(0xec4899).multiplyScalar(0.3),
      emissiveIntensity: 0.3,
      roughness: 0.2,
      metalness: 0.8,
      transparent: true,
      opacity: 0.9
    }),
    new THREE.MeshStandardMaterial({
      color: 0x10b981,
      emissive: new THREE.Color(0x10b981).multiplyScalar(0.3),
      emissiveIntensity: 0.3,
      roughness: 0.2,
      metalness: 0.8,
      transparent: true,
      opacity: 0.9
    }),
    new THREE.MeshStandardMaterial({
      color: 0x3b82f6,
      emissive: new THREE.Color(0x3b82f6).multiplyScalar(0.3),
      emissiveIntensity: 0.3,
      roughness: 0.2,
      metalness: 0.8,
      transparent: true,
      opacity: 0.9
    })
  ];
};

// 切换设置面板显示/隐藏
const toggleSettingsPanel = () => {
  showSettingsPanel.value = !showSettingsPanel.value;
};

// 处理粒子数量变化
const handleParticleCountChange = (event) => {
  settings.particleCount = parseInt(event.target.value);
  // 重新创建星空
  const scene = starsRef.value?.parent;
  if (scene) {
    starsRef.value = createStars(scene, settings);
  }
  
  // 保存重置后的设置到本地存储
  saveSettingsToStorage();
};

// 处理粒子大小变化
const handleParticleSizeChange = (event) => {
  settings.particleSize = parseFloat(event.target.value);
  if (starsRef.value?.material) {
    starsRef.value.material.size = settings.particleSize;
  }
  // 保存设置到本地存储
  saveSettingsToStorage();
};

// 处理粒子透明度变化
const handleParticleOpacityChange = (event) => {
  settings.particleOpacity = parseFloat(event.target.value);
  if (starsRef.value?.material) {
    starsRef.value.material.opacity = settings.particleOpacity;
  }
  // 保存设置到本地存储
  saveSettingsToStorage();
};

// 处理旋转速度变化
const handleRotationSpeedChange = (event) => {
  settings.rotationSpeed = parseFloat(event.target.value);
  starsConfig.rotationSpeed = settings.rotationSpeed;
  // 保存设置到本地存储
  saveSettingsToStorage();
};

// 重置设置
const resetSettings = () => {
  // 复制默认设置
  Object.assign(settings, defaultSettings);
  starsConfig.rotationSpeed = defaultSettings.rotationSpeed;
  
  // 重新创建星空
  const scene = starsRef.value?.parent;
  if (scene) {
    starsRef.value = createStars(scene, settings);
  }
};

// 显示提示信息
const showTooltip = (tooltipId, event) => {
  activeTooltip.value = tooltipId;
  
  // 计算弹窗位置
  if (event) {
    const rect = event.target.getBoundingClientRect();
    // 获取触发元素的中心点垂直位置
    const triggerCenterY = rect.top + rect.height / 2;
    
    tooltipStyle.value = {
      // 让tooltip顶部对齐触发元素中心点，实现垂直居中
      top: `${triggerCenterY}px`,
      left: `${rect.left}px`,
      // 添加transform使tooltip自身垂直居中
      transform: 'translateY(-50%)'
    };
  }
};

// 隐藏提示信息
const hideTooltip = (tooltipId) => {
  // 如果传入了tooltipId，只隐藏特定的提示
  if (tooltipId) {
    if (activeTooltip.value === tooltipId) {
      activeTooltip.value = '';
    }
  } else {
    // 否则隐藏所有提示
    activeTooltip.value = '';
  }
};

// 聚焦到特定节点
const focusOnNode = (nodeId) => {
  if (!nodeId) return;
  
  // 在组件重构后，相机控制逻辑已移至KnowledgeGraphRenderer组件
  // 此函数现在主要用于触发数据更新
  const node = contextStore.graphData.nodes.find(n => n.id === nodeId);
  if (node) {
    showNodeDetails(node);
  }
};

// 切换节点可见性
const toggleNodeVisibility = (nodeId) => {
  const isCurrentlyHidden = hiddenNodes.value.has(nodeId);
  
  // 更新隐藏节点集合
  if (isCurrentlyHidden) {
    hiddenNodes.value.delete(nodeId);
  } else {
    hiddenNodes.value.add(nodeId);
  }
  
  // 如果隐藏的是当前选中的节点，关闭信息面板
  if (selectedNode.value && selectedNode.value.id === nodeId && !isCurrentlyHidden) {
    closeModal();
  }
  
  // 更新相关连线的可见性
  updateLinksVisibility();
};

// 更新连线的可见性
const updateLinksVisibility = () => {
  // 在组件重构后，这个方法不再直接管理Three.js场景
  // 具体的连线可见性更新逻辑已移至KnowledgeGraphRenderer组件
};

// 立即初始化节点材质，确保子组件注入时已有值
initNodeMaterials();

// 为子组件提供属性和方法
provide('selectedNode', selectedNode);
provide('relatedNodes', relatedNodes);
provide('nodeMaterials', nodeMaterials);
provide('settings', settings);
provide('starsConfig', starsConfig);
provide('hiddenNodes', hiddenNodes);
provide('contextVisualizationContainer', contextVisualizationContainer);
provide('starsRef', starsRef);
provide('graphData', contextStore.graphData);
provide('showNodeDetails', showNodeDetails);
provide('updateLinksVisibility', updateLinksVisibility);
provide('focusOnNode', focusOnNode);
provide('toggleNodeVisibility', toggleNodeVisibility);
provide('graphData', contextStore.graphData);

// 组件挂载时初始化
onMounted(() => {
  initNodeMaterials();
  
  // 1秒后自动隐藏信息面板
  if (infoPanel.value) {
    setTimeout(() => {
      if (infoPanel.value) {
        infoPanel.value.style.opacity = '0';
        setTimeout(() => {
          if (infoPanel.value) {
            infoPanel.value.style.display = 'none';
          }
        }, 500); // 等待过渡动画完成
      }
    }, 1000);
  }
});

// 组件卸载时不需要特殊清理，因为Three.js相关资源由子组件管理
onUnmounted(() => {});
</script>

<style scoped>
.content-auto {
  content-visibility: auto;
}

.text-shadow {
  text-shadow: 0 0 10px rgba(99, 102, 241, 0.8);
}

.glow {
  box-shadow: 0 0 15px rgba(99, 102, 241, 0.6);
}

/* 自定义设置面板内部滚动条样式 - 隐藏滚动条但保持滚动功能 */
#graphSettingsPanel .overflow-y-auto,
#nodeInfoPanel .overflow-y-auto {
  /* Firefox */
  scrollbar-width: none;
  -ms-overflow-style: none;
}

/* Chrome, Edge, and Safari */
#graphSettingsPanel .overflow-y-auto::-webkit-scrollbar,
#nodeInfoPanel .overflow-y-auto::-webkit-scrollbar {
  display: none;
}
</style>