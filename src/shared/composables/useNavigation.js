// 导航组合式函数，封装应用内的路由导航逻辑
import { useRouter } from 'vue-router';
import { useSettingsStore } from '../../app/store/settingsStore.js';

/**
 * 导航组合式函数，封装应用内的路由导航逻辑
 * @returns {Object} 包含导航相关的方法
 */
export function useNavigation() {
  const router = useRouter();
  const settingsStore = useSettingsStore();

  /**
   * 跳转到聊天页面
   */
  const navigateToChat = () => {
    router.push('/chat');
  };

  /**
   * 跳转到首页
   */
  const navigateToHome = () => {
    router.push('/');
  };

  /**
   * 跳转到设置页面
   */
  const navigateToSettings = () => {
    router.push('/settings');
  };

  /**
   * 导航回上一页
   */
  const navigateBack = () => {
    router.back();
  };

  return {
    navigateToChat,
    navigateToHome,
    navigateToSettings,
    navigateBack
  };
}
