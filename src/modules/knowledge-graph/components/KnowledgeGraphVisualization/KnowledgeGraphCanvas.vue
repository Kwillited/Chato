<template>
  <!-- 知识图谱Canvas可视化容器 -->
  <div class="w-full h-full relative">
    <canvas ref="knowledgeGraphCanvasRef" class="w-full h-full border border-gray-200 dark:border-gray-700 rounded-lg"></canvas>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue';

// 定义组件属性
const props = defineProps({
  // 知识图谱节点数据
  nodes: {
    type: Array,
    default: () => []
  },
  // 知识图谱连线数据
  links: {
    type: Array,
    default: () => []
  },
  // 是否显示Canvas
  visible: {
    type: Boolean,
    default: true
  }
});

// 定义组件事件
const emit = defineEmits(['node-click', 'node-hover', 'view-changed']);

// 节流函数工具
const throttle = (func, limit) => {
  let inThrottle = false;
  return function(...args) {
    const context = this;
    if (!inThrottle) {
      func.apply(context, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
};

// Canvas相关引用和状态
const knowledgeGraphCanvasRef = ref(null);
const knowledgeGraphCanvasContext = ref(null);
const offscreenCanvas = ref(null);
const offscreenContext = ref(null);
const animationFrameId = ref(null);

// 帧率控制
const targetFPS = ref(60); // 目标帧率
const minFPS = ref(15); // 最小帧率
const frameInterval = ref(1000 / targetFPS.value); // 每帧间隔时间（毫秒）
const lastFrameTime = ref(0); // 上一帧时间戳

// 知识图谱数据
const knowledgeGraphNodes = ref([]);
const knowledgeGraphLinks = ref([]);

// 交互相关状态
const isDragging = ref(false);
const draggedNode = ref(null);
const hoveredNode = ref(null);
const mousePos = ref({ x: 0, y: 0 });

// 缩放相关状态
const scale = ref(1.0);
const minScale = ref(0.5);
const maxScale = ref(3.0);
const scaleSpeed = ref(0.1);
const origin = ref({ x: 0, y: 0 });
const isPanning = ref(false);
const panStart = ref({ x: 0, y: 0 });

// 监听节点和连线数据变化
watch(() => props.nodes, (newNodes) => {
  knowledgeGraphNodes.value = newNodes;
  if (knowledgeGraphCanvasContext.value) {
    // 重新生成节点和连线
    generateKnowledgeGraphData();
  }
}, { deep: true });

watch(() => props.links, (newLinks) => {
  knowledgeGraphLinks.value = newLinks;
  if (knowledgeGraphCanvasContext.value) {
    // 重新生成节点和连线
    generateKnowledgeGraphData();
  }
}, { deep: true });

// 初始化知识图谱Canvas
const initKnowledgeGraphCanvas = () => {
  if (!knowledgeGraphCanvasRef.value) return;
  
  const canvas = knowledgeGraphCanvasRef.value;
  const ctx = canvas.getContext('2d');
  knowledgeGraphCanvasContext.value = ctx;
  
  // 设置Canvas尺寸
  const container = canvas.parentElement;
  canvas.width = container.clientWidth;
  canvas.height = container.clientHeight;
  
  // 初始化离屏Canvas
  offscreenCanvas.value = document.createElement('canvas');
  offscreenCanvas.value.width = canvas.width;
  offscreenCanvas.value.height = canvas.height;
  offscreenContext.value = offscreenCanvas.value.getContext('2d');
  
  // 生成知识图谱数据
  generateKnowledgeGraphData();
  
  // 添加鼠标事件监听器
  addKnowledgeGraphMouseEventListeners(canvas);
  
  // 开始动画
  animateKnowledgeGraph();
};

// 生成知识图谱数据
const generateKnowledgeGraphData = () => {
  // 如果提供了外部节点数据，则使用外部数据
  if (props.nodes.length > 0) {
    // 为外部节点添加必要的属性（位置、速度等）
    const canvas = knowledgeGraphCanvasRef.value;
    const nodeWidth = canvas ? canvas.width : 800;
    const nodeHeight = canvas ? canvas.height : 600;
    
    knowledgeGraphNodes.value = props.nodes.map(node => {
      return {
        ...node,
        // 如果节点没有位置或速度属性，添加默认值
        x: node.x !== undefined ? node.x : Math.random() * nodeWidth,
        y: node.y !== undefined ? node.y : Math.random() * nodeHeight,
        vx: node.vx !== undefined ? node.vx : (Math.random() - 0.5) * 0.5,
        vy: node.vy !== undefined ? node.vy : (Math.random() - 0.5) * 0.5
      };
    });
    
    // 使用外部连线数据，如果没有则生成随机连线
    knowledgeGraphLinks.value = props.links.length > 0 
      ? props.links 
      : generateRandomLinks(knowledgeGraphNodes.value.length);
  } else {
    // 否则生成示例数据
    generateExampleKnowledgeGraphData();
  }
};

// 生成随机连线
const generateRandomLinks = (nodeCount) => {
  const links = [];
  for (let i = 0; i < nodeCount; i++) {
    for (let j = i + 1; j < nodeCount; j++) {
      if (Math.random() < 0.15) { // 15%的概率生成连线
        links.push({
          source: i,
          target: j
        });
      }
    }
  }
  return links;
};

// 生成示例知识图谱数据
const generateExampleKnowledgeGraphData = () => {
  // 清空之前的数据
  knowledgeGraphNodes.value = [];
  knowledgeGraphLinks.value = [];
  
  // 示例节点数据
  const exampleNodes = [
    { id: 1, name: "人工智能", type: "concept", x: 100, y: 100, vx: 0, vy: 0, radius: 25, color: "#3B82F6" },
    { id: 2, name: "机器学习", type: "concept", x: 200, y: 150, vx: 0, vy: 0, radius: 20, color: "#10B981" },
    { id: 3, name: "深度学习", type: "concept", x: 300, y: 200, vx: 0, vy: 0, radius: 18, color: "#F59E0B" },
    { id: 4, name: "神经网络", type: "concept", x: 400, y: 150, vx: 0, vy: 0, radius: 16, color: "#EF4444" },
    { id: 5, name: "计算机视觉", type: "application", x: 250, y: 300, vx: 0, vy: 0, radius: 20, color: "#8B5CF6" },
    { id: 6, name: "自然语言处理", type: "application", x: 150, y: 250, vx: 0, vy: 0, radius: 20, color: "#EC4899" }
  ];
  
  // 示例连线数据
  const exampleLinks = [
    { source: 0, target: 1 },
    { source: 1, target: 2 },
    { source: 2, target: 3 },
    { source: 1, target: 4 },
    { source: 1, target: 5 },
    { source: 0, target: 5 }
  ];
  
  // 随机化节点位置
  exampleNodes.forEach(node => {
    const canvas = knowledgeGraphCanvasRef.value;
    if (canvas) {
      node.x = Math.random() * canvas.width;
      node.y = Math.random() * canvas.height;
      node.vx = (Math.random() - 0.5) * 0.5;
      node.vy = (Math.random() - 0.5) * 0.5;
    }
  });
  
  knowledgeGraphNodes.value = exampleNodes;
  knowledgeGraphLinks.value = exampleLinks;
};

// 添加鼠标事件监听器
const addKnowledgeGraphMouseEventListeners = (canvas) => {
  // 创建节流后的事件处理函数
  const throttledMouseMove = throttle(handleKnowledgeGraphMouseMove, 16); // 约60fps
  const throttledMouseWheel = throttle(handleKnowledgeGraphMouseWheel, 16); // 约60fps
  
  // 存储节流函数引用，以便后续移除
  canvas._throttledMouseMove = throttledMouseMove;
  canvas._throttledMouseWheel = throttledMouseWheel;
  
  // 鼠标按下事件
  canvas.addEventListener('mousedown', handleKnowledgeGraphMouseDown);
  
  // 鼠标移动事件（节流处理）
  canvas.addEventListener('mousemove', throttledMouseMove);
  
  // 鼠标抬起事件
  canvas.addEventListener('mouseup', handleKnowledgeGraphMouseUp);
  
  // 鼠标离开事件
  canvas.addEventListener('mouseleave', handleKnowledgeGraphMouseLeave);
  
  // 鼠标滚轮事件（用于缩放，节流处理）
  canvas.addEventListener('wheel', throttledMouseWheel);
};

// 移除鼠标事件监听器
const removeKnowledgeGraphMouseEventListeners = (canvas) => {
  canvas.removeEventListener('mousedown', handleKnowledgeGraphMouseDown);
  
  // 移除节流后的鼠标移动事件
  if (canvas._throttledMouseMove) {
    canvas.removeEventListener('mousemove', canvas._throttledMouseMove);
    delete canvas._throttledMouseMove;
  } else {
    canvas.removeEventListener('mousemove', handleKnowledgeGraphMouseMove);
  }
  
  canvas.removeEventListener('mouseup', handleKnowledgeGraphMouseUp);
  canvas.removeEventListener('mouseleave', handleKnowledgeGraphMouseLeave);
  
  // 移除节流后的鼠标滚轮事件
  if (canvas._throttledMouseWheel) {
    canvas.removeEventListener('wheel', canvas._throttledMouseWheel);
    delete canvas._throttledMouseWheel;
  } else {
    canvas.removeEventListener('wheel', handleKnowledgeGraphMouseWheel);
  }
};

// 获取鼠标在Canvas中的坐标
const getKnowledgeGraphMousePos = (canvas, event) => {
  const rect = canvas.getBoundingClientRect();
  return {
    x: event.clientX - rect.left,
    y: event.clientY - rect.top
  };
};

// 检查节点是否在可视区域内
const isNodeInViewport = (node) => {
  const canvas = knowledgeGraphCanvasRef.value;
  if (!canvas) return true;
  
  // 将节点坐标转换为屏幕坐标
  const screenX = node.x * scale.value + origin.value.x;
  const screenY = node.y * scale.value + origin.value.y;
  
  // 考虑节点半径和一些边距，确保节点完全可见
  const margin = Math.max(node.radius * scale.value, 50);
  
  return (
    screenX + margin >= 0 &&
    screenX - margin <= canvas.width &&
    screenY + margin >= 0 &&
    screenY - margin <= canvas.height
  );
};

// 检查鼠标是否在节点内（考虑缩放和平移）
const isMouseInKnowledgeGraphNode = (node, mouseX, mouseY) => {
  // 将鼠标坐标转换为世界坐标
  const worldX = (mouseX - origin.value.x) / scale.value;
  const worldY = (mouseY - origin.value.y) / scale.value;
  
  const dx = node.x - worldX;
  const dy = node.y - worldY;
  return Math.sqrt(dx * dx + dy * dy) <= node.radius;
};

// 处理鼠标滚轮事件（缩放）
const handleKnowledgeGraphMouseWheel = (event) => {
  event.preventDefault();
  
  const canvas = knowledgeGraphCanvasRef.value;
  if (!canvas) return;
  
  const mouse = getKnowledgeGraphMousePos(canvas, event);
  
  // 计算缩放因子
  const delta = event.deltaY > 0 ? -scaleSpeed.value : scaleSpeed.value;
  const newScale = Math.max(minScale.value, Math.min(maxScale.value, scale.value + delta));
  
  // 计算缩放原点（鼠标位置）
  const scaleFactor = newScale / scale.value;
  
  // 更新原点位置，使缩放以鼠标位置为中心
  origin.value.x = mouse.x - (mouse.x - origin.value.x) * scaleFactor;
  origin.value.y = mouse.y - (mouse.y - origin.value.y) * scaleFactor;
  
  // 更新缩放比例
  scale.value = newScale;
  
  // 触发视图变化事件
  emit('view-changed', { scale: scale.value, origin: origin.value });
};

// 处理鼠标按下事件
const handleKnowledgeGraphMouseDown = (event) => {
  const canvas = knowledgeGraphCanvasRef.value;
  if (!canvas) return;
  
  const mouse = getKnowledgeGraphMousePos(canvas, event);
  
  // 检查是否点击了节点
  let clickedNode = null;
  for (let i = knowledgeGraphNodes.value.length - 1; i >= 0; i--) {
    const node = knowledgeGraphNodes.value[i];
    if (isMouseInKnowledgeGraphNode(node, mouse.x, mouse.y)) {
      clickedNode = node;
      break;
    }
  }
  
  if (clickedNode) {
    // 点击了节点，开始拖拽节点
    isDragging.value = true;
    draggedNode.value = clickedNode;
    mousePos.value = mouse;
    
    // 触发节点点击事件
    emit('node-click', clickedNode);
  } else {
    // 没有点击节点，开始平移
    if (event.button === 0 || event.button === 1) { // 左键或中键
      event.preventDefault();
      isPanning.value = true;
      panStart.value = mouse;
      canvas.style.cursor = 'grabbing';
    }
  }
};

// 处理鼠标移动事件
const handleKnowledgeGraphMouseMove = (event) => {
  const canvas = knowledgeGraphCanvasRef.value;
  if (!canvas) return;
  
  const mouse = getKnowledgeGraphMousePos(canvas, event);
  mousePos.value = mouse;
  
  // 处理平移
  if (isPanning.value) {
    // 计算平移距离
    const dx = mouse.x - panStart.value.x;
    const dy = mouse.y - panStart.value.y;
    
    // 更新原点位置
    origin.value.x += dx;
    origin.value.y += dy;
    
    // 更新平移起点
    panStart.value = mouse;
    
    // 触发视图变化事件
    emit('view-changed', { scale: scale.value, origin: origin.value });
  } 
  // 处理拖拽
  else if (isDragging.value && draggedNode.value) {
    // 将鼠标坐标转换为世界坐标（考虑缩放和平移）
    const worldX = (mouse.x - origin.value.x) / scale.value;
    const worldY = (mouse.y - origin.value.y) / scale.value;
    
    draggedNode.value.x = worldX;
    draggedNode.value.y = worldY;
    draggedNode.value.vx = 0;
    draggedNode.value.vy = 0;
  } 
  // 处理悬停效果
  else {
    let foundHoveredNode = null;
    for (const node of knowledgeGraphNodes.value) {
      if (isMouseInKnowledgeGraphNode(node, mouse.x, mouse.y)) {
        foundHoveredNode = node;
        break;
      }
    }
    
    if (hoveredNode.value !== foundHoveredNode) {
      hoveredNode.value = foundHoveredNode;
      // 触发节点悬停事件
      emit('node-hover', foundHoveredNode);
    }
    
    // 设置鼠标指针样式
    if (foundHoveredNode) {
      canvas.style.cursor = 'pointer';
    } else {
      canvas.style.cursor = 'default';
    }
  }
};

// 处理鼠标抬起事件
const handleKnowledgeGraphMouseUp = () => {
  isDragging.value = false;
  isPanning.value = false;
  draggedNode.value = null;
  
  const canvas = knowledgeGraphCanvasRef.value;
  if (canvas) {
    canvas.style.cursor = 'default';
  }
};

// 处理鼠标离开事件
const handleKnowledgeGraphMouseLeave = () => {
  isDragging.value = false;
  isPanning.value = false;
  draggedNode.value = null;
  hoveredNode.value = null;
  
  const canvas = knowledgeGraphCanvasRef.value;
  if (canvas) {
    canvas.style.cursor = 'default';
  }
  
  // 触发节点悬停事件，通知悬停结束
  emit('node-hover', null);
};

// 清理Canvas资源
const cleanupKnowledgeGraphCanvas = () => {
  if (animationFrameId.value) {
    cancelAnimationFrame(animationFrameId.value);
    animationFrameId.value = null;
  }
  
  // 移除鼠标事件监听器
  if (knowledgeGraphCanvasRef.value) {
    removeKnowledgeGraphMouseEventListeners(knowledgeGraphCanvasRef.value);
    // 重置鼠标样式
    knowledgeGraphCanvasRef.value.style.cursor = 'default';
  }
  
  // 重置缩放和平移状态
  scale.value = 1.0;
  origin.value = { x: 0, y: 0 };
  isPanning.value = false;
  panStart.value = { x: 0, y: 0 };
  
  // 清理离屏Canvas
  offscreenCanvas.value = null;
  offscreenContext.value = null;
  
  knowledgeGraphCanvasContext.value = null;
  hoveredNode.value = null;
  draggedNode.value = null;
  isDragging.value = false;
};

// 绘制知识图谱节点
const drawKnowledgeGraphNodes = () => {
  const ctx = offscreenContext.value;
  const canvas = knowledgeGraphCanvasRef.value;
  if (!ctx || !canvas) return;
  
  // 只绘制可视区域内的节点，或拖拽/悬停状态的节点
  const visibleNodes = knowledgeGraphNodes.value.filter(node => 
    isNodeInViewport(node) || node === hoveredNode.value || node === draggedNode.value
  );
  
  visibleNodes.forEach(node => {
    // 确定节点半径和样式
    let radius = node.radius;
    let strokeWidth = 2;
    let strokeColor = '#2C3E50';
    
    // 悬停效果
    if (node === hoveredNode.value && !isDragging.value) {
      radius += 5; // 悬停时增大半径
      strokeWidth = 3;
      strokeColor = '#3B82F6'; // 蓝色高亮
    }
    
    // 拖拽效果
    if (node === draggedNode.value) {
      strokeWidth = 4;
      strokeColor = '#EF4444'; // 红色高亮
    }
    
    // 绘制节点阴影
    ctx.beginPath();
    ctx.arc(node.x, node.y, radius + 2, 0, Math.PI * 2);
    ctx.fillStyle = 'rgba(0, 0, 0, 0.1)';
    ctx.fill();
    
    // 绘制节点
    ctx.beginPath();
    ctx.arc(node.x, node.y, radius, 0, Math.PI * 2);
    ctx.fillStyle = node.color;
    ctx.fill();
    ctx.strokeStyle = strokeColor;
    ctx.lineWidth = strokeWidth;
    ctx.stroke();
    
    // 绘制节点名称
    ctx.fillStyle = '#FFFFFF';
    ctx.font = '12px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(node.name.substring(0, 8), node.x, node.y);
    
    // 绘制完整节点名称提示（当悬停时）
    if (node === hoveredNode.value && !isDragging.value) {
      ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
      ctx.font = '12px Arial';
      const textWidth = ctx.measureText(node.name).width;
      const padding = 8;
      
      // 绘制背景矩形
      ctx.fillRect(
        node.x - textWidth / 2 - padding,
        node.y - radius - 25,
        textWidth + padding * 2,
        20
      );
      
      // 绘制文本
      ctx.fillStyle = '#FFFFFF';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(node.name, node.x, node.y - radius - 15);
    }
  });
};

// 绘制知识图谱连线
const drawKnowledgeGraphLinks = () => {
  const ctx = offscreenContext.value;
  if (!ctx) return;
  
  // 只绘制连接可视区域内节点的连线
  const visibleNodeIds = new Set(
    knowledgeGraphNodes.value
      .filter(node => isNodeInViewport(node) || node === hoveredNode.value || node === draggedNode.value)
      .map(node => node.id)
  );
  
  knowledgeGraphLinks.value.forEach(link => {
    const source = knowledgeGraphNodes.value[link.source];
    const target = knowledgeGraphNodes.value[link.target];
    
    // 只有当至少一个节点在可视区域内时才绘制连线
    if (visibleNodeIds.has(source.id) || visibleNodeIds.has(target.id)) {
      ctx.beginPath();
      ctx.moveTo(source.x, source.y);
      ctx.lineTo(target.x, target.y);
      ctx.strokeStyle = '#95A5A6';
      ctx.lineWidth = 1;
      ctx.stroke();
    }
  });
};

// 更新知识图谱节点位置（优化的力导向算法）
const updateKnowledgeGraphNodes = () => {
  const canvas = knowledgeGraphCanvasRef.value;
  if (!canvas) return;
  
  const springLength = 150; // 弹簧长度
  const springStrength = 0.00005; // 弹簧强度
  const repulsionStrength = 2000; // 排斥力强度
  const friction = 0.92; // 摩擦力
  const maxRepulsionDistance = 300; // 最大排斥力计算距离，超过此距离不计算排斥力
  
  // 只对非拖拽节点应用力
  const nonDraggedNodes = knowledgeGraphNodes.value.filter(node => node !== draggedNode.value);
  
  // 分离可视节点和非可视节点
  const visibleNodes = nonDraggedNodes.filter(node => isNodeInViewport(node));
  const nonVisibleNodes = nonDraggedNodes.filter(node => !isNodeInViewport(node));
  
  // 应用排斥力 - 仅对可视节点和它们的邻居应用完整排斥力计算
  // 1. 可视节点之间的排斥力
  for (let i = 0; i < visibleNodes.length; i++) {
    for (let j = i + 1; j < visibleNodes.length; j++) {
      const nodeA = visibleNodes[i];
      const nodeB = visibleNodes[j];
      
      const dx = nodeA.x - nodeB.x;
      const dy = nodeA.y - nodeB.y;
      const distanceSquared = dx * dx + dy * dy;
      
      // 跳过距离太远的节点，减少计算量
      if (distanceSquared > maxRepulsionDistance * maxRepulsionDistance) {
        continue;
      }
      
      const distance = Math.sqrt(distanceSquared);
      if (distance > 0) {
        // 使用库仑定律风格的排斥力
        const force = repulsionStrength / distanceSquared;
        const fx = (dx / distance) * force;
        const fy = (dy / distance) * force;
        
        nodeA.vx += fx;
        nodeA.vy += fy;
        nodeB.vx -= fx;
        nodeB.vy -= fy;
      }
    }
  }
  
  // 2. 可视节点与非可视节点之间的排斥力（简化计算，减少精度要求）
  for (const visibleNode of visibleNodes) {
    for (const nonVisibleNode of nonVisibleNodes) {
      const dx = visibleNode.x - nonVisibleNode.x;
      const dy = visibleNode.y - nonVisibleNode.y;
      const distanceSquared = dx * dx + dy * dy;
      
      // 跳过距离太远的节点
      if (distanceSquared > maxRepulsionDistance * maxRepulsionDistance) {
        continue;
      }
      
      const distance = Math.sqrt(distanceSquared);
      if (distance > 0) {
        // 使用简化的排斥力计算
        const force = (repulsionStrength * 0.5) / distanceSquared; // 降低强度
        const fx = (dx / distance) * force;
        const fy = (dy / distance) * force;
        
        // 只对可视节点应用此排斥力，减少计算量
        visibleNode.vx += fx;
        visibleNode.vy += fy;
      }
    }
  }
  
  // 应用弹簧力
  knowledgeGraphLinks.value.forEach(link => {
    const nodeA = knowledgeGraphNodes.value[link.source];
    const nodeB = knowledgeGraphNodes.value[link.target];
    
    // 跳过拖拽节点的弹簧力
    if (nodeA === draggedNode.value || nodeB === draggedNode.value) {
      return;
    }
    
    const dx = nodeA.x - nodeB.x;
    const dy = nodeA.y - nodeB.y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    
    // 只对距离合理的节点应用弹簧力
    if (distance > 0 && distance < springLength * 3) {
      const springForce = (distance - springLength) * springStrength;
      
      const fx = (dx / distance) * springForce;
      const fy = (dy / distance) * springForce;
      
      // 根据节点是否可见调整弹簧力强度
      const nodeAvisible = isNodeInViewport(nodeA);
      const nodeBvisible = isNodeInViewport(nodeB);
      
      if (nodeAvisible) {
        nodeA.vx -= fx;
        nodeA.vy -= fy;
      }
      
      if (nodeBvisible) {
        nodeB.vx += fx;
        nodeB.vy += fy;
      }
    }
  });
  
  // 更新节点位置并应用摩擦力
  // 只对可视节点应用完整更新，非可视节点只做简单更新
  nonDraggedNodes.forEach(node => {
    const isVisible = isNodeInViewport(node);
    
    // 可视节点应用完整更新
    if (isVisible) {
      node.vx *= friction;
      node.vy *= friction;
      
      node.x += node.vx;
      node.y += node.vy;
      
      // 边界检查 - 确保节点始终在可视区域内
      // 计算世界坐标系下的可视区域边界
      // 可视区域的左上角在世界坐标系中的位置
      const viewLeft = -origin.value.x / scale.value;
      const viewTop = -origin.value.y / scale.value;
      // 可视区域的右下角在世界坐标系中的位置
      const viewRight = viewLeft + canvas.width / scale.value;
      const viewBottom = viewTop + canvas.height / scale.value;
      
      // 确保节点在可视区域内
      node.x = Math.max(viewLeft + node.radius, Math.min(viewRight - node.radius, node.x));
      node.y = Math.max(viewTop + node.radius, Math.min(viewBottom - node.radius, node.y));
    } else {
      // 非可视节点只做简单更新，降低计算量
      node.vx *= (friction + 0.05); // 更强的摩擦力，减少不必要的运动
      node.vy *= (friction + 0.05);
      
      node.x += node.vx * 0.5; // 降低更新幅度
      node.y += node.vy * 0.5;
      
      // 非可视节点的边界检查 - 使用更宽松的边界
      // 为非可视节点提供更大的移动空间，只做基本限制
      // 计算世界坐标系下的画布尺寸
      const worldWidth = canvas.width / scale.value;
      const worldHeight = canvas.height / scale.value;
      
      // 允许节点在更大的范围内移动（当前可视区域的3倍）
      const maxBound = 3;
      node.x = Math.max(-worldWidth * maxBound, Math.min(worldWidth * maxBound, node.x));
      node.y = Math.max(-worldHeight * maxBound, Math.min(worldHeight * maxBound, node.y));
    }
  });
};

// 知识图谱动画循环
const animateKnowledgeGraph = (timestamp) => {
  if (!knowledgeGraphCanvasContext.value || !knowledgeGraphCanvasRef.value || !offscreenContext.value) return;
  
  const ctx = knowledgeGraphCanvasContext.value;
  const canvas = knowledgeGraphCanvasRef.value;
  const offCtx = offscreenContext.value;
  if (!ctx || !canvas || !offCtx) return;
  
  // 计算时间差
  const deltaTime = timestamp - lastFrameTime.value;
  
  // 如果时间差大于等于帧间隔，则执行渲染
  if (deltaTime >= frameInterval.value) {
    // 更新上一帧时间戳
    lastFrameTime.value = timestamp;
    
    // 确保离屏Canvas尺寸与可视Canvas一致
    if (offscreenCanvas.value.width !== canvas.width || offscreenCanvas.value.height !== canvas.height) {
      offscreenCanvas.value.width = canvas.width;
      offscreenCanvas.value.height = canvas.height;
    }
    
    // 清空离屏Canvas
    offCtx.fillStyle = '#F8FAFC';
    if (document.documentElement.classList.contains('dark')) {
      offCtx.fillStyle = '#1E293B';
    }
    offCtx.fillRect(0, 0, canvas.width, canvas.height);
    
    // 应用缩放和平移变换到离屏Canvas
    offCtx.save();
    offCtx.translate(origin.value.x, origin.value.y);
    offCtx.scale(scale.value, scale.value);
    
    // 更新节点位置
    updateKnowledgeGraphNodes();
    
    // 绘制连线到离屏Canvas
    drawKnowledgeGraphLinks();
    
    // 绘制节点到离屏Canvas
    drawKnowledgeGraphNodes();
    
    // 恢复变换
    offCtx.restore();
    
    // 将离屏Canvas的内容一次性绘制到可视Canvas上
    ctx.drawImage(offscreenCanvas.value, 0, 0);
    
    // 动态调整帧率
    const actualFPS = 1000 / deltaTime;
    if (actualFPS < minFPS.value) {
      // 如果实际帧率低于最小帧率，降低目标帧率
      targetFPS.value = Math.max(minFPS.value, targetFPS.value - 5);
      frameInterval.value = 1000 / targetFPS.value;
    } else if (actualFPS > targetFPS.value + 10 && targetFPS.value < 60) {
      // 如果实际帧率远高于目标帧率，提高目标帧率
      targetFPS.value = Math.min(60, targetFPS.value + 5);
      frameInterval.value = 1000 / targetFPS.value;
    }
  }
  
  // 请求下一帧动画
  animationFrameId.value = requestAnimationFrame(animateKnowledgeGraph);
};

// 处理窗口大小变化
const handleKnowledgeGraphResize = () => {
  if (!knowledgeGraphCanvasRef.value || !props.visible) return;
  
  cleanupKnowledgeGraphCanvas();
  nextTick(() => {
    initKnowledgeGraphCanvas();
  });
};

// 组件挂载时初始化
onMounted(() => {
  if (props.visible) {
    nextTick(() => {
      initKnowledgeGraphCanvas();
    });
  }
  
  // 监听窗口大小变化
  window.addEventListener('resize', handleKnowledgeGraphResize);
});

// 组件卸载时清理
onUnmounted(() => {
  cleanupKnowledgeGraphCanvas();
  
  // 移除窗口大小变化监听
  window.removeEventListener('resize', handleKnowledgeGraphResize);
});

// 监听visible属性变化
watch(() => props.visible, (newVisible) => {
  if (newVisible) {
    nextTick(() => {
      initKnowledgeGraphCanvas();
    });
  } else {
    cleanupKnowledgeGraphCanvas();
  }
});
</script>

<style scoped>
/* 知识图谱Canvas样式 */
canvas {
  transition: all 0.3s ease;
  border-radius: 12px;
  display: block;
}
</style>