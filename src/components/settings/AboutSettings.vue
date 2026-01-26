<template>
  <div class="max-w-2xl mx-auto">
    <div class="text-center mb-8">
      <div
        class="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4 shadow-sm hover-scale"
      >
        <i class="fa-regular fa-comments text-primary text-3xl"></i>
      </div>
      <h3 class="font-semibold text-xl">Chato</h3>
      <div class="text-sm text-neutral mt-1">版本 v1.0.0</div>
    </div>

    <div class="card p-6 mb-6 depth-1 hover:depth-2 transition-all duration-300">
      <h4 class="font-medium mb-3">关于应用</h4>
      <p class="text-sm text-gray-700">Chato新生代全栈AI应用平台，满足你所想、符合你所需</p>
    </div>

    <div class="space-y-3">
      <button
        class="w-full text-left p-3 rounded-lg text-primary hover:bg-primary/5 transition-colors flex items-center justify-between hover-scale"
      >
        <span><i class="fa-regular fa-file-lines mr-2"></i> 使用条款</span>
        <i class="fa-solid fa-chevron-right text-xs"></i>
      </button>

      <button
        class="w-full text-left p-3 rounded-lg text-primary hover:bg-primary/5 transition-colors flex items-center justify-between hover-scale"
      >
        <span><i class="fa-solid fa-shield-halved mr-2"></i> 隐私政策</span>
        <i class="fa-solid fa-chevron-right text-xs"></i>
      </button>

      <button
        class="w-full text-left p-3 rounded-lg text-primary hover:bg-primary/5 transition-colors flex items-center justify-between hover-scale"
      >
        <span><i class="fa-solid fa-circle-question mr-2"></i> 帮助中心</span>
        <i class="fa-solid fa-chevron-right text-xs"></i>
      </button>

      <a
        href="https://github.com/Kwillited/Chato"
        target="_blank"
        rel="noopener noreferrer"
        class="w-full text-left p-3 rounded-lg text-primary hover:bg-primary/5 transition-colors flex items-center justify-between hover-scale"
      >
        <span><i class="fa-brands fa-github mr-2"></i> 开源仓库</span>
        <i class="fa-solid fa-chevron-right text-xs"></i>
      </a>
    </div>

    <div class="mt-10 text-center text-xs text-neutral">© 2025 Chato. 保留所有权利.</div>
  </div>
</template>

<script setup>
// 关于页面组件逻辑
</script>
