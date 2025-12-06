<script setup>
import { ref, watch, computed } from 'vue'

const props = defineProps({
  indicators: Object
})

const amount = ref(1)
const currencyFrom = ref('dolar')
const currencyTo = ref('clp')
const result = ref(0)

// Helper to get rate for a currency code
const getRate = (code) => {
  if (code === 'clp') return 1
  if (!props.indicators || !props.indicators[code]) return 0
  return props.indicators[code].valor
}

// Helper to get symbol/name
const getName = (code) => {
  if (code === 'clp') return 'Peso Chileno'
  if (!props.indicators || !props.indicators[code]) return code
  return props.indicators[code].nombre
}

const calculate = () => {
  const rateFrom = getRate(currencyFrom.value)
  const rateTo = getRate(currencyTo.value)

  if (!rateFrom || !rateTo) {
    result.value = 0
    return
  }
  
  // (Amount * RateFrom) / RateTo
  // Example: 100 USD -> UF
  // (100 * 950) / 37000 = 2.56 UF
  result.value = (amount.value * rateFrom) / rateTo
}

const swapCurrencies = () => {
  const temp = currencyFrom.value
  currencyFrom.value = currencyTo.value
  currencyTo.value = temp
}

watch([amount, currencyFrom, currencyTo, () => props.indicators], () => {
  calculate()
})

const copyToClipboard = async () => {
  try {
    const text = `${new Intl.NumberFormat('es-CL', { maximumFractionDigits: 4 }).format(result.value)} ${currencyTo.value.toUpperCase()}`
    await navigator.clipboard.writeText(text)
    // Optional: Show tooltip or toast? For now just a console log or simple visual feedback could happen
    const btn = document.querySelector('.copy-btn')
    if (btn) {
      const original = btn.innerHTML
      btn.innerHTML = '✓'
      setTimeout(() => btn.innerHTML = original, 2000)
    }
  } catch (err) {
    console.error('Failed to copy', err)
  }
}

defineExpose({ calculate })
</script>

<template>
  <div class="calculator">
    <h2>Conversor de Divisas</h2>
    
    <div class="converter-grid">
      <!-- Amount -->
      <div class="input-group full-width">
        <label>Cantidad</label>
        <input type="number" v-model="amount" min="0" step="any" placeholder="0.00">
      </div>

      <!-- From -->
      <div class="input-group">
        <label>De (Origen)</label>
        <select v-model="currencyFrom">
          <option value="clp">CLP (Peso Chileno)</option>
          <option value="uf">UF (Unidad de Fomento)</option>
          <option value="dolar">USD (Dólar Observado)</option>
          <option value="euro">EUR (Euro)</option>
          <option value="utm">UTM</option>
        </select>
      </div>

      <!-- Swap Button -->
      <div class="swap-container">
        <button class="swap-btn" @click="swapCurrencies" title="Invertir monedas">
          ⇄
        </button>
      </div>

      <!-- To -->
      <div class="input-group">
        <label>A (Destino)</label>
         <select v-model="currencyTo">
          <option value="clp">CLP (Peso Chileno)</option>
          <option value="uf">UF (Unidad de Fomento)</option>
          <option value="dolar">USD (Dólar Observado)</option>
          <option value="euro">EUR (Euro)</option>
          <option value="utm">UTM</option>
        </select>
      </div>
    </div>

    <!-- Result -->
    <div class="result-display">
      <div class="conversion-summary">
        {{ new Intl.NumberFormat('es-CL').format(amount) }} {{ currencyFrom.toUpperCase() }} =
      </div>
      <div class="result-row">
        <div class="val">
            {{ new Intl.NumberFormat('es-CL', { maximumFractionDigits: 4 }).format(result) }}
            <span class="currency-suffix">{{ currencyTo.toUpperCase() }}</span>
        </div>
        <button class="copy-btn" @click="copyToClipboard" title="Copiar resultado">
            📋
        </button>
      </div>
      
      <small class="rate-info">
        1 {{ currencyFrom.toUpperCase() }} = {{ new Intl.NumberFormat('es-CL', { maximumFractionDigits: 5 }).format(getRate(currencyFrom)/getRate(currencyTo)) }} {{ currencyTo.toUpperCase() }}
      </small>
    </div>
  </div>
