import { h } from 'vue'
import { processInlineTokens } from '../utils/tokenProcessor.js'

export const inlineRules = {
  strong: (token, key) => {
    if (token.raw && token.raw.startsWith('__') && token.raw.endsWith('__')) {
      return h('u', { key }, processInlineTokens(token.tokens, key))
    } else {
      return h('strong', { key }, processInlineTokens(token.tokens, key))
    }
  },
  em: (token, key) => h('em', { key }, processInlineTokens(token.tokens, key)),
  u: (token, key) => h('u', { key }, processInlineTokens(token.tokens, key)),
  link: (token, key) => h('a', {
    key,
    href: token.href,
    target: '_blank',
    rel: 'noopener noreferrer'
  }, processInlineTokens(token.tokens, key)),
  code: (token, key) => h('code', { key, class: 'inline-code' }, token.text),
  codespan: (token, key) => h('code', { key, class: 'inline-code' }, token.text),
  image: (token, key) => h('span', { key, class: 'image-wrapper' }, [
    h('span', { class: 'image-loading' }, [
      h('i', { class: 'fa-solid fa-spinner fa-spin' }),
      h('span', '加载中...')
    ]),
    h('img', {
      src: token.href,
      alt: token.text || '',
      title: token.title,
      class: 'markdown-image',
      onLoad: (event) => {
        event.target.previousElementSibling.style.display = 'none';
        event.target.style.display = 'block';
      },
      onError: (event) => {
        event.target.previousElementSibling.style.display = 'none';
        event.target.style.display = 'none';
        event.target.nextElementSibling.style.display = 'flex';
      }
    }),
    h('span', { class: 'image-error' }, [
      h('i', { class: 'fa-solid fa-image' }),
      h('span', '图片加载失败')
    ])
  ]),
  del: (token, key) => h('del', { key }, processInlineTokens(token.tokens, key)),
  text: (token) => token.text
}
