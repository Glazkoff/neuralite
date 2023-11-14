<script setup>
import Recorder from "./components/Recorder.vue";
</script>

<template>
  <!-- <img
    id="logo"
    alt="Wails logo"
    style="--wails-draggable: no-drag"
    src="./assets/images/logo-universal.png"
    draggable="false"
  /> -->
  <Recorder />
</template>

<style>
#logo {
  display: block;
  width: 50%;
  height: 50%;
  margin: auto;
  padding: 10% 0 0;
  box-sizing: border-box;
  background-position: center;
  background-repeat: no-repeat;
  background-size: 100% 100%;
  background-origin: content-box;
}
</style>
