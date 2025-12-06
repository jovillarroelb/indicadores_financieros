<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const props = defineProps({
  intervalMinutes: {
    type: Number,
    default: 15
  }
})

const emit = defineEmits(['refresh'])

const remainingSeconds = ref(props.intervalMinutes * 60)
let timer = null
let intervalId = null

const formatTime = (seconds) => {
  const m = Math.floor(seconds / 60)
  const s = seconds % 60
  return `${m}:${s.toString().padStart(2, '0')}`
}

const tick = () => {
  remainingSeconds.value--
  if (remainingSeconds.value <= 0) {
    emit('refresh')
    remainingSeconds.value = props.intervalMinutes * 60
  }
}

const reset = () => {
    remainingSeconds.value = props.intervalMinutes * 60
}

onMounted(() => {
  intervalId = setInterval(tick, 1000)
})

onUnmounted(() => {
  clearInterval(intervalId)
})

defineExpose({ reset })
</script>

<template>
  <div class="update-timer">
    <span class="label">Próxima actualización en: </span>
    <span class="time">{{ formatTime(remainingSeconds) }}</span>
  </div>
</template>

<style scoped>
.update-timer {
  background: rgba(255, 255, 255, 0.1);
  padding: 0.5rem 1rem;
  border-radius: 20px;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--text-secondary);
}

.time {
  color: var(--accent-color);
  font-weight: bold;
  font-feature-settings: "tnum";
  font-variant-numeric: tabular-nums;
  min-width: 45px;
}
</style>
