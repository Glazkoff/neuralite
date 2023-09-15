<script setup>
import { reactive } from "vue";

const data = reactive({
  isFullScreen: false
});

function switchFullScreen(params) {
  data.isFullScreen = !data.isFullScreen;
  if (data.isFullScreen) {
    window.runtime.WindowUnfullscreen();
  } else {
    window.runtime.WindowFullscreen();
  }
}
</script>

<template>
  <button type="button" class="btn" @click="switchFullScreen">
    {{ data.isFullScreen ? "Full" : "Unfull" }}
  </button>
</template>

<style scoped>
.btn {
  width: 60px;
  height: 30px;
  line-height: 30px;
  border-radius: 3px;
  border: none;
  margin: 0 0 0 20px;
  padding: 0 8px;
  cursor: pointer;
}
</style>
