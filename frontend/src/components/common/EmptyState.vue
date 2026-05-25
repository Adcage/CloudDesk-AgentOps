<template>
  <div class="empty-state">
    <a-empty :description="description">
      <template #image>
        <slot name="icon">
          <InboxOutlined style="font-size: 64px; color: #d9d9d9" />
        </slot>
      </template>
      <slot></slot>
    </a-empty>
  </div>
</template>

<script setup lang="ts">
import { InboxOutlined } from '@ant-design/icons-vue';

interface Props {
  description?: string;
}

withDefaults(defineProps<Props>(), {
  description: '暂无数据'
});
</script>

<style scoped>
.empty-state {
  padding: 48px 0;
  text-align: center;
}
</style>
