import { defineStore } from 'pinia';
import { StorageManager, mergeSettings } from './utils';
import { apiService } from '../services/apiService.js';
import { eventBus } from '../services/eventBus.js';
import { showNotification } from '../services/notificationUtils.js';

// 存储键名常量
const STORAGE_KEYS = {
  MODEL_SETTINGS: 'modelSettings',
};

// 定义模型参数的类型描述
/**
 * @typedef {Object} ModelParams
 * @property {number} temperature - 温度参数
 * @property {number} max_tokens - 最大生成token数
 * @property {number} top_p - 采样参数
 * @property {number} top_k - 采样参数
 * @property {number} frequency_penalty - 频率惩罚
 */

export const useModelSettingStore = defineStore('modelSetting', {
  state: () => ({
    // 模型相关设置
    availableModels: [],
    models: [], // 存储所有模型配置
    modelParams: {
      temperature: 0.7,
      max_tokens: 2000,
      top_p: 1.0,
      top_k: 50,
      frequency_penalty: 0.0,
    },
    
    // 加载状态
    isLoading: false,
    // 错误信息
    error: null,
  }),

  getters: {
    // 获取当前模型的参数
    currentModelParams: (state) => state.modelParams,
    
    // 获取可用模型列表
    availableModelList: (state) => state.availableModels,
    
    // 获取所有模型配置
    allModels: (state) => state.models,
    
    // 获取已配置的模型列表
    configuredModels: (state) => state.models.filter(model => model.configured),
    
    // 获取未配置的模型列表
    unconfiguredModels: (state) => state.models.filter(model => !model.configured),
    

  },

  actions: {
    // 设置加载状态
    setLoading(loading) {
      this.isLoading = loading;
    },
    
    // 设置错误信息
    setError(error) {
      this.error = error;
      if (error) {
        console.error('模型管理错误:', error);
        // 可以在这里添加全局错误通知
      }
    },
    
    // 选择模型（仅同步到本地存储，主要通过settingsStore管理）
    selectModel(model) {
      if (this.availableModels.includes(model)) {
        // 注意：selectedModel已移至settingsStore管理
        // 此处保留方法以确保向后兼容性
        this.saveModelSettings();
      }
    },

    // 更新模型参数
    updateModelParams(params) {
      this.modelParams = { ...this.modelParams, ...params };
      this.saveModelSettings();
    },

    // 从后端加载模型列表
    async loadModels() {
      try {
        this.setLoading(true);
        this.setError(null);
        
        // 从后端加载模型列表
        const response = await apiService.models.getModels();
        // 确保models是数组
        this.models = Array.isArray(response.models) ? response.models : [];
        
        // 更新可用模型列表
        this.updateAvailableModels();
        
        // 通知事件总线，模型列表已更新
        eventBus.emit('modelsLoaded', { models: this.models });
      } catch (error) {
        this.setError('加载模型列表失败');
        console.error('加载模型列表失败:', error);
      } finally {
        this.setLoading(false);
      }
    },

    // 更新模型数据，添加图标URL
    updateModelsWithIcons(configuredModels, unconfiguredModels) {
      // 首先更新已配置模型
      const updatedModels = [...this.models];
      
      // 更新已配置模型
      configuredModels.forEach(configuredModel => {
        const index = updatedModels.findIndex(m => m.name === configuredModel.name);
        if (index !== -1) {
          updatedModels[index] = configuredModel;
        }
      });
      
      // 更新未配置模型
      unconfiguredModels.forEach(unconfiguredModel => {
        const index = updatedModels.findIndex(m => m.name === unconfiguredModel.name);
        if (index !== -1) {
          updatedModels[index] = unconfiguredModel;
        }
      });
      
      // 更新store中的models状态
      this.models = updatedModels;
      
      // 更新可用模型列表
      this.updateAvailableModels();
    },
    
    // 更新可用模型列表，与select组件保持一致的模型ID格式
    updateAvailableModels() {
      const available = [];
      
      this.models.forEach(model => {
        if (model.configured && model.enabled && model.versions) {
          model.versions.forEach(version => {
            if (version && version.version_name) {
              // 与select组件保持一致：只使用version_name构建模型标识
              // 格式：model.name-version_name
              available.push(`${model.name}-${version.version_name}`);
            }
          });
        }
      });
      
      this.availableModels = available;
    },

    // 保存模型配置
    async saveModelConfig(modelName, config) {
      try {
        this.setLoading(true);
        this.setError(null);
        
        // 调用后端API保存配置
        await apiService.post(`/api/models/${modelName}`, {
          custom_name: config.customName,
          api_key: config.apiKey,
          api_base_url: config.apiBaseUrl,
          version_name: config.versionName,
          streaming_config: config.streamingConfig
        });
        
        // 重新加载模型列表以更新状态
        await this.loadModels();
        
        // 通过事件总线通知模型已更新
        eventBus.emit('modelUpdated');
        
        return true;
      } catch (error) {
        this.setError('保存模型配置失败');
        console.error('保存模型配置失败:', error);
        throw error;
      } finally {
        this.setLoading(false);
      }
    },

    // 删除模型配置
    async deleteModelConfig(modelName) {
      try {
        this.setLoading(true);
        this.setError(null);
        
        // 调用后端API删除配置
        await apiService.delete(`/api/models/${modelName}`);
        
        // 重新加载模型列表以更新状态
        await this.loadModels();
        
        // 通过事件总线通知模型已更新
        eventBus.emit('modelUpdated');
        
        // 显示成功通知
        showNotification(`已删除${modelName}的配置`, 'success');
        
        return true;
      } catch (error) {
        this.setError('删除模型配置失败');
        console.error('删除模型配置失败:', error);
        showNotification('删除失败: ' + (error.message || '未知错误'), 'error');
        throw error;
      } finally {
        this.setLoading(false);
      }
    },

    // 切换模型启用状态
    async toggleModelEnabled(modelName, enabled) {
      try {
        this.setLoading(true);
        this.setError(null);
        
        // 调用后端API更新启用状态
        await apiService.post(`/api/models/${modelName}/enabled`, {
          enabled: enabled
        });
        
        // 重新加载模型列表以更新状态
        await this.loadModels();
        
        // 通过事件总线通知模型已更新
        eventBus.emit('modelUpdated');
        
        return true;
      } catch (error) {
        this.setError('更新模型启用状态失败');
        console.error('更新模型启用状态失败:', error);
        throw error;
      } finally {
        this.setLoading(false);
      }
    },

    // 添加模型版本
    async addModelVersion(modelName, versionConfig) {
      try {
        this.setLoading(true);
        this.setError(null);
        
        // 构建请求数据
        const modelConfig = {
          custom_name: versionConfig.customName,
          api_key: versionConfig.apiKey,
          api_base_url: versionConfig.apiBaseUrl,
          version_name: versionConfig.versionName,
          streaming_config: versionConfig.streamingConfig
        };
        
        console.log('发送的API请求数据:', JSON.stringify(modelConfig));
        
        // 调用后端API保存配置
        await apiService.post(`/api/models/${modelName}`, modelConfig);
        
        // 重新加载模型列表以更新状态
        await this.loadModels();
        
        // 通过事件总线通知模型已更新
        eventBus.emit('modelUpdated');
        
        return true;
      } catch (error) {
        this.setError('添加模型版本失败');
        console.error('添加模型版本失败:', error);
        throw error;
      } finally {
        this.setLoading(false);
      }
    },

    // 编辑模型版本
    async updateModelVersion(modelName, versionName, versionConfig) {
      try {
        this.setLoading(true);
        this.setError(null);
        
        // 构建请求数据
        const requestData = {
          custom_name: versionConfig.customName,
          api_key: versionConfig.apiKey,
          api_base_url: versionConfig.apiBaseUrl,
          version_name: versionConfig.versionName,
          streaming_config: versionConfig.streamingConfig
        };
        
        // 调用API保存配置
        await apiService.post(`/api/models/${modelName}`, requestData);
        
        // 重新加载模型列表以更新状态
        await this.loadModels();
        
        // 通过事件总线通知模型已更新
        eventBus.emit('modelUpdated');
        
        return true;
      } catch (error) {
        this.setError('更新模型版本失败');
        console.error('更新模型版本失败:', error);
        throw error;
      } finally {
        this.setLoading(false);
      }
    },

    // 删除模型版本
    async deleteModelVersion(modelName, versionName) {
      try {
        this.setLoading(true);
        this.setError(null);
        
        // 调用后端API删除模型版本
        await apiService.delete(`/api/models/${modelName}/versions/${versionName}`);
        
        // 重新加载模型列表以更新状态
        await this.loadModels();
        
        // 通过事件总线通知模型已更新
        eventBus.emit('modelUpdated');
        
        // 查找模型和版本信息用于通知
        const model = this.models.find(m => m.name === modelName);
        const version = model?.versions?.find(v => v.version_name === versionName);
        
        // 显示成功通知
        showNotification(`已删除${modelName}的版本 ${version?.custom_name || versionName}`, 'success');
        
        return true;
      } catch (error) {
        this.setError('删除模型版本失败');
        console.error('删除模型版本失败:', error);
        showNotification('删除失败: ' + (error.message || '未知错误'), 'error');
        throw error;
      } finally {
        this.setLoading(false);
      }
    },

    // 重置模型设置为默认值
    resetModelSettings() {
      this.modelParams = {
        temperature: 0.7,
        max_tokens: 2000,
        top_p: 1.0,
        top_k: 50,
        frequency_penalty: 0.0,
      };
      this.availableModels = [];
      this.error = null;
      this.saveModelSettings();
    },

    // 从存储中加载模型设置
    loadModelSettings() {
      try {
        const savedSettings = StorageManager.getItem(STORAGE_KEYS.MODEL_SETTINGS);
        if (savedSettings) {
          this.mergeSavedModelSettings(savedSettings);
        }
      } catch (error) {
        console.error('加载模型设置失败:', error);
        // 加载失败时使用默认设置
        this.resetModelSettings();
      }
    },

    // 合并保存的模型设置
    mergeSavedModelSettings(savedSettings) {
      if (savedSettings.modelParams && typeof savedSettings.modelParams === 'object') {
        this.modelParams = mergeSettings(this.modelParams, savedSettings.modelParams);
      }

      // 注意：selectedModel已移至settingsStore管理
    },

    // 保存模型设置的核心功能
    _saveModelSettingsCore: function() {
      try {
        const settingsToSave = {
          modelParams: this.modelParams,
          timestamp: Date.now(),
        };

        const saved = StorageManager.setItem(STORAGE_KEYS.MODEL_SETTINGS, settingsToSave);
        return saved;
      } catch (error) {
        console.error('保存模型设置失败:', error);
        return false;
      }
    },

    // 保存模型设置
    saveModelSettings: function() {
      return this._saveModelSettingsCore();
    },
  },
});