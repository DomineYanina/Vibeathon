# ??? Nerdearla Live Subs - Vibeathon 2026

![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)

Solución *open source* de transcripción y traducción simultánea de audio en tiempo real, diseñada como MVP para el desafío Vibeathon de Nerdearla 2026.

Este proyecto captura audio en vivo desde el navegador, lo transmite vía WebSockets a un servidor ligero en Python, y utiliza el SDK de **Gemini 2.5 Flash** para devolver subtítulos (idioma original y traducción Inglés ? Español) con latencia mínima.

## ?? Características (MVP)

*   **Baja Latencia:** Uso de WebSockets bidireccionales en lugar de bases de datos para sincronizar el texto en pantalla.
*   **Procesamiento Inteligente:** Integración directa con el modelo Gemini Flash para transcripción y traducción simultánea en un solo paso.
*   **Fácil Despliegue:** Frontend estático en Vanilla JS (sin frameworks pesados) y backend en FastAPI.
*   **Soporte Multisesión (Local):** La arquitectura actual de WebSockets permite abrir múltiples pestañas del frontend para procesar al menos 2 sesiones de stream en simultáneo de forma local.

---

## ?? Requisitos Previos

Para correr este proyecto necesitas:

1.  **Python 3.9** o superior.
2.  Un navegador web moderno (Chrome, Firefox, Edge) con permisos de micrófono habilitados.
3.  Una API Key de **Google AI Studio**. Puedes obtener una gratis [aquí](https://aistudio.google.com/).

---

## ?? Instalación y Configuración

**1. Clonar el repositorio**
```bash
git clone https://github.com/TU_USUARIO/nerdearla-live-subs.git
cd nerdearla-live-subs
```

**2. Instalar dependencias**
Se recomienda utilizar un entorno virtual (venv):
```bash
pip install -r requirements.txt
```

**3. Variables de Entorno**
Crea un archivo llamado `.env` en la raíz del proyecto y agrega tu clave de Gemini:
```env
GEMINI_API_KEY=tu_api_key_de_google_ai_studio_aqui
```

---

## ????? Cómo levantar el proyecto

El proyecto consta de dos partes muy sencillas de ejecutar:

### 1. Iniciar el Backend (Servidor de WebSockets)
Abre tu terminal en la carpeta del proyecto y ejecuta:
```bash
uvicorn main:app --reload
```
El servidor quedará escuchando en `ws://localhost:8000/ws/transcribe`.

### 2. Iniciar el Frontend (Cliente / Audiencia)
Simplemente haz doble clic en el archivo `index.html` para abrirlo en tu navegador web. 
*   Haz clic en el botón **"Iniciar Transcripción"**.
*   Otorga los permisos de micrófono al navegador.
*   ¡Comienza a hablar (o reproduce una charla de Nerdearla cerca del micrófono) y verás los subtítulos en tiempo real!

---

## ?? Escalabilidad a Producción (10+ sesiones)

Aunque este MVP está diseñado para correr localmente y demostrar el concepto base (2+ sesiones), la arquitectura está pensada para escalar a nivel conferencia:
*   **Desacople:** El frontend estático puede alojarse en un CDN.
*   **Balanceo de Carga:** Se puede interponer NGINX para distribuir las conexiones WebSocket.
*   **Workers:** Integrando Redis Pub/Sub, múltiples workers de FastAPI pueden procesar cientos de streams de audio de diferentes escenarios (Escenario A, B, C) sin bloquear el hilo principal.

---

## ?? Licencia

Este proyecto está bajo la Licencia MIT - mira el archivo [LICENSE](LICENSE) para más detalles.