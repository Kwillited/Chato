import { computed } from 'vue';
import { useSettingsStore } from '../store/settingsStore.js';

/**
 * 主题状态管理组合函数
 * 用于管理应用的主题、字体大小、字体家族等状态和操作
 */
export function useThemeState() {
  const settingsStore = useSettingsStore();
  
  // 计算属性：当前深色模式状态
  const isDarkMode = computed(() => settingsStore.systemSettings.darkMode);
  
  // 计算属性：当前字体大小
  const fontSize = computed(() => settingsStore.systemSettings.fontSize);
  
  // 计算属性：当前字体家族
  const fontFamily = computed(() => settingsStore.systemSettings.fontFamily);
  
  // 计算属性：当前语言
  const language = computed(() => settingsStore.systemSettings.language);
  
  // 方法：切换深色模式
  const toggleDarkMode = () => {
    settingsStore.toggleDarkMode();
  };
  
  // 方法：设置字体大小
  const setFontSize = (size) => {
    settingsStore.updateSystemSettings({ fontSize: size });
  };
  
  // 方法：设置字体家族
  const setFontFamily = (family) => {
    settingsStore.updateSystemSettings({ fontFamily: family });
  };
  
  // 方法：设置语言
  const setLanguage = (lang) => {
    settingsStore.updateSystemSettings({ language: lang });
  };
  
  // 方法：应用主题设置
  const applyThemeSettings = () => {
    // 应用深色模式
    settingsStore.applyDarkMode();
    
    // 应用字体大小
    if (settingsStore.systemSettings.fontSize) {
      document.documentElement.style.fontSize = `${settingsStore.systemSettings.fontSize}px`;
    }
    
    // 应用字体家族
    if (settingsStore.systemSettings.fontFamily) {
      document.body.style.fontFamily = settingsStore.systemSettings.fontFamily;
    }
  };
  
  // 方法：重置主题设置为默认值
  const resetThemeSettings = () => {
    settingsStore.updateSystemSettings({
      darkMode: false,
      fontSize: 16,
      fontFamily: 'Inter, system-ui, sans-serif',
      language: 'zh-CN',
    });
    applyThemeSettings();
  };
  
  return {
    // 状态
    isDarkMode,
    fontSize,
    fontFamily,
    language,
    
    // 方法
    toggleDarkMode,
    setFontSize,
    setFontFamily,
    setLanguage,
    applyThemeSettings,
    resetThemeSettings,
  };
}
