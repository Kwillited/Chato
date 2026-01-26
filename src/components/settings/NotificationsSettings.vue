<template>
  <div class="space-y-6 max-w-2xl mx-auto">
    <div class="card p-4 depth-1 hover:depth-2 transition-all duration-300">
      <h4 class="font-medium mb-4">通知偏好</h4>

      <div class="space-y-4">
        <SettingItem
          type="toggle"
          title="新消息通知"
          description="当收到AI回复时通知"
          v-model="settingsStore.notificationsConfig.newMessage"
          @change="settingsStore.saveSettings"
        />

        <SettingItem
          type="toggle"
          title="声音提示"
          description="新消息通知时播放提示音"
          v-model="settingsStore.notificationsConfig.sound"
          @change="settingsStore.saveSettings"
        />

        <SettingItem
          type="toggle"
          title="系统通知"
          description="显示应用更新等系统通知"
          v-model="settingsStore.notificationsConfig.system"
          @change="settingsStore.saveSettings"
        />

        <SettingItem
          type="select"
          title="通知显示时间"
          description="控制通知在屏幕上停留的时间"
          v-model="settingsStore.notificationsConfig.displayTime"
          :options="displayTimeOptions"
          @change="settingsStore.saveSettings"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { useSettingsStore } from '../../store/settingsStore.js';
import SettingItem from '../common/SettingItem.vue';

const settingsStore = useSettingsStore();

// 通知显示时间选项
const displayTimeOptions = [
  { value: '2秒', label: '2秒' },
  { value: '5秒', label: '5秒' },
  { value: '10秒', label: '10秒' }
];
</script>
