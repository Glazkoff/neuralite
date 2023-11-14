<script setup>
import { reactive } from "vue";

const data = reactive({
  isFullScreen: false
});

function switchFullScreen(params) {
  if (data.isFullScreen) {
    window.runtime.WindowUnfullscreen();
  } else {
    window.runtime.WindowFullscreen();
  }
  data.isFullScreen = !data.isFullScreen;
}
</script>

<template>
  <button type="button" class="btn" @click="switchFullScreen">
    {{ data.isFullScreen ? "Unfull" : "Full" }}
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
