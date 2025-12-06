<script setup>
import { ref, onMounted } from 'vue'

const isDark = ref(true)

const toggleTheme = () => {
  isDark.value = !isDark.value
  updateTheme()
}

const updateTheme = () => {
  const root = document.documentElement
  if (isDark.value) {
    root.classList.remove('light-mode')
    localStorage.setItem('theme', 'dark')
  } else {
    root.classList.add('light-mode')
    localStorage.setItem('theme', 'light')
  }
}

onMounted(() => {
  // Check local storage or system preference
  const savedTheme = localStorage.getItem('theme')
  if (savedTheme) {
    isDark.value = savedTheme === 'dark'
  } else {
    isDark.value = window.matchMedia('(prefers-color-scheme: dark)').matches
  }
  updateTheme()
})
</script>

<template>
  <button class="theme-toggle" @click="toggleTheme" title="Cambiar Tema">
    <span v-if="isDark">☀️</span>
    <span v-else>🌙</span>
  </button>
</template>

<style scoped>
.theme-toggle {
  background: var(--bg-secondary);
  border: 1px solid rgba(128,128,128,0.3);
  color: var(--text-primary);
  font-size: 1.5rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s;
  box-shadow: var(--card-shadow);
}

.theme-toggle:hover {
  transform: scale(1.1);
  background: var(--bg-primary);
}
</style>
