// src/composables/useRouteState.js
import { ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';

/**
 * 处理状态与路由的双向绑定
 * @param {string} paramName - 路由参数名
 * @param {any} initialValue - 初始状态值
 * @returns {Object} 包含状态和方法的对象
 */
export function useRouteState(paramName, initialValue = null) {
  const route = useRoute();
  const router = useRouter();
  const state = ref(initialValue);

  // 初始化状态
  const initState = () => {
    const paramValue = route.query[paramName];
    if (paramValue) {
      state.value = paramValue;
    }
  };

  // 更新状态并同步到路由
  const setState = (newValue) => {
    state.value = newValue;
    if (newValue) {
      router.push({ path: route.path, query: { ...route.query, [paramName]: newValue } });
    } else {
      const newQuery = { ...route.query };
      delete newQuery[paramName];
      router.push({ path: route.path, query: newQuery });
    }
  };

  // 监听路由参数变化
  watch(() => route.query[paramName], (newValue) => {
    state.value = newValue || initialValue;
  });

  // 初始化
  initState();

  return {
    state,
    setState,
    initState
  };
}
