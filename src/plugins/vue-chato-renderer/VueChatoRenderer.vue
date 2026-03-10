<script>
import { ref, computed, watch, onMounted, h, defineComponent } from 'vue'
import { createMarkdownRenderer } from './core/markdown-renderer.js'
import { createAstParser } from './core/ast-parser.js'
import { createVNodeTransformer } from './core/vnode-transformer.js'
import { createCodeHighlighter } from './extensions/code-highlighter.js'

export default defineComponent({
  name: 'VueChatoRenderer',
  props: {
    content: {
      type: String,
      default: ''
    },
    config: {
      type: Object,
      default: () => ({
        breaks: true,
        gfm: true,
        highlight: true,
        copy: true
      })
    }
  },
  setup(props) {
    // 创建渲染实例
    const markdownRenderer = createMarkdownRenderer(props.config)
    const astParser = createAstParser()
    const vnodeTransformer = createVNodeTransformer()
    const codeHighlighter = createCodeHighlighter()

    // 缓存上次的内容和解析结果
    const lastContent = ref('')
    const cachedVNodes = ref([])

    // 解析 Markdown 为 VNode 树
    const parseMarkdownToVNodes = (content) => {
      if (!content) return []
      
      try {
        // 解析为 AST，默认使用增量解析
        const ast = astParser.parse(content)
        // 转换为 VNode
        return vnodeTransformer.transform(ast)
      } catch (error) {
        console.warn('Vue-Chato-Renderer 解析失败:', error)
        // 解析失败时返回原始内容作为文本
        return [content]
      }
    }

    // 计算 VNode 树
    const vnodeTree = computed(() => {
      // 检查内容是否有变化
      if (props.content === lastContent.value && cachedVNodes.value.length > 0) {
        return h('div', { class: 'markdown-content' }, cachedVNodes.value)
      }
      
      // 内容变化或首次渲染，重新解析
      const vnodes = parseMarkdownToVNodes(props.content)
      cachedVNodes.value = vnodes
      lastContent.value = props.content
      
      return h('div', { class: 'markdown-content' }, vnodes)
    })

    // 组件挂载时处理
    onMounted(() => {
      // 初始渲染后处理
      setTimeout(() => {
        // 处理代码高亮
        if (props.config.highlight) {
          codeHighlighter.highlightAll()
        }
      }, 0)
    })

    // 监听内容变化，处理代码高亮
    watch(() => props.content, () => {
      setTimeout(() => {
        // 处理代码高亮
        if (props.config.highlight) {
          codeHighlighter.highlightAll()
        }
      }, 0)
    })

    return {
      vnodeTree
    }
  },
  render() {
    return this.vnodeTree || h('div', { class: 'markdown-content' })
  }
})
</script>

<style scoped>
.markdown-content {
  /* 基础样式 */
  line-height: var(--line-height-base);
  font-family: var(--font-family-base);
  padding: 0;
}
</style>

<style>
/* 导入全局 Vue-Chato-Renderer 样式 */
@import './styles/variables.css';
@import './styles/markdown-styles.css';
</style>
