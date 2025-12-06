<script setup>
defineProps({
  indicator: Object,
  loading: Boolean
})

const formatValue = (val) => {
  if (val === null || val === undefined) return '-'
  return new Intl.NumberFormat('es-CL', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(val)
}

const formatPercent = (val) => {
    if (val === null || val === undefined) return '0.00%'
    return new Intl.NumberFormat('es-CL', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(val) + '%'
}

const getVarClass = (val) => {
    if (val > 0) return 'positive'
    if (val < 0) return 'negative'
    return 'neutral'
}

const formatCurrency = (value, unit) => {
  if (value === undefined || value === null) return '---'
  
  if (unit === 'Pesos') {
    return new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP' }).format(value)
  }
  // For other units like Percentage if we had them, handle here.
  // Assuming mostly CLP values for these indicators from mindicador.
  return new Intl.NumberFormat('es-CL', { style: 'currency', currency: 'CLP' }).format(value)
}
</script>

<template>
  <div class="indicator-card">
    <div v-if="loading" class="skeleton"></div>
    <div v-else-if="indicator">
      <div class="header">
        <h3>{{ indicator.nombre }}</h3>
        <span class="unit">{{ indicator.unidad_medida }}</span>
      </div>
      
      <div class="value">
        {{ formatValue(indicator.valor) }}
      </div>

      <div class="variations-grid">
        <!-- Daily -->
        <div class="var-item">
          <span class="var-label">Ayer: {{ formatValue(indicator.valor_ayer) }}</span>
          <span :class="getVarClass(indicator.variacion_diaria)">
            {{ formatPercent(indicator.variacion_diaria) }} 
            <span v-if="indicator.variacion_diaria > 0">▲</span>
            <span v-else-if="indicator.variacion_diaria < 0">▼</span>
            <span v-else>=</span>
          </span>
        </div>
        <!-- Weekly -->
        <div class="var-item border-left">
          <span class="var-label">Semana: {{ formatValue(indicator.valor_semana) }}</span>
          <span :class="getVarClass(indicator.variacion_semanal)">
            {{ formatPercent(indicator.variacion_semanal) }}
            <span v-if="indicator.variacion_semanal > 0">▲</span>
            <span v-else-if="indicator.variacion_semanal < 0">▼</span>
            <span v-else>=</span>
          </span>
        </div>
        <!-- Monthly -->
        <div class="var-item border-left">
          <span class="var-label">Mes: {{ formatValue(indicator.valor_mes) }}</span>
          <span :class="getVarClass(indicator.variacion_mensual)">
            {{ formatPercent(indicator.variacion_mensual) }}
            <span v-if="indicator.variacion_mensual > 0">▲</span>
            <span v-else-if="indicator.variacion_mensual < 0">▼</span>
            <span v-else>=</span>
          </span>
        </div>
      </div>

      <div class="footer">
        <span class="date">Actualizado: {{ indicator.fecha ? indicator.fecha.substring(0, 10) : '' }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.indicator-card {
  background: var(--bg-secondary);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: var(--card-shadow);
  transition: transform 0.2s, box-shadow 0.2s;
  min-height: 140px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.indicator-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 12px rgba(0,0,0,0.4);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.header h3 {
  margin: 0;
  font-size: 1.1rem;
  color: var(--text-secondary);
  font-weight: 500;
}

.unit {
  font-size: 0.8rem;
  background: rgba(255, 255, 255, 0.1);
  padding: 2px 8px;
  border-radius: 12px;
}

.variations-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  font-size: 0.8rem;
  margin-top: 1rem;
  background: rgba(0,0,0,0.03);
  padding: 0.5rem;
  border-radius: 6px;
}

.var-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.2rem;
  padding: 0 0.5rem;
}

.border-left {
  border-left: 1px solid var(--border-color);
}

.var-label {
  color: var(--text-secondary);
  font-size: 0.75rem;
}

.positive { color: var(--success-color); }
.negative { color: var(--error-color); }
.neutral { color: var(--text-secondary); }

.card-footer {
  margin-top: 1rem;
  justify-content: space-between;
}

.value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.5rem;
}

.footer {
  font-size: 0.8rem;
  color: var(--text-secondary);
  display: flex;
  justify-content: space-between;
}

/* Skeleton Loading */
.skeleton {
  background: linear-gradient(90deg, #2a2a2a 25%, #333333 50%, #2a2a2a 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  height: 100px;
  border-radius: 8px;
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
</style>