</template>

<style scoped>
.calculator {
  background: var(--bg-secondary);
  border-radius: 16px; /* More rounded */
  padding: 2rem;
  box-shadow: var(--card-shadow);
  border: 1px solid rgba(148, 163, 184, 0.1);
}

h2 {
  margin-top: 0;
  margin-bottom: 2rem;
  font-size: 1.25rem;
  color: var(--text-primary);
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

h2::before {
    content: '';
    display: block;
    width: 4px;
    height: 1.25rem;
    background: var(--accent-color);
    border-radius: 2px;
}

.converter-grid {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  gap: 1.5rem;
  align-items: end; /* Align to bottom of inputs */
  margin-bottom: 2rem;
}

.full-width {
  grid-column: 1 / -1;
  margin-bottom: 0.5rem; /* Less margin since grid handles gap */
}

.input-group {
  display: flex;
  flex-direction: column;
}

.input-group label {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
  font-weight: 500;
}

input, select {
  background: var(--bg-primary); /* Darker input bg */
  border: 1px solid rgba(148, 163, 184, 0.2);
  color: var(--text-primary);
  padding: 0.8rem 1rem;
  border-radius: 10px;
  font-size: 0.95rem;
  outline: none;
  width: 100%;
  box-sizing: border-box;
  transition: all 0.2s ease;
  font-family: var(--font-family);
}

input:focus, select:focus {
  border-color: var(--accent-color);
  box-shadow: 0 0 0 2px rgba(45, 212, 191, 0.1); /* Glow effect */
}

.swap-container {
  display: flex;
  justify-content: center;
  padding-bottom: 5px;
}

.swap-btn {
  background: rgba(148, 163, 184, 0.1);
  border: none;
  color: var(--accent-color);
  font-size: 1.2rem;
  width: 42px;
  height: 42px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.swap-btn:hover {
  background: var(--accent-color);
  color: #fff;
  transform: rotate(180deg) scale(1.1);
}

.result-display {
  background: var(--bg-result);
  padding: 1.5rem;
  border-radius: 12px;
  border: 1px solid rgba(45, 212, 191, 0.2); /* Accent border */
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.result-display::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 4px;
    height: 100%;
    background: var(--accent-color);
}

.conversion-summary {
  color: var(--text-secondary);
  font-size: 0.85rem;
  margin-bottom: 0.5rem;
  font-family: monospace;
}

.result-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
    margin-bottom: 0.5rem;
}

.val {
  font-size: 2rem;
  font-weight: 700;
  color: var(--text-primary);
  line-height: 1.1;
  letter-spacing: -0.02em;
}

.currency-suffix {
  font-size: 1rem;
  color: var(--accent-color);
  font-weight: 500;
  margin-left: 0.5rem;
}

.copy-btn {
    background: rgba(255, 255, 255, 0.05);
    border: none;
    color: var(--text-secondary);
    width: 36px;
    height: 36px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 1rem;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
}

.copy-btn:hover {
    background: rgba(255, 255, 255, 0.1);
    color: var(--text-primary);
}

.rate-info {
  color: var(--text-secondary);
  font-family: monospace;
  font-size: 0.75rem;
  opacity: 0.8;
}

@media (max-width: 600px) {
  .converter-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .swap-container {
    padding: 0;
    margin: -0.5rem 0;
  }
  
  .swap-btn {
    transform: rotate(90deg);
    width: 36px;
    height: 36px;
  }
  .swap-btn:hover {
    transform: rotate(270deg);
  }
}
</style>
