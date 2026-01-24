<template>
  <!-- 3D上下文可视化容器 -->
  <div id="context-visualization" class="absolute inset-0 bg-gradient-universe"></div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, inject, provide } from 'vue';

// 引入 Three.js 库
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import logger from '../../../utils/logger.js';

// 从父组件注入属性和方法
const nodeMaterials = inject('nodeMaterials');
const settings = inject('settings');
const starsConfig = inject('starsConfig');
const showNodeDetails = inject('showNodeDetails');
const starsRef = inject('starsRef');
const containerRef = inject('contextVisualizationContainer');
const contextData = inject('graphData');

// 响应式状态
const animationFrameId = ref(null);

// 获取实际的DOM元素
const getContainer = () => {
  // 如果containerRef是ref对象，返回其值；否则直接返回
  return containerRef && containerRef.value ? containerRef.value : containerRef;
};

// 全局变量，避免Vue响应式代理与Three.js冲突
let contextNodeObjects = [];
let contextNodes = [];



// 初始化3D上下文可视化场景
const initContextScene = () => {
  const container = getContainer();
  if (!container) return () => {};
  
  // 场景、相机和渲染器
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 2000);
  
  // 设置相机位置，使其能够看到节点
  camera.position.z = 680;
  
  // 保存全局引用，以便在其他函数中访问
  window.contextScene = scene;
  window.contextCamera = camera;
  
  // 创建渲染器
  const renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: true,
    powerPreference: "high-performance"
  });
  renderer.setSize(container.clientWidth, container.clientHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.outputEncoding = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1;
  renderer.setClearColor(0x1a202c, 1);
  
  const contextContainer = document.getElementById('context-visualization');
  if (contextContainer) {
    contextContainer.appendChild(renderer.domElement);
  }

  // 添加星空背景
  const stars = createContextStars(scene, settings);
  starsRef.value = stars;

  // 创建节点和连线
  const contextLinks = [];
  const contextLinkObjects = [];
  contextNodeObjects = []; // 清空之前的节点对象
  contextNodes = []; // 清空之前的节点数据

  // 创建上下文节点
  contextData.nodes.forEach(node => {
    const geometry = new THREE.SphereGeometry(node.size / 2, 32, 32);
    const material = nodeMaterials.value[(node.group - 1) % nodeMaterials.value.length];
    const mesh = new THREE.Mesh(geometry, material);
    
    // 添加userData以存储节点ID
    mesh.userData = { contextId: node.id };
    
    // 初始位置给一些随机性，避免所有节点完全重叠
    const radius = 300;
    const theta = Math.random() * Math.PI * 2;
    const phi = Math.acos(Math.random() * 2 - 1);
    
    mesh.position.x = radius * Math.sin(phi) * Math.cos(theta);
    mesh.position.y = radius * Math.sin(phi) * Math.sin(theta);
    mesh.position.z = radius * Math.cos(phi);
      
      // 添加发光效果
      const glowGeometry = new THREE.SphereGeometry(node.size / 2 + 3, 32, 32);
      const glowMaterial = new THREE.ShaderMaterial({
        uniforms: {
          c: { type: 'f', value: 0.8 },
          p: { type: 'f', value: 2.0 },
          glowColor: { type: 'c', value: new THREE.Color(nodeMaterials.value[(node.group - 1) % nodeMaterials.value.length].color) }
        },
        vertexShader: `
          uniform float c;
          uniform float p;
          varying vec3 vNormal;
          varying vec3 vPositionNormal;
          void main() {
            vNormal = normalize(normalMatrix * normal);
            vPositionNormal = normalize((modelMatrix * vec4(position, 1.0)).xyz);
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
          }
        `,
        fragmentShader: `
          uniform vec3 glowColor;
          uniform float c;
          uniform float p;
          varying vec3 vNormal;
          varying vec3 vPositionNormal;
          void main() {
            float intensity = pow(c - dot(vNormal, vPositionNormal), p);
            gl_FragColor = vec4(glowColor, intensity);
          }
        `,
        side: THREE.FrontSide,
        blending: THREE.AdditiveBlending,
        transparent: true
      });
      
      const glowMesh = new THREE.Mesh(glowGeometry, glowMaterial);
      // 设置发光网格不可被射线检测
      glowMesh.raycast = () => {};
      mesh.add(glowMesh);
      
      contextNodeObjects.push(mesh);
      contextNodes.push({ ...node, mesh });
    });
    
    // 使用改进的力导向布局算法优化节点位置
    const applyContextLayout = () => {
      const iterations = 30; // 迭代次数
      const springForce = 0.02; // 增加弹簧力系数
      const repulsionForce = 5000; // 调整排斥力系数
      const damping = 0.85; // 调整阻尼系数
      
      // 初始化速度
        const velocities = new Array(contextNodes.length).fill().map(() => new THREE.Vector3());
        
        // 计算节点之间的力
        for (let iter = 0; iter < iterations; iter++) {
          // 重置力
          const forces = new Array(contextNodes.length).fill().map(() => new THREE.Vector3());
          
          // 计算排斥力 - 对所有节点对都应用排斥力
          for (let i = 0; i < contextNodes.length; i++) {
            for (let j = i + 1; j < contextNodes.length; j++) {
              const nodeA = contextNodes[i].mesh.position;
              const nodeB = contextNodes[j].mesh.position;
            const direction = new THREE.Vector3().subVectors(nodeB, nodeA);
            const distance = direction.length();
            
            // 如果距离为0，添加小的随机方向
            if (distance === 0) {
              direction.set(
                (Math.random() - 0.5) * 10,
                (Math.random() - 0.5) * 10,
                (Math.random() - 0.5) * 10
              );
            } else if (distance < 1) {
              // 如果距离非常小，设置最小距离
              direction.normalize().multiplyScalar(1);
            }
            
            const repulsion = direction.normalize().multiplyScalar(
              -repulsionForce / (distance * distance + 10)
            );
            forces[i].add(repulsion);
            forces[j].sub(repulsion);
          }
        }
        
        // 计算吸引力（基于上下文关系）
          contextData.links.forEach(link => {
            const sourceIndex = contextNodes.findIndex(n => n.id === link.source);
            const targetIndex = contextNodes.findIndex(n => n.id === link.target);
            
            if (sourceIndex !== -1 && targetIndex !== -1) {
              const nodeA = contextNodes[sourceIndex].mesh.position;
              const nodeB = contextNodes[targetIndex].mesh.position;
            const direction = new THREE.Vector3().subVectors(nodeB, nodeA);
            const distance = direction.length();
            const targetDistance = 120; // 目标连接距离
            
            const spring = direction.normalize().multiplyScalar(
              springForce * (distance - targetDistance)
            );
            forces[sourceIndex].add(spring);
            forces[targetIndex].sub(spring);
          }
        });
        
        // 应用力和更新位置
          for (let i = 0; i < contextNodes.length; i++) {
            // 应用力
            velocities[i].add(forces[i]);
            // 应用阻尼
            velocities[i].multiplyScalar(damping);
            // 更新位置
            contextNodes[i].mesh.position.add(velocities[i]);
            
            // 限制在球形空间内
            const maxRadius = 450;
            const distance = contextNodes[i].mesh.position.length();
            if (distance > maxRadius) {
              contextNodes[i].mesh.position.normalize().multiplyScalar(maxRadius);
            }
          }
      }
    };
    
    // 应用上下文布局
    applyContextLayout();
    
    // 将节点添加到场景
    contextNodeObjects.forEach(mesh => {
      scene.add(mesh);
    });
    
    // 创建上下文关系连线
    contextData.links.forEach(link => {
      const source = contextNodes.find(n => n.id === link.source);
      const target = contextNodes.find(n => n.id === link.target);
      
      if (source && target) {
        const geometry = new THREE.BufferGeometry().setFromPoints([
          source.mesh.position.clone(),
          target.mesh.position.clone()
        ]);
        
        const material = new THREE.LineBasicMaterial({
          color: 0x6366f1,
          transparent: true,
          opacity: 0.3,
          linewidth: link.value * 2
        });
        
        const line = new THREE.Line(geometry, material);
        // 添加userData以存储连线信息
        line.userData = { contextLink: { ...link } };
        scene.add(line);
        contextLinkObjects.push(line);
        contextLinks.push({ ...link, line });
      }
    });

    // 添加光源
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    
    // 添加定向光
    const directionalLight1 = new THREE.DirectionalLight(0x6366f1, 0.8);
    directionalLight1.position.set(1, 1, 1);
    scene.add(directionalLight1);
    
    const directionalLight2 = new THREE.DirectionalLight(0x8b5cf6, 0.8);
    directionalLight2.position.set(-1, -1, -1);
    scene.add(directionalLight2);
    
    // 添加点光源增强质感
    const pointLight1 = new THREE.PointLight(0x6366f1, 0.5, 500);
    pointLight1.position.set(100, 100, 100);
    scene.add(pointLight1);
    
    const pointLight2 = new THREE.PointLight(0x8b5cf6, 0.5, 500);
    pointLight2.position.set(-100, -100, -100);
    scene.add(pointLight2);

    // 控制器
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.rotateSpeed = 0.3;
    controls.zoomSpeed = 0.7;
    controls.enablePan = true;
    controls.panSpeed = 0.5;
    controls.autoRotate = false; // 禁用自动旋转，由用户控制
    controls.autoRotateSpeed = 0.3;

    // 窗口大小调整
    const handleResize = () => {
      const container = getContainer();
      if (!container || !camera || !renderer) return;
      
      const width = container.clientWidth;
      const height = container.clientHeight;
      
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
    };

    // 监听窗口大小变化
    window.addEventListener('resize', handleResize);
    
    // 添加ResizeObserver监听容器大小变化
    let resizeObserver = null;
    if ('ResizeObserver' in window && container && container instanceof Element) {
      resizeObserver = new ResizeObserver(entries => {
        for (let _entry of entries) {
          handleResize();
        }
      });
      resizeObserver.observe(container);
    } else if (container && !(container instanceof Element)) {
      logger.warn('ResizeObserver: container is not an Element', container);
    }

    // 节点点击检测
    const raycaster = new THREE.Raycaster();
    const mouse = new THREE.Vector2();

    const onMouseMove = (event) => {
        // 使用容器的尺寸而不是窗口尺寸来计算鼠标坐标
        const container = getContainer();
        if (container && container instanceof Element) {
          const rect = container.getBoundingClientRect();
          mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
          mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
        }
      };

    const onMouseClick = (event) => {
        // 使用点击事件的坐标重新计算，确保准确性
        const container = getContainer();
        if (container && container instanceof Element) {
          const rect = container.getBoundingClientRect();
          mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
          mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
          
          raycaster.setFromCamera(mouse, camera);
          const intersects = raycaster.intersectObjects(contextNodeObjects);
          
          if (intersects.length > 0) {
            const clickedObject = intersects[0].object;
            const nodeId = contextNodes.findIndex(n => n.mesh === clickedObject);
            
            if (nodeId !== -1) {
              showNodeDetails(contextNodes[nodeId]);
            }
          }
        }
      };

    window.addEventListener('mousemove', onMouseMove);
    window.addEventListener('click', onMouseClick);

    // 动画循环
    const animateContext = () => {
      animationFrameId.value = requestAnimationFrame(animateContext);
      
      // 更新上下文连线位置
      contextLinks.forEach((link, index) => {
        const source = contextNodes.find(n => n.id === link.source);
        const target = contextNodes.find(n => n.id === link.target);
        
        if (source && target) {
          contextLinkObjects[index].geometry.setFromPoints([
            source.mesh.position.clone(),
            target.mesh.position.clone()
          ]);
        }
      });
      
      // 星空缓慢移动
    if (starsRef.value && settings.showBackground) {
      // 背景旋转
      starsRef.value.rotation.y += starsConfig.rotationSpeed * 10; // 增加速度以更容易观察效果
    }
    
    // 如果用户正在交互，则不自动旋转视图
    if (!controls.isRotating && !controls.isZooming && !controls.isPanning) {
      // 使整个视图缓慢旋转，这样节点就会跟着一起旋转
      scene.rotation.y += starsConfig.rotationSpeed * 10; // 增加速度
    }
      
      controls.update();
      renderer.render(scene, camera);
    };

    animateContext();

    // 返回清理函数
    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('mousemove', onMouseMove);
      window.removeEventListener('click', onMouseClick);
      
      // 断开ResizeObserver连接
      if (resizeObserver) {
        resizeObserver.disconnect();
        resizeObserver = null;
      }
      cancelAnimationFrame(animationFrameId.value);
      
      // 清理Three.js资源
      contextNodeObjects.forEach(obj => scene.remove(obj));
      contextLinkObjects.forEach(obj => scene.remove(obj));
      scene.remove(stars, ambientLight, directionalLight1, directionalLight2, pointLight1, pointLight2);
      
      // 正确获取contextContainer元素并移除renderer
      const parentElement = renderer.domElement.parentNode;
      const contextContainer = document.getElementById('context-visualization');
      if (parentElement && parentElement === contextContainer) {
        contextContainer.removeChild(renderer.domElement);
      }
      
      renderer.dispose();
    };
};

// 创建上下文可视化背景星空
const createContextStars = (scene, config) => {
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

// 提供createContextStars函数给父组件使用
provide('createContextStars', createContextStars);

// 组件挂载时初始化
let cleanup = null;
onMounted(() => {
  cleanup = initContextScene();
});

// 组件卸载时清理
onUnmounted(() => {
  if (cleanup) cleanup();
});
</script>

<style scoped>
#context-visualization {
  border-radius: 12px;
  overflow: hidden;
}

.bg-gradient-universe {
  background: radial-gradient(circle at center, #0f172a 0%, #020617 100%);
}

/* 为Three.js渲染的canvas添加圆角 */
#context-visualization canvas {
  border-radius: 12px;
  display: block;
}
</style>