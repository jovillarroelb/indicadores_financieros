<script setup>
import { ref, onMounted } from 'vue'
import IndicatorCard from './components/IndicatorCard.vue'
import Calculator from './components/Calculator.vue'
import ThemeToggle from './components/ThemeToggle.vue'
import HistoryView from './views/HistoryView.vue'
import CrossRatesTable from './components/CrossRatesTable.vue'
import UpdateTimer from './components/UpdateTimer.vue'

const indicators = ref({
  uf: null,
  dolar: null,
  euro: null,
  utm: null
})
const loading = ref(true)
const error = ref(null)

// History Modal State
const showHistory = ref(false)
const historyIndicator = ref(null)
const timerRef = ref(null)

const openHistory = (indicator = 'UF') => {
  historyIndicator.value = indicator
  showHistory.value = true
}

const fetchData = async (force = false) => {
  loading.value = true
  error.value = null
  try {
    // In dev, vite proxy will forward /api to http://localhost:8000/api
    const url = force ? '/api/indicators?force=true' : '/api/indicators'
    const response = await fetch(url)
    if (!response.ok) throw new Error('Error al obtener datos')
    indicators.value = await response.json()
    // Reset timer on manual or auto refresh if component is mounted
    if (timerRef.value) timerRef.value.reset()
  } catch (err) {
    console.error(err)
    error.value = "No se pudieron cargar los indicadores. Intente nuevamente."
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchData()
  // Refresh handled by Timer component
})
</script>

<template>
  <HistoryView 
    :isOpen="showHistory" 
    :defaultIndicator="historyIndicator"
    @close="showHistory = false"
  />

  <div class="top-bar">
    <UpdateTimer ref="timerRef" @refresh="fetchData" />
    <button class="refresh-btn" @click="fetchData(true)" title="Actualizar ahora">🔄</button>
    <button class="history-btn" @click="openHistory('UF')">📊 Ver Histórico</button>
    <ThemeToggle />
  </div>

  <div class="dashboard-header">
    <h1>Indicadores Económicos Chile</h1>
    <p>Monitoreo en tiempo real para toma de decisiones financieras.</p>
  </div>

  <div v-if="error" class="error-banner">
    {{ error }}
    <button @click="fetchData">Reintentar</button>
  </div>

  <div class="cards-grid">
    <IndicatorCard 
      :indicator="indicators.uf" 
      :loading="loading" 
      @click="openHistory('UF')"
    />
    <IndicatorCard 
      :indicator="indicators.dolar" 
      :loading="loading" 
      @click="openHistory('Dolar')"
    />
    <IndicatorCard 
      :indicator="indicators.euro" 
      :loading="loading" 
      @click="openHistory('Euro')"
    />
    <IndicatorCard 
      :indicator="indicators.utm" 
      :loading="loading" 
      @click="openHistory('UTM')"
    />
  </div>

  <div class="calculator-section">
    <div class="tools-grid">
    <Calculator :indicators="indicators" />
    <CrossRatesTable :indicators="indicators" :loading="loading" />
  </div>
  </div>
</template>

<style scoped>
.error-banner {
  background: var(--error-color);
  color: white;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.error-banner button {
  background: white;
  color: var(--error-color);
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}
</style>
