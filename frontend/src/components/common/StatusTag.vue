<template>
  <a-tag :color="color" class="status-tag">
    <slot>{{ label }}</slot>
  </a-tag>
</template>

<script setup lang="ts">
interface Props {
  type?: 'success' | 'warning' | 'error' | 'processing' | 'default';
  label?: string;
  color?: string;
}

defineProps<Props>();
</script>

<style scoped>
.status-tag {
  border-radius: 2px;
  font-weight: 500;
  padding: 0 8px;
}
</style>
