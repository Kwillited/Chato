import { computed } from 'vue';

export function useModelUtils(modelStore) {
  // 获取所有可用模型版本
  const allModelVersions = computed(() => {
    const versions = [];
    
    modelStore.allModels.forEach(model => {
      if (model.configured && model.versions) {
        model.versions.forEach(version => {
          const versionName = version?.version_name;
          if (versionName) {
            // 检查是否是默认模型版本
            const isDefaultVersion = model.is_default && model.default_version === versionName;
            // 包含启用的版本或默认版本
            if (version.enabled || isDefaultVersion) {
              const id = `${model.name}-${versionName}`;
              const displayName = `${model.name}-${version.custom_name || versionName}`;
              
              versions.push({
                id,
                displayName
              });
            }
          }
        });
      }
    });
    
    return versions;
  });

  // 获取所有可用嵌入模型版本
  const allEmbeddingModelVersions = computed(() => {
    const versions = [];
    
    (modelStore.allEmbeddingModels || []).forEach(model => {
      if (model.configured && model.versions) {
        model.versions.forEach(version => {
          const versionName = version?.version_name;
          if (versionName) {
            const id = `${model.name}-${versionName}`;
            const displayName = `${model.name}-${version.custom_name || versionName}`;
            
            versions.push({
              id,
              displayName
            });
          }
        });
      }
    });
    
    return versions;
  });

  // 获取可用模型ID列表
  const availableModelIds = computed(() => {
    return allModelVersions.value.map(version => version.id);
  });

  // 获取可用嵌入模型ID列表
  const availableEmbeddingModelIds = computed(() => {
    return allEmbeddingModelVersions.value.map(version => version.id);
  });

  // 获取格式化后的模型列表
  const formattedModels = computed(() => {
    return allModelVersions.value.map(version => ({
      value: version.id,
      displayName: version.displayName
    }));
  });

  // 获取格式化后的嵌入模型列表
  const formattedEmbeddingModels = computed(() => {
    return allEmbeddingModelVersions.value.map(version => ({
      value: version.id,
      label: version.displayName
    }));
  });

  // 获取模型显示名称
  const getModelDisplayName = (modelId) => {
    if (!modelId || !modelStore.allModels.length) {
      return modelId || '默认模型';
    }
    
    for (const model of modelStore.allModels) {
      if (model.versions) {
        for (const version of model.versions) {
          const selectModelId = `${model.name}-${version.version_name}`;
          if (selectModelId === modelId || 
              version.version_name === modelId || 
              version.custom_name === modelId) {
            const modelDisplay = model.name;
            const versionDisplay = version.custom_name || version.version_name;
            return `${modelDisplay}-${versionDisplay}`;
          }
        }
      }
    }
    
    return modelId || '默认模型';
  };

  // 获取嵌入模型显示名称
  const getEmbeddingModelDisplayName = (modelId) => {
    if (!modelId || !modelStore.allEmbeddingModels || !modelStore.allEmbeddingModels.length) {
      return modelId || '默认嵌入模型';
    }
    
    for (const model of modelStore.allEmbeddingModels) {
      if (model.versions) {
        for (const version of model.versions) {
          const selectModelId = `${model.name}-${version.version_name}`;
          if (selectModelId === modelId || 
              version.version_name === modelId || 
              version.custom_name === modelId) {
            const modelDisplay = model.name;
            const versionDisplay = version.custom_name || version.version_name;
            return `${modelDisplay}-${versionDisplay}`;
          }
        }
      }
    }
    
    return modelId || '默认嵌入模型';
  };

  return {
    allModelVersions,
    allEmbeddingModelVersions,
    availableModelIds,
    availableEmbeddingModelIds,
    formattedModels,
    formattedEmbeddingModels,
    getModelDisplayName,
    getEmbeddingModelDisplayName
  };
}
