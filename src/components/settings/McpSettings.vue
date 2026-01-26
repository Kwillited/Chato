<template>
  <div class="space-y-6 max-w-2xl mx-auto">
    <div class="card p-4 depth-1 hover:depth-2 transition-all duration-300">
      <h4 class="font-medium mb-4">MCP服务配置</h4>

      <div class="space-y-4">
        <div class="setting-item p-3 rounded-lg">
          <div class="flex justify-between items-center">
            <div>
              <div class="font-medium text-sm">启用MCP服务</div>
              <div class="text-xs text-neutral mt-0.5">启用后可连接到MCP服务器进行数据交换</div>
            </div>
            <label class="toggle-switch">
              <input type="checkbox" :checked="settingsStore.mcpConfig.enabled" @change="handleMcpEnabledChange" />
              <span class="toggle-slider"></span>
            </label>
          </div>
        </div>

        <div class="setting-item p-3 rounded-lg">
          <div>
            <div class="font-medium text-sm">MCP服务器配置</div>
            <div class="text-xs text-neutral mt-0.5">MCP服务器的IP地址或域名和端口号</div>
            
            <div class="flex space-x-2 mt-2">
              <input
                type="text"
                v-model="settingsStore.mcpConfig.serverAddress"
                class="input-field flex-1 text-sm px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-primary"
                placeholder="例如：127.0.0.1"
                @change="updateMcpConfig"
              />
              <span class="flex items-center text-neutral">:</span>
              <input
                type="number"
                v-model="settingsStore.mcpConfig.serverPort"
                class="input-field w-24 text-sm px-2 py-1.5 focus:outline-none focus:ring-1 focus:ring-primary"
                placeholder="8080"
                min="1"
                max="65535"
                @change="updateMcpConfig"
              />
            </div>
          </div>
        </div>

        <div class="setting-item p-3 rounded-lg">
          <div>
            <div class="font-medium text-sm">MCP服务超时设置 (秒)</div>
            <div class="text-xs text-neutral mt-0.5">连接MCP服务器的超时时间</div>

            <input
              type="number"
              v-model="settingsStore.mcpConfig.timeout"
              class="input-field w-full text-sm px-2 py-1.5 mt-2 focus:outline-none focus:ring-1 focus:ring-primary"
              placeholder="例如：30"
              min="1"
              max="300"
              @change="updateMcpConfig"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useSettingsStore } from '../../store/settingsStore.js';

const settingsStore = useSettingsStore();

// 处理MCP启用状态变更
function handleMcpEnabledChange(event) {
  const enabled = event.target.checked;
  settingsStore.toggleMcp(enabled);
}

// 更新MCP配置
function updateMcpConfig() {
  // 由于使用了v-model，直接保存整个配置对象
  settingsStore.saveSettings();
}
</script>
