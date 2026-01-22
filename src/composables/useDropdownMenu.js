import { ref, onMounted, onUnmounted } from 'vue';

/**
 * 下拉菜单组合式函数，用于管理下拉菜单的显示、隐藏和点击外部关闭等逻辑
 * @param {Object} options - 配置选项
 * @param {string} [options.menuSelector='.relative.hover-scale'] - 菜单按钮选择器
 * @returns {Object} 包含下拉菜单相关的状态和方法
 */
export function useDropdownMenu(options = {}) {
  const { menuSelector = '.relative.hover-scale' } = options;
  
  // 菜单显示状态
  const isMenuOpen = ref(false);
  
  /**
   * 切换菜单显示状态
   */
  const toggleMenu = () => {
    isMenuOpen.value = !isMenuOpen.value;
  };
  
  /**
   * 打开菜单
   */
  const openMenu = () => {
    isMenuOpen.value = true;
  };
  
  /**
   * 关闭菜单
   */
  const closeMenu = () => {
    isMenuOpen.value = false;
  };
  
  /**
   * 点击外部区域关闭菜单
   * @param {MouseEvent} event - 鼠标点击事件
   */
  const handleClickOutside = (event) => {
    const menuButtons = document.querySelectorAll(menuSelector);
    
    let clickedInsideMenu = false;
    menuButtons.forEach(button => {
      if (button.contains(event.target)) {
        clickedInsideMenu = true;
      }
    });
    
    if (!clickedInsideMenu) {
      isMenuOpen.value = false;
    }
  };
  
  /**
   * 点击菜单内的项后关闭菜单
   * @param {Function} callback - 点击项的回调函数
   * @returns {Function} 包装后的回调函数
   */
  const handleMenuItemClick = (callback) => {
    return (...args) => {
      closeMenu();
      if (callback) {
        callback(...args);
      }
    };
  };
  
  // 添加点击外部事件监听
  onMounted(() => {
    document.addEventListener('click', handleClickOutside);
  });
  
  // 移除事件监听
  onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside);
  });
  
  return {
    // 状态
    isMenuOpen,
    
    // 方法
    toggleMenu,
    openMenu,
    closeMenu,
    handleMenuItemClick
  };
}