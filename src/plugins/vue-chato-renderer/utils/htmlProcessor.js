import { h } from 'vue'

export const parseHtmlString = (htmlString) => {
  const parser = new DOMParser()
  const doc = parser.parseFromString(htmlString, 'text/html')
  const parserError = doc.querySelector('parsererror')
  if (parserError) {
    console.error('HTML 解析错误:', parserError.textContent)
    return null
  }
  return doc.body
}

export const convertElementToVNode = (element, key) => {
  if (element.nodeType === Node.TEXT_NODE) {
    return element.textContent
  } else if (element.nodeType === Node.ELEMENT_NODE) {
    const props = { key }
    
    for (let i = 0; i < element.attributes.length; i++) {
      const attr = element.attributes[i]
      props[attr.name] = attr.value
    }
    
    if (element.style) {
      props.style = {}
      for (let i = 0; i < element.style.length; i++) {
        const property = element.style[i]
        props.style[property] = element.style[property]
      }
    }
    
    const children = Array.from(element.childNodes).map((child, index) => 
      convertElementToVNode(child, `${key}-child-${index}`)
    ).filter(child => child !== null && child !== '')
    
    return h(element.tagName.toLowerCase(), props, children)
  }
  return null
}
