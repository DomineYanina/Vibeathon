from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel
import os
import json
import logging

# ---------------------------------------------------------------------------
# Configuración inicial
# ---------------------------------------------------------------------------
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Cliente Gemini
# ---------------------------------------------------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise EnvironmentError("GEMINI_API_KEY no encontrada en las variables de entorno.")

client = genai.Client(api_key=GEMINI_API_KEY)

MODEL_ID = "gemini-2.5-flash"

PROMPT_AUDIO = (
    "Toma este fragmento de audio. "
    "Devuélveme un JSON con dos claves: "
    "'original' (la transcripción en el idioma original) y "
    "'traduccion' (si es inglés, traduce al español; si es español, traduce al inglés)."
)

# ---------------------------------------------------------------------------
# Schema de respuesta estructurada
# ---------------------------------------------------------------------------
class TranscripcionRespuesta(BaseModel):
    original: str
    traduccion: str

# ---------------------------------------------------------------------------
# Función de procesamiento de audio
# ---------------------------------------------------------------------------
async def procesar_audio_gemini(audio_chunk: bytes) -> TranscripcionRespuesta:
    """
    Envía un fragmento de audio al modelo Gemini y devuelve la transcripción
    en el idioma original junto con su traducción al idioma contrario.

    Args:
        audio_chunk: Bytes de audio crudos (PCM / WAV / etc.).

    Returns:
        TranscripcionRespuesta con 'original' y 'traduccion'.
    """
    try:
        audio_part = types.Part.from_bytes(
            data=audio_chunk,
            mime_type="audio/wav",
        )

        response = await client.aio.models.generate_content(
            model=MODEL_ID,
            contents=[audio_part, PROMPT_AUDIO],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=TranscripcionRespuesta,
                temperature=0.2,
            ),
        )

        result = json.loads(response.text)
        logger.info("Transcripción completada: %s", result)
        return TranscripcionRespuesta(**result)

    except Exception as exc:
        logger.error("Error al procesar audio con Gemini: %s", exc)
        raise

# ---------------------------------------------------------------------------
# Aplicación FastAPI
# ---------------------------------------------------------------------------
app = FastAPI(title="Vibeathon API", version="1.0.0")


@app.get("/health")
async def health_check():
    return {"status": "ok"}


# ---------------------------------------------------------------------------
# Endpoint WebSocket: /ws/transcribe
# ---------------------------------------------------------------------------
@app.websocket("/ws/transcribe")
async def ws_transcribe(websocket: WebSocket):
    """
    WebSocket que recibe chunks de audio del cliente, los procesa con Gemini
    y devuelve la transcripción + traducción como JSON en tiempo real.

    Formatos de audio aceptados:
      - bytes crudos (PCM 16-bit / WAV)
      - array de enteros enviado como bytes
      - base64 enviado como texto (se decodifica automáticamente)
    """
    await websocket.accept()
    logger.info("Cliente WebSocket conectado: %s", websocket.client)

    try:
        while True:
            # --- Recepción: bytes directos o texto base64 ---
            try:
                message = await websocket.receive()
            except WebSocketDisconnect:
                raise  # lo captura el bloque exterior

            if "bytes" in message and message["bytes"] is not None:
                audio_chunk: bytes = message["bytes"]
            elif "text" in message and message["text"] is not None:
                # El cliente envió el audio codificado en base64
                import base64
                try:
                    audio_chunk = base64.b64decode(message["text"])
                except Exception:
                    await websocket.send_json({
                        "error": "Formato de texto inválido; se esperaba base64."
                    })
                    continue
            else:
                await websocket.send_json({"error": "Mensaje vacío o tipo no soportado."})
                continue

            # --- Procesamiento con Gemini ---
            try:
                resultado = await procesar_audio_gemini(audio_chunk)
                await websocket.send_json(resultado.model_dump())
            except Exception as exc:
                logger.error("Error Gemini en WebSocket: %s", exc)
                await websocket.send_json({
                    "error": f"Error al procesar el audio: {str(exc)}"
                })

    except WebSocketDisconnect:
        logger.info("Cliente WebSocket desconectado: %s", websocket.client)
    except Exception as exc:
        logger.error("Error inesperado en WebSocket: %s", exc)
        try:
            await websocket.close(code=1011)  # Internal Error
        except Exception:
            pass

