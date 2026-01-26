import { ref, computed } from 'vue';

/**
 * 搜索功能Hook
 * @param {Object} options 配置选项
 * @param {Array} options.data 要搜索的数据数组
 * @param {string} options.initialQuery 初始搜索查询
 * @param {Function} options.searchFields 搜索字段配置函数，返回要搜索的字段数组
 * @returns {Object} 搜索功能管理对象
 */
export function useSearch(options = {}) {
  const {
    data,
    initialQuery = '',
    searchFields = (item) => {
      // 默认搜索逻辑：如果item是对象，搜索所有字符串字段；如果是字符串，直接搜索
      if (typeof item === 'string') {
        return [item];
      }
      return Object.values(item).filter(val => typeof val === 'string');
    }
  } = options;

  // 搜索查询
  const searchQuery = ref(initialQuery);

  // 过滤后的数据
  const filteredTools = computed(() => {
    if (!searchQuery.value.trim()) {
      return data.value;
    }
    
    const query = searchQuery.value.toLowerCase().trim();
    return data.value.filter(item => {
      const fieldsToSearch = searchFields(item);
      return fieldsToSearch.some(field => 
        field.toLowerCase().includes(query)
      );
    });
  });

  // 处理搜索输入
  const handleSearch = (query) => {
    searchQuery.value = query;
  };

  // 重置搜索
  const resetSearch = () => {
    searchQuery.value = initialQuery;
  };

  return {
    searchQuery,
    filteredTools,
    handleSearch,
    resetSearch
  };
}