<template>
  <div class="setting-item p-3 rounded-lg">
    <!-- 标题和描述 -->
    <div class="mb-2" v-if="title || description">
      <div v-if="title" class="font-medium text-sm">{{ title }}</div>
      <div v-if="description" class="text-xs text-neutral mt-0.5">{{ description }}</div>
    </div>
    
    <!-- 内容区域 -->
    <div class="setting-content" :class="contentClass">
      <!-- 开关类型 -->
      <div v-if="type === 'toggle'" class="flex justify-between items-center">
        <!-- 如果没有标题，显示自定义内容 -->
        <slot v-if="!title"></slot>
        <!-- 开关 -->
        <label class="toggle-switch">
          <input 
            type="checkbox" 
            :checked="modelValue" 
            @change="handleToggleChange" 
            v-bind="$attrs"
          />
          <span class="toggle-slider"></span>
        </label>
      </div>
      
      <!-- 下拉选择类型 -->
      <div v-else-if="type === 'select'" class="relative">
        <select 
          class="input-field w-full text-sm px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-primary"
          v-model="localValue"
          @change="handleSelectChange"
          v-bind="$attrs"
        >
          <option v-for="option in options" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>
      </div>
      
      <!-- 按钮组类型 -->
      <div v-else-if="type === 'button-group'" class="flex gap-3">
        <button
          v-for="option in options"
          :key="option.value"
          class="chat-style-btn flex-1 py-2 px-3 text-sm border rounded-lg transition-all duration-300 hover:bg-gray-50"
          :class="modelValue === option.value ? 'border-primary bg-primary/10 text-primary active' : 'border-gray-200 bg-white text-gray-700'"
          @click="() => handleButtonGroupChange(option.value)"
          v-bind="$attrs"
        >
          <i v-if="option.icon" :class="['fa-regular', option.icon, 'mr-2']"></i>
          {{ option.label }}
        </button>
      </div>
      
      <!-- 输入框类型 -->
      <div v-else-if="type === 'input'">
        <input
          type="text"
          class="input-field w-full text-sm px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-primary"
          v-model="localValue"
          @input="handleInputChange"
          v-bind="$attrs"
        />
      </div>
      
      <!-- 自定义内容 -->
      <slot v-else></slot>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

// 定义组件属性
const props = defineProps({
  // 设置项类型：toggle, select, button-group, input, custom
  type: {
    type: String,
    default: 'custom',
    validator: (value) => ['toggle', 'select', 'button-group', 'input', 'custom'].includes(value)
  },
  // 设置项标题
  title: {
    type: String,
    default: ''
  },
  // 设置项描述
  description: {
    type: String,
    default: ''
  },
  // 模型值，用于双向绑定
  modelValue: {
    type: [String, Number, Boolean, Array, Object],
    default: null
  },
  // 选项列表，用于select和button-group类型
  options: {
    type: Array,
    default: () => []
  },
  // 内容区域额外的CSS类
  contentClass: {
    type: String,
    default: ''
  }
});

// 定义组件事件
const emit = defineEmits(['update:modelValue', 'change']);

// 本地值，用于处理双向绑定
const localValue = ref(props.modelValue);

// 监听props.modelValue变化，更新本地值
watch(() => props.modelValue, (newValue) => {
  localValue.value = newValue;
});

// 处理开关变化
const handleToggleChange = (event) => {
  const value = event.target.checked;
  emit('update:modelValue', value);
  emit('change', value);
};

// 处理选择变化
const handleSelectChange = () => {
  emit('update:modelValue', localValue.value);
  emit('change', localValue.value);
};

// 处理按钮组变化
const handleButtonGroupChange = (value) => {
  emit('update:modelValue', value);
  emit('change', value);
};

// 处理输入框变化
const handleInputChange = () => {
  emit('update:modelValue', localValue.value);
  emit('change', localValue.value);
};

// 定义组件名称
defineOptions({
  name: 'SettingItem'
});
</script>

<style scoped>
/* 设置项基础样式已在全局样式中定义 */
.setting-content {
  width: 100%;
}
</style>