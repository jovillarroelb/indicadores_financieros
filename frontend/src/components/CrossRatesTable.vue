<script setup>
import { computed } from 'vue'

const props = defineProps({
  indicators: Object,
  loading: Boolean
})

const currencies = ['clp', 'uf', 'dolar', 'euro', 'utm']

const getName = (code) => {
    switch(code) {
        case 'clp': return 'CLP'
        case 'uf': return 'UF'
        case 'dolar': return 'USD'
        case 'euro': return 'EUR'
        case 'utm': return 'UTM'
    }
}

const getRate = (code) => {
  if (code === 'clp') return 1
  if (!props.indicators || !props.indicators[code]) return 0
  return props.indicators[code].valor
}

// Matrix of values
const matrix = computed(() => {
    if (props.loading || !props.indicators) return []
    
    // We want to show how much 1 ROW_CURRENCY is in COL_CURRENCY
    // e.g. Row USD, Col CLP = 950
    return currencies.map(from => {
        return {
            code: from,
            name: getName(from),
            rates: currencies.map(to => {
                const rateFrom = getRate(from)
                const rateTo = getRate(to)
                if (!rateFrom || !rateTo) return 0
                return (rateFrom / rateTo)
            })
        }
    })
})
</script>

<template>
  <div class="cross-rates-card">
    <h3>Tasas Cruzadas</h3>
    <div class="table-container">
        <table>
            <thead>
                <tr>
                    <th>1 ...</th>
                    <th v-for="c in currencies" :key="c">{{ getName(c) }}</th>
                </tr>
            </thead>
            <tbody>
                <tr v-if="loading">
                    <td :colspan="currencies.length + 1" class="loading-cell">Cargando...</td>
                </tr>
                <tr v-else v-for="(row, rIndex) in matrix" :key="row.code">
                    <td class="row-header">1 {{ row.name }}</td>
                    <td v-for="(val, cIndex) in row.rates" :key="cIndex" :class="{'diagonal': rIndex === cIndex}">
                        <span v-if="rIndex === cIndex">-</span>
                        <span v-else>
                            {{ new Intl.NumberFormat('es-CL', { maximumFractionDigits: rIndex === 0 ? 5 : 2 }).format(val) }}
                        </span>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
  </div>
</template>

<style scoped>
.cross-rates-card {
  background: var(--bg-secondary);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: var(--card-shadow);
  border: 1px solid rgba(148, 163, 184, 0.1);
  overflow: hidden;
}

h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  font-size: 1.25rem;
  color: var(--text-primary);
  font-weight: 600;
  border-bottom: 1px solid rgba(148, 163, 184, 0.1);
  padding-bottom: 0.5rem;
}

.table-container {
    overflow-x: auto;
}

table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9rem;
    color: var(--text-primary);
}

th, td {
    padding: 0.75rem 0.5rem;
    text-align: right;
    border-bottom: 1px solid rgba(148, 163, 184, 0.05);
}

th {
    text-align: right;
    color: var(--text-secondary);
    font-weight: 500;
    font-size: 0.8rem;
}

th:first-child {
    text-align: left;
}

.row-header {
    text-align: left;
    font-weight: 600;
    color: var(--accent-color);
}

.diagonal {
    color: var(--text-secondary);
    opacity: 0.3;
}

.loading-cell {
    text-align: center;
    padding: 2rem;
    color: var(--text-secondary);
}

tbody tr:last-child td {
    border-bottom: none;
}

tbody tr:hover {
    background: rgba(255, 255, 255, 0.02);
}
</style>
