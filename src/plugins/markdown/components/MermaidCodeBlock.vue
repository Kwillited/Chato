<template>
  <div class="code-container">
    <div class="code-header">
      <span class="code-language">mermaid</span>
      <div class="code-header-actions">
        <div class="mermaid-toggle-slider"
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
    <div class="mermaid-container" :id="mermaidContainerId" v-show="isMermaidVisible">
      <!-- 使用渲染函数渲染 VNode -->
      <component :is="svgVNode" />
    </div>
    <pre class="mermaid-code" :id="codeBlockId" v-show="!isMermaidVisible"><code class="language-plaintext">{{ code }}</code></pre>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, computed, h } from 'vue'

const props = defineProps({
  code: {
    type: String,
    default: ''
  }
})

const isMermaidVisible = ref(true)
const mermaidId = `mermaid-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
const codeBlockId = `code-block-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
const mermaidContainerId = `mermaid-container-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

// 渲染状态
const isRendering = ref(false)
const renderTimer = ref(null)

// 临时缓冲区，用于按行积累代码
const tempCodeBuffer = ref('')
const lastCodeLength = ref(0)

// 基础容器 VNode 引用
const containerVNode = ref(null)

// SVG 内容
const svgContent = ref('')

const toggleView = () => {
  isMermaidVisible.value = !isMermaidVisible.value
}

const copyCode = () => {
  navigator.clipboard.writeText(props.code)
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

// 计算容器高度
const containerHeight = computed(() => {
  const lines = codeLines.value
  // 根据代码行数计算高度，每行 30px，最少 300px，最多 800px
  return Math.min(Math.max(300, lines.length * 30), 800)
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

// 解析 SVG 字符串为 DOM 元素
const parseSvgString = (svgString) => {
  const parser = new DOMParser()
  const doc = parser.parseFromString(svgString, 'image/svg+xml')
  // 检查是否解析成功
  const parserError = doc.querySelector('parsererror')
  if (parserError) {
    console.error('SVG 解析错误:', parserError.textContent)
    return null
  }
  return doc.documentElement
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
    const camelCaseTags = ['foreignobject', 'textpath', 'textpath', 'lineargradient', 'radialgradient', 'clippath', 'fegaussianblur']
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
  console.log('开始更新 SVG 内容')
  svgContent.value = svg
  console.log('SVG 内容长度:', svg.length)
  
  try {
    // 解析 SVG 字符串为 DOM 元素
    console.log('开始解析 SVG 字符串')
    const svgElement = parseSvgString(svg)
    console.log('SVG 元素解析结果:', svgElement)
    
    if (svgElement) {
      // 转换为 VNode
      console.log('开始转换为 VNode')
      const svgVNode = convertElementToVNode(svgElement)
      console.log('VNode 转换结果:', svgVNode)
      // 创建容器 VNode
      console.log('创建容器 VNode')
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
      console.log('容器 VNode 创建完成')
    } else {
      // SVG 解析失败，创建空容器
      console.log('SVG 解析失败，创建错误容器')
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



// 生成稳定的 ID，基于代码内容的哈希值
const generateStableId = (code) => {
  let hash = 0
  for (let i = 0; i < code.length; i++) {
    const char = code.charCodeAt(i)
    hash = ((hash << 5) - hash) + char
    hash = hash & hash // 转换为 32 位整数
  }
  return `mermaid-${Math.abs(hash)}`
}

// 渲染 Mermaid 图表
const renderMermaid = () => {
  console.log('开始渲染 Mermaid 图表')
  if (typeof mermaid === 'undefined') {
    console.error('Mermaid 库未加载')
    return
  }
  
  const container = document.getElementById(mermaidContainerId)
  if (!container) {
    console.error('容器元素未找到:', mermaidContainerId)
    return
  }
  
  // 设置容器固定高度
  container.style.height = `${containerHeight.value}px`
  console.log('容器高度设置为:', containerHeight.value)
  
  // 清除之前的渲染定时器
  if (renderTimer.value) {
    clearTimeout(renderTimer.value)
  }
  
  // 如果正在渲染，等待当前渲染完成
  if (isRendering.value) {
    console.log('正在渲染中，等待完成')
    renderTimer.value = setTimeout(renderMermaid, 50)
    return
  }
  
  isRendering.value = true
  
  // 使用临时缓冲区中的代码
  const code = cleanedCode.value
  console.log('Mermaid 代码:', code)
  if (!code) {
    console.log('代码为空，创建空容器')
    updateSvgContent('')
    isRendering.value = false
    return
  }
  
  try {
    // 尝试解析代码语法
    console.log('开始解析代码语法')
    mermaid.parse(code)
      .then(() => {
        // 语法正确，Promise 被 resolve
        console.log('语法解析成功')
        // 进行渲染
        const stableId = generateStableId(code)
        console.log('生成的稳定 ID:', stableId)
        console.log('开始渲染 Mermaid 图表')
        mermaid.render(stableId, code)
          .then(result => {
            console.log('渲染成功，SVG 长度:', result.svg.length)
            // 更新 SVG 内容
            updateSvgContent(result.svg)
            isRendering.value = false
          })
          .catch(error => {
            console.error('Mermaid 渲染错误:', error)
            isRendering.value = false
          })
      })
      .catch(error => {
        // 语法错误，Promise 被 reject
        console.error('Mermaid 语法错误:', error)
        isRendering.value = false
      })
  } catch (error) {
    console.error('Mermaid 解析错误:', error)
    isRendering.value = false
  }
}

onMounted(() => {
  // 延迟渲染，确保 DOM 已更新
  setTimeout(renderMermaid, 100)
})

// 当代码变化时重新渲染
watch(() => props.code, (newCode) => {
  console.log('代码变化:', newCode)
  
  // 检查是否有新的换行符
  const newLines = (newCode.match(/\n/g) || []).length
  const oldLines = (tempCodeBuffer.value.match(/\n/g) || []).length
  
  // 更新临时缓冲区
  tempCodeBuffer.value = newCode
  
  // 只有当代码长度增加且包含新的换行符时，才进行渲染
  if (newCode.length > lastCodeLength.value && newLines > oldLines) {
    console.log('检测到新行，开始渲染')
    // 立即渲染，移除防抖
    renderMermaid()
  }
  
  // 更新最后代码长度
  lastCodeLength.value = newCode.length
})

// 当代码行数变化时更新容器高度
watch(codeLines, () => {
  const container = document.getElementById(mermaidContainerId)
  if (container) {
    container.style.height = `${containerHeight.value}px`
  }
})

// 组件卸载时清理资源
onUnmounted(() => {
  // 清理引用
  containerVNode.value = null
  svgContent.value = ''
})
</script>

<style scoped>
.code-container {
  margin: 1em 0;
  border-radius: 5px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.code-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #f5f5f5;
  padding: 0.5em 1em;
  border-bottom: 1px solid #e0e0e0;
}

.code-language {
  font-size: 0.85em;
  font-weight: 600;
  color: #666;
}

.code-header-actions {
  display: flex;
  gap: 0.5em;
}

.mermaid-toggle-slider {
  cursor: pointer;
  display: flex;
  align-items: center;
  padding: 0.25em;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.mermaid-toggle-slider:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.mermaid-toggle-slider.active {
  background-color: rgba(0, 123, 255, 0.1);
}

.slider-track {
  display: flex;
  align-items: center;
}

.slider-thumb {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
}

.copy-code-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25em;
  border-radius: 4px;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.copy-code-btn:hover {
  background-color: rgba(0, 0, 0, 0.05);
}

.mermaid-container {
  background-color: #fff;
  padding: 1em;
  border-bottom: 1px solid #e0e0e0;
  /* 设置固定高度，避免高度变化导致的闪烁 */
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

/* 确保 SVG 适应容器大小 */
.mermaid-container svg {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  flex-shrink: 0;
}

.mermaid-code {
  background-color: #f5f5f5;
  margin: 0;
  padding: 1em;
  overflow-x: auto;
}

.mermaid-code code {
  background-color: transparent;
  padding: 0;
  font-family: 'Courier New', Courier, monospace;
}
</style>