# 容器宽度一致化解决方案

## 问题分析

根据对代码的分析，当前聊天消息布局存在以下问题：

1. **UserChatBubble** 组件：
   - 默认样式：外层容器 `div` 样式为 `flex justify-end max-w-[85%]`
   - 内部消息气泡：`w-fit max-w-full`

2. **AIChatBubble** 组件：
   - 默认样式：外层容器 `div` 样式为 `flex items-start max-w-[85%]`
   - 内部消息气泡：`w-fit max-w-full`

3. **ChatMessage** 组件：
   - 将两个气泡分别渲染在独立的 `div` 中
   - 用户消息右对齐，AI消息左对齐

由于两个气泡容器是独立的，它们的宽度基于各自内容计算，导致无法始终保持一致。

## 解决方案

要让两个容器始终保持宽度一致，需要调整父容器布局并合并容器。以下是具体实现方案：

### 1. 修改 `ChatMessage.vue` 组件

**调整默认样式布局**：
```html
<!-- 默认样式 -->
<div v-if="!chatStyleDocument" class="flex mb-4">
  <!-- 共享容器，确保宽度一致 -->
  <div class="flex-1 max-w-[85%]">
    <!-- AI消息气泡 - 左对齐 -->
    <div v-if="!isUserMessage" class="w-full">
      <AIChatBubble 
        :message="message" 
        :chatStyleDocument="chatStyleDocument"
      />
    </div>
    
    <!-- 用户消息气泡 - 右对齐 -->
    <div v-else class="w-full flex justify-end">
      <UserChatBubble 
        :message="message" 
        :chatStyleDocument="chatStyleDocument"
        @editMessage="handleEditMessage"
      />
    </div>
  </div>
</div>
```

### 2. 修改 `UserChatBubble.vue` 组件

**移除外层 max-w 限制**：
```html
<!-- 默认气泡样式 -->
<div v-else class="flex justify-end">
  <!-- 移除 max-w-[85%]，由父容器控制宽度 -->
  <div class="relative group flex flex-col items-end">
    <!-- 消息内容气泡 -->
    <div 
      v-if="messageContent || messageValue.error || messageValue.isTyping"
      :class="[
        'bg-primary/20 text-gray-800 rounded-2xl rounded-tr-none px-5 py-3 shadow-lg overflow-hidden',
        'w-fit',
        'max-w-full' <!-- 保留 max-w-full 以防止内容溢出 -->
      ]"
    >
      <!-- 消息内容 -->
    </div>
    <!-- 操作按钮 -->
  </div>
</div>
```

### 3. 修改 `AIChatBubble.vue` 组件

**移除外层 max-w 限制**：
```html
<!-- 默认气泡样式 -->
<div v-else class="flex items-start">
  <!-- 移除 max-w-[85%]，由父容器控制宽度 -->
  <!-- 头像 -->
  <div class="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center mr-2 mt-1 flex-shrink-0">
    <!-- 头像图标 -->
  </div>
  <div class="relative group">
    <!-- 消息内容气泡 -->
    <div :class="[
      'bg-white dark:bg-dark-bg-tertiary rounded-2xl rounded-tl-none px-5 py-3 shadow-lg dark:border dark:border-dark-border overflow-hidden',
      'w-fit',
      'max-w-full' <!-- 保留 max-w-full 以防止内容溢出 -->
    ]">
      <!-- 消息内容 -->
    </div>
    <!-- 时间戳和操作按钮 -->
  </div>
</div>
```

## 实现原理

1. **共享父容器**：将用户消息和AI消息放入同一个父容器中，该容器设置统一的 `max-w-[85%]` 限制

2. **宽度继承**：子容器（气泡）不再设置自己的最大宽度，而是继承父容器的宽度限制

3. **对齐方式**：
   - AI消息：父容器内左对齐（默认）
   - 用户消息：父容器内右对齐（使用 `flex justify-end`）

4. **内容自适应**：气泡本身仍使用 `w-fit`，但受限于父容器的 `max-w-[85%]`，确保两者宽度一致

## 预期效果

- 所有消息气泡将共享相同的最大宽度限制
- 用户消息和AI消息的容器宽度始终保持一致
- 消息气泡宽度仍会根据内容自适应，但不超过统一的最大宽度
- 保持了原有的对齐方式（用户消息右对齐，AI消息左对齐）

## 注意事项

1. 此修改仅影响默认样式，不影响文档模式样式
2. 需确保所有相关组件的样式修改正确应用
3. 测试不同屏幕尺寸下的显示效果，确保响应式布局正常工作

通过以上调整，两个容器将始终保持宽度一致，同时保持原有的视觉效果和交互体验。