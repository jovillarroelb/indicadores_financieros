<script setup>
import { ref, computed, watch } from 'vue'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js'
import { Line } from 'vue-chartjs'
import { format, subDays, startOfMonth, startOfYear, endOfMonth } from 'date-fns'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

const props = defineProps(['isOpen', 'defaultIndicator'])
const emit = defineEmits(['close'])

const selectedIndicator = ref('UF')
const startDate = ref(format(startOfYear(new Date()), 'yyyy-MM-dd'))
const endDate = ref(format(endOfMonth(new Date()), 'yyyy-MM-dd'))
const historyData = ref([])
const loading = ref(false)

const chartData = computed(() => {
  return {
    labels: historyData.value.map(item => {
      const d = new Date(item.fecha)
      return d.toLocaleDateString('es-CL', { day: '2-digit', month: 'short' })
    }),
    datasets: [
      {
        label: `${selectedIndicator.value}`,
        backgroundColor: (ctx) => {
          const canvas = ctx.chart.ctx;
          const gradient = canvas.createLinearGradient(0, 0, 0, 400);
          gradient.addColorStop(0, 'rgba(45, 212, 191, 0.5)'); // primary color low opacity
          gradient.addColorStop(1, 'rgba(45, 212, 191, 0.0)');
          return gradient;
        },
        borderColor: '#2DD4BF', // var(--accent-color)
        borderWidth: 2,
        pointBackgroundColor: '#2DD4BF',
        pointRadius: 3,
        pointHoverRadius: 5,
        fill: true,
        data: historyData.value.map(item => item.valor),
        tension: 0.3 // smooth curves
      }
    ]
  }
})

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { 
        display: false // minimalistic
    },
    tooltip: { 
        mode: 'index', 
        intersect: false,
        backgroundColor: '#1E293B',
        titleColor: '#F8FAFC',
        bodyColor: '#94A3B8',
        borderColor: 'rgba(148, 163, 184, 0.1)',
        borderWidth: 1,
        padding: 10,
        cornerRadius: 8
    }
  },
  scales: {
    x: { 
        display: true,
        grid: {
            display: false,
            drawBorder: false
        },
        ticks: {
            color: '#94A3B8',
            font: { size: 10 }
        }
    },
    y: { 
        display: true,
        grid: {
            color: 'rgba(148, 163, 184, 0.05)',
            drawBorder: false
        },
        ticks: {
            color: '#94A3B8',
            font: { size: 10 },
            callback: function(value) {
                return '$' + value.toLocaleString('es-CL')
            }
        }
    }
  },
  interaction: {
      mode: 'nearest',
      axis: 'x',
      intersect: false
  }
}

const fetchHistory = async () => {
  if (!startDate.value || !endDate.value) return
  loading.value = true
  try {
    const res = await fetch(`/api/history/${selectedIndicator.value}?start=${startDate.value}&end=${endDate.value}`)
    if (!res.ok) throw new Error("Failed to fetch")
    historyData.value = await res.json()
  } catch (e) {
    console.error(e)
    historyData.value = []
  } finally {
    loading.value = false
  }
}

watch([selectedIndicator, startDate, endDate], () => {
  if (props.isOpen) fetchHistory()
})

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    if (props.defaultIndicator) selectedIndicator.value = props.defaultIndicator.toUpperCase()
    fetchHistory()
  }
})
</script>

<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Histórico: {{ selectedIndicator }}</h2>
        <button class="close-btn" @click="$emit('close')">X</button>
      </div>
      
      <div class="filters">
        <select v-model="selectedIndicator">
          <option value="UF">UF</option>
          <option value="USD">Dólar</option>
          <option value="EUR">Euro</option>
          <option value="UTM">UTM</option>
        </select>
        
        <input type="date" v-model="startDate">
        <span class="to">a</span>
        <input type="date" v-model="endDate">
      </div>

      <div class="content-body">
        <div v-if="loading" class="loading">Cargando datos...</div>
        
        <div v-else class="data-container">
          <div class="chart-container">
            <Line :data="chartData" :options="chartOptions" />
          </div>
          
          <div class="table-container">
            <table>
              <thead>
                <tr>
                  <th>Fecha</th>
                  <th>Valor</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="row in historyData" :key="row.fecha">
                  <td>{{ new Date(row.fecha).toLocaleDateString('es-CL') }}</td>
                  <td>${{ row.valor.toLocaleString('es-CL') }}</td>
                </tr>
                <tr v-if="historyData.length === 0">
                  <td colspan="2">No data found</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.8);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  background: var(--bg-secondary);
  width: 90%;
  max-width: 1000px;
  max-height: 90vh;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  color: var(--text-primary);
  box-shadow: 0 10px 25px rgba(0,0,0,0.5);
}

.modal-header {
  padding: 1.5rem;
  border-bottom: 1px solid rgba(255,255,255,0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filters {
  padding: 1rem 1.5rem;
  display: flex;
  gap: 1rem;
  align-items: center;
  background: rgba(0,0,0,0.2);
  flex-wrap: wrap;
}

.content-body {
  flex: 1;
  overflow: hidden;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
}

.data-container {
  display: flex;
  gap: 2rem;
  height: 100%;
  overflow: hidden;
}

.chart-container {
  flex: 2;
  min-height: 300px;
}

.table-container {
  flex: 1;
  overflow-y: auto;
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th, td {
  padding: 0.8rem;
  text-align: left;
  border-bottom: 1px solid rgba(255,255,255,0.1);
}

th {
  background: rgba(255,255,255,0.05); /* sticky not working well in flex without more css, keeping simple */
  position: sticky; 
  top: 0;
  background: var(--bg-secondary);
}

.close-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 1.5rem;
  cursor: pointer;
}

input, select {
  padding: 0.5rem;
  border-radius: 4px;
  border: 1px solid rgba(255,255,255,0.2);
  background: var(--bg-primary);
  color: var(--text-primary);
}

@media (max-width: 768px) {
  .data-container {
    flex-direction: column;
    overflow-y: auto;
  }
  .chart-container {
    height: 300px;
    flex: none;
  }
}
</style>
