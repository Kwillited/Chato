// 组件库入口文件
// 统一导出所有组件，方便外部引入

export { default as AIChatBubble } from './chat/AIChatBubble.vue'
export { default as UserChatBubble } from './chat/UserChatBubble.vue'
export { default as UserInputBox } from './UserInputBox/UserInputBox.vue'
// AIChatDocumentBubble 已合并到 AIChatBubble 组件中，通过 chatStyleDocument 属性控制
export { default as ChatJumpIndicator } from './ChatJumpIndicator/ChatJumpIndicator.vue'
export { default as Tooltip } from '../common/Tooltip.vue'
export { default as ContextVisualizationContent } from './ContextVisualization/ContextVisualizationContent.vue'
export { default as KnowledgeGraphVisualization } from './KnowledgeGraphVisualization/KnowledgeGraphCanvas.vue'
export { default as ToolExecutionStatus } from './ToolExecutionStatus/ToolExecutionStatus.vue'
export { default as ToolCallPlan } from './ToolCallPlan/ToolCallPlan.vue'

export { default as Button } from '../common/Button.vue'
export { default as Loading } from '../common/Loading.vue'
export { default as ConfirmationModal } from '../common/ConfirmationModal.vue'
export { default as DragDropZone } from '../common/DragDropZone.vue'
export { default as SearchBar } from '../common/SearchBar.vue'
export { default as SettingItem } from '../common/SettingItem.vue'

// 导入并导出 VueChatoRenderer 组件
import { VueChatoRenderer } from '../../plugins/vue-chato-renderer/index.js'
export { VueChatoRenderer }