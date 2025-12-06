# 🚀 Despliegue en Vercel

Este proyecto está configurado para desplegarse fácilmente en **Vercel** usando una arquitectura Monorepo (Frontend Vite + Backend Python Serverless).

## Pasos para desplegar

1.  **Sube tu código a GitHub**
    - Asegúrate de haber hecho commit de todos los cambios:
      ```bash
      git add .
      git commit -m "Preparado para deploy"
      git push
      ```

2.  **Importa el proyecto en Vercel**
    - Ve a [vercel.com/new](https://vercel.com/new).
    - Selecciona tu repositorio de GitHub `indicadores_financieros`.
    - Haz clic en **Import**.

3.  **Configuración del Proyecto**
    - **Framework Preset**: Vercel debería detectar `Vite` o `Other`. Selecciona **Vite**.
    - **Root Directory**: `.` (Déjalo en la raíz, NO selecciones frontend).
    - **Build Command**: Vercel usará la configuración de `vercel.json`, pero si te pregunta:
        - Frontend Build: `cd frontend && npm install && npm run build`
        - Output Directory: `frontend/dist`
    - **Variables de Entorno**: No requeridas por ahora.

4.  **Deploy**
    - Haz clic en **Deploy**.
    - Vercel detectará el archivo `vercel.json` y construirá automáticamente:
        - El Frontend como archivos estáticos.
        - El Backend como Serverless Functions (`/api`).

## Verificación

Una vez desplegado, visita tu URL (ej: `https://indicadores-financieros.vercel.app`).
- El Dashboard debería cargar.
- La API debería responder en `/api/indicators`.

## Solución de Problemas

- **Si la API da 404**: Verifica que `vercel.json` esté en la raíz.
- **Si hay error de Python**: Verifica los logs de Vercel (Functions tab) y asegura que `requirements.txt` tenga todas las dependencias.
