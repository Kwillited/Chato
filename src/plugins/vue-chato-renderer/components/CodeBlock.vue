<template>
  <div class="code-container">
    <div class="code-header">
      <span class="code-language">{{ language }}</span>
      <div class="code-header-actions">
        <!-- Mermaid 视图切换按钮 -->
        <div v-if="isMermaid" class="mermaid-toggle-slider"
          :data-mermaid-id="mermaidId"
          :data-code-id="codeBlockId"
          title="切换视图"
          @click="toggleView"
          :class="{ active: !isMermaidVisible }"
        >
          <div class="slider-track">
            <div class="slider-thumb">
              <i :class="isMermaidVisible ? 'fa-solid fa-chart-simple' : 'fa-solid fa-code'"></i>
            </div>
          </div>
        </div>
        <!-- 复制按钮 -->
        <button 
          class="copy-code-btn"
          :data-code-block-id="codeBlockId"
          title="复制代码"
          @click="copyCode"
        >
          <i class="fa-solid fa-copy"></i>
        </button>
      </div>
    </div>
    <!-- Mermaid 图表容器 -->
    <div v-if="isMermaid && isMermaidVisible" class="mermaid-container" :id="mermaidContainerId">
      <component :is="svgVNode" />
    </div>
    <!-- 代码容器 -->
    <pre v-show="!isMermaid || !isMermaidVisible" :class="{ 'mermaid-code': isMermaid }"><code :class="`language-${language}`" :id="codeBlockId">{{ code }}</code></pre>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, onUpdated, watch, computed, h } from 'vue'
import { createMermaidRenderer } from '../extensions/mermaid-renderer.js'
import { createCodeHighlighter } from '../extensions/code-highlighter.js'
import { copyToClipboard } from '../extensions/copy-feature.js'
import { parseSvgString } from '../utils/svg-utils.js'

const props = defineProps({
  code: {
    type: String,
    default: ''
  },
  language: {
    type: String,
    default: 'plaintext'
  },
  isMermaid: {
    type: Boolean,
    default: false
  }
})

const codeBlockId = `code-block-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
const mermaidId = `mermaid-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
const mermaidContainerId = `mermaid-container-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

// Mermaid 相关状态
const isMermaidVisible = ref(true)
const isRendering = ref(false)
const renderTimer = ref(null)
const tempCodeBuffer = ref('')
const lastCodeLength = ref(0)

// 基础容器 VNode 引用
const containerVNode = ref(null)
// SVG 内容
const svgContent = ref('')

// 创建渲染器实例
const mermaidRenderer = createMermaidRenderer()
const codeHighlighter = createCodeHighlighter()

const copyCode = async () => {
  await copyToClipboard(props.code)
}

// 处理代码高亮
const handleHighlight = () => {
  const codeElement = document.getElementById(codeBlockId)
  if (codeElement) {
    codeHighlighter.highlightElement(codeElement)
  }
}

// Mermaid 视图切换
const toggleView = () => {
  isMermaidVisible.value = !isMermaidVisible.value
}

// 清理代码
const cleanedCode = computed(() => {
  let code = props.code.trim()
  if (code.startsWith('```mermaid')) {
    code = code.substring('```mermaid'.length)
  }
  if (code.endsWith('```')) {
    code = code.substring(0, code.length - 3)
  }
  return code.trim()
})

// 代码行数组
const codeLines = computed(() => {
  return cleanedCode.value.split('\n').filter(line => line.trim() !== '')
})

// 初始化基础 VNode
const initContainerVNode = () => {
  if (!containerVNode.value) {
    containerVNode.value = h('div', {
      class: 'svg-container',
      style: {
        width: '100%',
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }
    })
  }
}

// 递归转换 DOM 元素为 VNode
const convertElementToVNode = (element) => {
  if (element.nodeType === Node.TEXT_NODE) {
    return element.textContent
  } else if (element.nodeType === Node.ELEMENT_NODE) {
    const props = {}
    
    // 处理属性
    for (let i = 0; i < element.attributes.length; i++) {
      const attr = element.attributes[i]
      props[attr.name] = attr.value
    }
    
    // 处理样式
    if (element.style) {
      props.style = {}
      for (let i = 0; i < element.style.length; i++) {
        const property = element.style[i]
        props.style[property] = element.style[property]
      }
    }
    
    // 为 SVG 元素添加自适应大小的样式
    if (element.tagName.toLowerCase() === 'svg') {
      props.style = {
        ...props.style,
        width: '100%',
        height: '100%',
        maxWidth: '100%',
        maxHeight: '100%',
        objectFit: 'contain'
      }
    }
    
    // 处理子节点
    const children = Array.from(element.childNodes).map(convertElementToVNode).filter(child => child !== null && child !== '')
    
    // 对于 SVG 元素，保持标签名大小写
    let tagName = element.tagName.toLowerCase()
    // 特殊处理需要驼峰命名的 SVG 元素
    const camelCaseTags = ['foreignobject', 'textpath', 'lineargradient', 'radialgradient', 'clippath', 'fegaussianblur']
    if (camelCaseTags.includes(tagName)) {
      // 转换为驼峰命名
      tagName = tagName.replace(/-(.)/g, (_, char) => char.toUpperCase())
      // 特殊处理 foreignobject
      if (tagName === 'foreignobject') {
        tagName = 'foreignObject'
      }
    }
    
    // 创建 VNode
    return h(tagName, props, children)
  }
  return null
}

