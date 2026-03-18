<template>
  <div class="space-y-6 max-w-2xl mx-auto">
    <Card>
      <!-- 选项卡导航 -->
      <div class="border-b">
        <div class="flex">
          <button
            class="px-6 py-3 text-sm font-medium border-b-2 transition-colors"
            :class="activeTab === 'basic' ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
            @click="activeTab = 'basic'"
          >
            基本设置
          </button>
          <button
            class="px-6 py-3 text-sm font-medium border-b-2 transition-colors"
            :class="activeTab === 'paths' ? 'border-primary text-primary' : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'"
            @click="activeTab = 'paths'"
          >
            路径设置
          </button>
        </div>
      </div>

      <!-- 基本设置选项卡 -->
      <div v-show="activeTab === 'basic'" class="p-4">
        <div class="space-y-4">
          <div class="setting-item p-3 rounded-lg">
            <div>
              <div class="font-medium text-sm">Embedder模型</div>
              <div class="text-xs text-neutral mt-0.5">用于将文本转换为向量的模型</div>

              <select
                v-model="vectorStore.config.embedding.model"
                class="input-field w-full text-sm px-2 py-1.5 mt-2 focus:outline-none focus:ring-1 focus:ring-primary"
                @change="updateVectorConfig"
              >
                <option value="qwen3-embedding-0.6b">qwen3-embedding-0.6b (推荐)</option>
                <option value="all-MiniLM-L6-v2">all-MiniLM-L6-v2 (轻量)</option>
                <option value="all-mpnet-base-v2">all-mpnet-base-v2 (更精确)</option>
                <option value="all-MiniLM-L12-v2">all-MiniLM-L12-v2 (平衡)</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- 路径设置选项卡 -->
      <div v-show="activeTab === 'paths'" class="p-4">
        <div class="space-y-4">
          <div class="setting-item p-3 rounded-lg">
            <div>
              <div class="font-medium text-sm">向量数据库路径</div>
              <div class="text-xs text-neutral mt-0.5">向量数据的存储位置（留空使用系统默认路径）</div>

              <input
                type="text"
                v-model="vectorStore.config.storage.path"
                class="input-field w-full text-sm px-2 py-1.5 mt-2 focus:outline-none focus:ring-1 focus:ring-primary"
                placeholder="留空使用默认路径"
                @change="updateVectorConfig"
              />
              <div class="text-xs text-neutral mt-1">系统默认路径: 用户数据目录下的 "Retrieval-Augmented Generation\vectorDb"</div>
            </div>
          </div>

          <div class="setting-item p-3 rounded-lg">
            <div>
              <div class="font-medium text-sm">知识库存储路径</div>
              <div class="text-xs text-neutral mt-0.5">知识库文档文件的存储位置（留空使用系统默认路径）</div>

              <input
                type="text"
                v-model="vectorStore.config.storage.knowledgeBasePath"
                class="input-field w-full text-sm px-2 py-1.5 mt-2 focus:outline-none focus:ring-1 focus:ring-primary"
                placeholder="留空使用默认路径"
                @change="updateVectorConfig"
              />
              <div class="text-xs text-neutral mt-1">系统默认路径: 用户数据目录下的 "Retrieval-Augmented Generation\knowledgeBase"</div>
            </div>
          </div>
        </div>
      </div>
    </Card>
  </div>
</template>



<script setup>
import { ref } from 'vue';
import { useVectorStore } from '../../store/vectorStore.js';
import { Card } from '../library/index.js';

const vectorStore = useVectorStore();
// 活动选项卡，默认为基本设置
const activeTab = ref('basic');

// 更新向量配置
function updateVectorConfig() {
  // 向量配置变更，vectorStore内部会处理状态更新
}
</script>