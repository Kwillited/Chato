<template>
  <div v-if="showSettingsPanel" id="graphSettingsPanel" class="absolute top-10 left-4 h-[calc(100%-60px)] w-[16rem] bg-dark/80 backdrop-blur-md z-40 border border-blue-400/30 flex flex-col transform transition-transform duration-300 rounded-[12px]">
    <div class="p-3 flex justify-between items-center border-b border-blue-400/30">
      <h2 class="text-lg font-bold text-blue-300">背景设置</h2>
      <button
        class="w-8 h-8 p-1.5 flex items-center justify-center text-blue-300 hover:text-blue-200 hover:bg-blue-400/20 rounded-full transition-colors"
        title="关闭设置面板"
        @click="emit('toggleSettingsPanel')"
      >
        <i class="fa-solid fa-xmark"></i>
      </button>
    </div>

    <div class="overflow-y-auto flex-1 p-4 space-y-6">
      <!-- 粒子数量设置 -->
      <div class="mb-6 border-b border-gray-700/50 pb-4">
        <div class="flex justify-between items-center mb-1">
          <label class="text-sm font-medium text-blue-200">粒子数量</label>
          <span
            class="text-sm font-medium text-blue-300 px-2 py-0.5 bg-blue-400/10 rounded-full"
            id="particleCountValue"
            >{{ settings.particleCount }}</span
          >
        </div>
        <input
          type="range"
          min="500"
          max="5000"
          step="100"
          :value="settings.particleCount"
          class="slider w-full"
          id="particleCountSlider"
          @input="(event) => emit('handleParticleCountChange', event)"
        />
        <div class="flex justify-between text-xs text-blue-300 mt-1">
          <span>少</span>
          <span>多</span>
        </div>
      </div>

      <!-- 粒子大小设置 -->
      <div class="mb-6 border-b border-gray-700/50 pb-4">
        <div class="flex justify-between items-center mb-1">
          <label class="text-sm font-medium text-blue-200">粒子大小</label>
          <span
            class="text-sm font-medium text-blue-300 px-2 py-0.5 bg-blue-400/10 rounded-full"
            id="particleSizeValue"
            >{{ settings.particleSize.toFixed(1) }}</span
          >
        </div>
        <input
          type="range"
          min="0.5"
          max="3.0"
          step="0.1"
          :value="settings.particleSize"
          class="slider w-full"
          id="particleSizeSlider"
          @input="(event) => emit('handleParticleSizeChange', event)"
        />
        <div class="flex justify-between text-xs text-blue-300 mt-1">
          <span>小</span>
          <span>大</span>
        </div>
      </div>

      <!-- 粒子透明度设置 -->
      <div class="mb-6 border-b border-gray-700/50 pb-4">
        <div class="flex justify-between items-center mb-1">
          <label class="text-sm font-medium text-blue-200">粒子透明度</label>
          <span
            class="text-sm font-medium text-blue-300 px-2 py-0.5 bg-blue-400/10 rounded-full"
            id="particleOpacityValue"
            >{{ settings.particleOpacity.toFixed(1) }}</span
          >
        </div>
        <input
          type="range"
          min="0.1"
          max="1.0"
          step="0.1"
          :value="settings.particleOpacity"
          class="slider w-full"
          id="particleOpacitySlider"
          @input="(event) => emit('handleParticleOpacityChange', event)"
        />
        <div class="flex justify-between text-xs text-blue-300 mt-1">
          <span>透明</span>
          <span>不透明</span>
        </div>
      </div>

      <!-- 背景旋转速度设置 -->
      <div class="mb-6 border-b border-gray-700/50 pb-4">
        <div class="flex justify-between items-center mb-1">
          <label class="text-sm font-medium text-blue-200">旋转速度</label>
          <span
            class="text-sm font-medium text-blue-300 px-2 py-0.5 bg-blue-400/10 rounded-full"
            id="rotationSpeedValue"
            >{{ (settings.rotationSpeed * 10000).toFixed(1) }}</span
          >
        </div>
        <input
          type="range"
          min="0"
          max="0.001"
          step="0.00005"
          :value="settings.rotationSpeed"
          class="slider w-full"
          id="rotationSpeedSlider"
          @input="(event) => emit('handleRotationSpeedChange', event)"
        />
        <div class="flex justify-between text-xs text-blue-300 mt-1">
          <span>停止</span>
          <span>快速</span>
        </div>
      </div>



      <!-- 重置设置按钮 -->
      <button
        class="w-full py-2.5 mt-4 text-sm text-blue-200 bg-gray-800 hover:bg-gray-700 rounded-lg transition-colors"
        @click="emit('resetSettings')"
      >
        <i class="fa-solid fa-rotate-right mr-2"></i>重置设置
      </button>
    </div>
  </div>
</template>

<script setup>
// 定义props，接收父组件传递的数据
const _props = defineProps({
  // 控制设置面板显示/隐藏的状态
  showSettingsPanel: {
    type: Boolean,
    required: true
  },
  // 包含各种设置的对象
  settings: {
    type: Object,
    required: true
  },
  // 当前激活的提示框ID
  activeTooltip: {
    type: String,
    required: true
  },
  // 提示框样式
  tooltipStyle: {
    type: Object,
    required: true
  }
});

// 定义emits，向父组件发送事件
const emit = defineEmits([
  'toggleSettingsPanel',
  'handleParticleCountChange',
  'handleParticleSizeChange',
  'handleParticleOpacityChange',
  'handleRotationSpeedChange',
  'resetSettings'
]);
</script>

<style scoped>
/* 自定义设置面板内部滚动条样式 - 隐藏滚动条但保持滚动功能 */
#graphSettingsPanel .overflow-y-auto {
  /* Firefox */
  scrollbar-width: none;
  -ms-overflow-style: none;
}

/* Chrome, Edge, and Safari */
#graphSettingsPanel .overflow-y-auto::-webkit-scrollbar {
  display: none;
}
</style>