// 更新 SVG 内容
const updateSvgContent = (svg) => {
  svgContent.value = svg
  
  try {
    // 解析 SVG 字符串为 DOM 元素
    const svgElement = parseSvgString(svg)
    
    if (svgElement) {
      // 转换为 VNode
      const svgVNode = convertElementToVNode(svgElement)
      // 创建容器 VNode
      containerVNode.value = h('div', {
        class: 'svg-container',
        style: {
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }
      }, [svgVNode])
    } else {
      // SVG 解析失败，创建空容器
      containerVNode.value = h('div', {
        class: 'svg-container',
        style: {
          width: '100%',
          height: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center'
        }
      }, ['SVG 解析失败'])
    }
  } catch (error) {
    console.error('SVG 解析错误:', error)
    // 出错时创建空容器
    containerVNode.value = h('div', {
      class: 'svg-container',
      style: {
        width: '100%',
        height: '100%',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }
    }, ['SVG 渲染失败'])
  }
}

// 计算 VNode
const svgVNode = computed(() => {
  initContainerVNode()
  return containerVNode.value
})

// 渲染 Mermaid 图表
const renderMermaid = async () => {
  if (isRendering.value) {
    renderTimer.value = setTimeout(renderMermaid, 50)
    return
  }
  
  isRendering.value = true
  
  try {
    // 渲染 Mermaid 图表
    const svg = await mermaidRenderer.render(cleanedCode.value)
    updateSvgContent(svg)
  } catch (error) {
    console.error('Mermaid 渲染错误:', error)
  } finally {
    isRendering.value = false
  }
}

onMounted(() => {
  // 延迟处理，确保 DOM 已更新
  setTimeout(() => {
    handleHighlight()
    if (props.isMermaid) {
      renderMermaid()
    }
  }, 100)
})

// 检测代码块是否结束
const isCodeBlockEnded = (code) => {
  // 检测 Markdown 代码块的结束标记
  return code.includes('```')
}

// 组件更新时处理
onUpdated(() => {
  // 只有当代码块结束时才进行高亮
  if (isCodeBlockEnded(props.code)) {
    // 延迟处理，确保 DOM 已更新
    setTimeout(() => {
      handleHighlight()
    }, 100)
  }
})

// 当代码变化时重新处理
watch(() => props.code, (newCode) => {
  // 只有当代码块结束时才进行高亮
  if (isCodeBlockEnded(newCode)) {
    // 重新高亮代码
    setTimeout(handleHighlight, 100)
  }
  
  // 如果是 Mermaid 图表，重新渲染
  if (props.isMermaid) {
    // 检查是否有新的换行符
    const newLines = (newCode.match(/\n/g) || []).length
    const oldLines = (tempCodeBuffer.value.match(/\n/g) || []).length
    
    // 更新临时缓冲区
    tempCodeBuffer.value = newCode
    
    // 只有当代码长度增加且包含新的换行符时，才进行渲染
    if (newCode.length > lastCodeLength.value && newLines > oldLines) {
      // 立即渲染，移除防抖
      renderMermaid()
    }
    
    // 更新最后代码长度
    lastCodeLength.value = newCode.length
  }
})

// 当代码行数变化时更新容器高度
watch(codeLines, () => {
  if (props.isMermaid) {
    const container = document.getElementById(mermaidContainerId)
    if (container) {
      // 根据代码行数计算高度，每行 30px，最少 300px，最多 800px
      const height = Math.min(Math.max(300, codeLines.value.length * 30), 800)
      container.style.height = `${height}px`
    }
  }
})

// 组件卸载时清理资源
onUnmounted(() => {
  // 清理引用
  containerVNode.value = null
  svgContent.value = ''
  if (renderTimer.value) {
    clearTimeout(renderTimer.value)
  }
})
</script>

<style>
/* 导入样式 */
@import '../styles/code-block-styles.css';
</style>
