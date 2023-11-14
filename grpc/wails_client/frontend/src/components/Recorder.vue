<script setup>
import { reactive } from "vue";
import { ProcessAudioBase64 } from "../../wailsjs/go/main/App";
import FullScreenBtn from "./FullScreenBtn.vue";

const data = reactive({
  name: "",
  resultText: "Пожалуйста, начните запись 👇",
  isRecording: false,
  audioStream: null,
  mediaRecorder: null,
  startTime: null,
  elapsedTime: 0
});

function setElapsedTime() {
  let currentTime = new Date();
  if (data.startTime != null) {
    let elapsedTime = (currentTime - data.startTime) / 1000;
    data.elapsedTime = Math.round(elapsedTime * 100) / 100;
  }
}

function voiceRecording() {
  if (!data.isRecording) {
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      console.log("getUserMedia supported.");

      data.audioStream = navigator.mediaDevices
        .getUserMedia(
          // constraints - only audio needed for this app
          {
            audio: true
          }
        )

        // Success callback
        .then(stream => {
          data.audioStream = stream;
          // TODO: const mimeTypes = MediaRecorder.isTypeSupported("audio/wav");
          data.mediaRecorder = new MediaRecorder(data.audioStream, {
            audioBitsPerSecond: 128000
            // mimeType: mimeTypes[0]
          });
          const sampleRate = data.mediaRecorder.audioBitsPerSecond / (16 * 1);
          console.log("data.mediaRecorder", sampleRate, data.mediaRecorder);
          data.mediaRecorder.start();
          // TODO: data.mediaRecorder.start(400);

          data.elapsedTime = 0;
          data.startTime = new Date();
          data.mediaRecorder.ondataavailable = e => {
            const blob = e.data;
            console.log(blob);

            const reader = new window.FileReader();
            reader.readAsDataURL(blob);

            reader.onloadend = function () {
              let base64 = reader.result;
              base64 = base64.split(",")[1];
              console.log(base64.slice(0, 10) + "...");

              // ProcessAudioBase64(base64);
            };
          };
          data.resultText = data.mediaRecorder.state;
        })

        // Error callback
        .catch(err => {
          console.error(`The following getUserMedia error occurred: ${err}`);
        });
    } else {
      console.log("getUserMedia not supported on your browser!");
    }
  } else {
    if (data.mediaRecorder != null) {
      data.mediaRecorder.stop();
      data.resultText = data.mediaRecorder.state + data.mediaRecorder;
    } else {
      data.resultText = "-";
    }
    setElapsedTime();
    console.log("close");
  }

  data.isRecording = !data.isRecording;
}

setInterval(() => {
  if (data.isRecording) {
    setElapsedTime();
  }
}, 100);

window.runtime.EventsOn("get_response", newText => {
  data.resultText = newText.join(" ");
});
</script>

<template>
  <main>
    <div id="result" class="result">{{ data.resultText }}</div>
    <div id="input" class="input-box">
      <p>Записано секунд: {{ data.elapsedTime }}</p>
      <!-- <FullScreenBtn></FullScreenBtn> -->
      <button class="btn" @click="voiceRecording">
        {{ data.isRecording ? "Stop" : "Record" }}
      </button>
    </div>
  </main>
</template>

<style scoped>
.result {
  height: 20px;
  line-height: 20px;
  margin: 1.5rem auto;
}

.input-box .btn {
  width: 60px;
  height: 30px;
  line-height: 30px;
  border-radius: 3px;
  border: none;
  margin: 0 0 0 20px;
  padding: 0 8px;
  cursor: pointer;
}

.input-box .btn:hover {
  background-image: linear-gradient(to top, #cfd9df 0%, #e2ebf0 100%);
  color: #333333;
}

.input-box .input {
  border: none;
  border-radius: 3px;
  outline: none;
  height: 30px;
  line-height: 30px;
  padding: 0 10px;
  background-color: rgba(240, 240, 240, 1);
  -webkit-font-smoothing: antialiased;
}

.input-box .input:hover {
  border: none;
  background-color: rgba(255, 255, 255, 1);
}

.input-box .input:focus {
  border: none;
  background-color: rgba(255, 255, 255, 1);
}
</style>
