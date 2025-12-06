# Indicadores Económicos Chile - Dashboard

Aplicación web de monitoreo de indicadores económicos (UF, USD, EUR, UTM) en tiempo real, diseñada para alta eficiencia y usabilidad ejecutiva.

## Tecnologías

- **Backend**: Python 3 (FastAPI) - Alta velocidad y concurrencia.
- **Frontend**: Vue 3 + Vite - UI Reactiva y liviana.
- **Estilo**: CSS moderno (Variables, Flexbox/Grid) con diseño "Dark Mode" ejecutivo.

## Requisitos

- Python 3.8+
- Node.js 16+

## Instalación y Ejecución

### 1. Backend

Desde la raíz del proyecto:

```bash
# Crear entorno virtual (opcional pero recomendado)
python3 -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r backend/requirements.txt

# Ejecutar servidor (puerto 8000)
uvicorn backend.app.main:app --reload
```

### 2. Frontend

Desde la raíz del proyecto (en otra terminal):

```bash
cd frontend

# Instalar dependencias
npm install

# Iniciar servidor de desarrollo (puerto 5173 por defecto)
npm run dev
```

La aplicación estará disponible en `http://localhost:5173`.
El frontend redirige automáticamente las llamadas `/api` al backend en `http://localhost:8000`.

## Estructura del Proyecto

```
/backend
  /app
    main.py       # Punto de entrada API
    services.py   # Lógica de obtención de datos (Mindicador/SII)
    models.py     # Esquemas de datos
  requirements.txt

/frontend
  /src
    /components
      IndicatorCard.vue
      Calculator.vue
    App.vue
    style.css     # Estilos globales y tema visual
  vite.config.js  # Configuración Proxy
```
