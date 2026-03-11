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
        copy: true,
        enableAst: true
      })
    }
  },
  setup(props) {
    // 创建渲染实例
    const markdownRenderer = createMarkdownRenderer(props.config)
    const astParser = createAstParser()
    const vnodeTransformer = createVNodeTransformer()
    const codeHighlighter = createCodeHighlighter()

    // 状态管理
    const rawContent = ref(props.content)
    const ast = ref([])
    const isParsing = ref(false)
    const parsingError = ref(null)
    const codeBlocks = ref([])

    // 处理 AST 解析
    const processAstParsing = async (content) => {
      if (!content) {
        ast.value = []
        codeBlocks.value = []
        parsingError.value = null
        return
      }

      if (isParsing.value) return

      isParsing.value = true
      try {
        // 解析为 AST
        const parsedAst = astParser.parse(content)
        ast.value = parsedAst
        parsingError.value = null
        
        // 提取代码块信息
        const newCodeBlocks = parsedAst.filter(node => node.type === 'code').map(node => ({
          lang: node.lang || 'plaintext',
          code: node.text
        }))
        codeBlocks.value = newCodeBlocks
      } catch (error) {
        console.warn('AST 解析失败:', error)
        parsingError.value = error
        ast.value = []
        codeBlocks.value = []
      } finally {
        isParsing.value = false
      }
    }

    // 计算 VNode 树
    const vnodeTree = computed(() => {
      if (!rawContent.value) {
        return h('div', { class: 'markdown-content' }, [])
      }

      try {
        // 如果有 AST 且解析成功，使用 VNode 转换器
        if (ast.value.length > 0 && !parsingError.value) {
          const vnodes = vnodeTransformer.transform(ast.value)
          return h('div', { class: 'markdown-content' }, vnodes)
        } else {
          // 否则渲染原始文本
          return h('div', { class: 'markdown-content raw-content' }, rawContent.value)
        }
      } catch (error) {
        console.warn('VNode 生成失败:', error)
        // 出错时渲染原始文本
        return h('div', { class: 'markdown-content raw-content' }, rawContent.value)
      }
    })



    // 检测代码块是否结束
    const isCodeBlockEnded = (content) => {
      // 检测 Markdown 代码块的结束标记
      const codeBlockRegex = /```[\s\S]*?```/g
      const matches = content.match(codeBlockRegex)
      return matches !== null
    }

    // 实时更新原始内容
    watch(() => props.content, (newContent) => {
      rawContent.value = newContent
      // 根据配置决定是否触发 AST 解析
      if (props.config.enableAst) {
        // 对所有内容进行 AST 解析，不仅仅是包含代码块的内容
        processAstParsing(newContent)
      } else {
        // 禁用 AST 时，清空 AST 数据
        ast.value = []
        parsingError.value = null
      }
    }, { immediate: true })

    // 组件挂载时处理
    onMounted(() => {
      // 初始渲染后处理
      setTimeout(() => {
        // 处理代码高亮
        if (props.config.highlight) {
          codeHighlighter.highlightAll()
        }
      }, 100)
    })

    // 监听代码块变化，处理代码高亮
    watch(codeBlocks, (newCodeBlocks, oldCodeBlocks) => {
      // 只有当代码块结束且代码块内容发生变化时才进行高亮
      if (isCodeBlockEnded(props.content) && newCodeBlocks.length > 0) {
        // 比较新旧代码块是否有变化
        const codeBlocksChanged = !oldCodeBlocks || 
          newCodeBlocks.length !== oldCodeBlocks.length ||
          newCodeBlocks.some((block, index) => {
            const oldBlock = oldCodeBlocks[index]
            return oldBlock && (block.lang !== oldBlock.lang || block.code !== oldBlock.code)
          })
        
        if (codeBlocksChanged) {
          setTimeout(() => {
            // 处理代码高亮
            if (props.config.highlight) {
              codeHighlighter.highlightAll()
            }
          }, 100)
        }
      }
    })

    // 监听 enableAst 配置变化
    watch(() => props.config.enableAst, (enableAst) => {
      if (enableAst) {
        // 启用 AST 时，触发解析
        processAstParsing(props.content)
      } else {
        // 禁用 AST 时，清空 AST 数据
        ast.value = []
        parsingError.value = null
      }
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

.raw-content {
  white-space: pre-wrap;
  word-break: break-word;
}
</style>

<style>
/* 导入全局 Vue-Chato-Renderer 样式 */
@import './styles/variables.css';
@import './styles/markdown-styles.css';
</style>
