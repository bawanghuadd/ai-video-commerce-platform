<script setup>
defineProps({
  title: {
    type: String,
    required: true,
  },

  value: {
    type: [String, Number],
    default: 0,
  },

  icon: {
    type: Object,
    required: true,
  },

  tone: {
    type: String,
    default: 'purple',
  },
})
</script>

<template>
  <article class="stat-card">
    <div
      class="stat-icon"
      :class="tone"
    >
      <el-icon>
        <component :is="icon" />
      </el-icon>
    </div>

    <div class="stat-content">
      <span>{{ title }}</span>
      <strong>{{ value }}</strong>
    </div>
  </article>
</template>

<style scoped>
.stat-card {
  display: flex;
  height: 74px;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  background: #111621;
  border: 1px solid #202736;
  border-radius: 7px;
}

.stat-icon {
  display: flex;
  width: 38px;
  height: 38px;
  flex: 0 0 38px;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  border-radius: 9px;
}

.stat-icon.purple {
  color: #927dff;
  background: rgba(118, 91, 255, 0.12);
}

.stat-icon.green {
  color: #55d6a2;
  background: rgba(45, 190, 135, 0.11);
}

.stat-icon.orange {
  color: #e2ae60;
  background: rgba(226, 174, 96, 0.1);
}

.stat-icon.cyan {
  color: #48c5d2;
  background: rgba(72, 197, 210, 0.1);
}

.stat-content {
  display: flex;
  min-width: 0;
  flex-direction: column;
}

.stat-content span {
  color: #737c8d;
  font-size: 12px;
}

.stat-content strong {
  margin-top: 4px;
  overflow: hidden;
  color: #edf0f5;
  font-size: 20px;
  font-weight: 500;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>