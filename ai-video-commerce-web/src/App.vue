<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <RouterView />
</template>

<style>
* {
  box-sizing: border-box;
}

html,
body,
#app {
  min-height: 100%;
  margin: 0;
}

body {
  font-family: Inter, 'Microsoft YaHei', Arial, sans-serif;
  background: #f5f7fa;
}
</style>