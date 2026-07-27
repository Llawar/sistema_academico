"""
Servicio de inteligencia artificial para extraer datos
del texto libre del estudiante usando Google Gemini.
"""

import json
import logging
import google.generativeai as genai

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from ..core.database import settings
from ..models.models import DatoHabitual, Materia, RegistroDiario

logger = logging.getLogger(__name__)

# Configurar Gemini con la API key
genai.configure(api_key=settings.GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-3-flash-preview")


# ══════════════════════════════════════════════════════════
#  Constantes
# ══════════════════════════════════════════════════════════
TIPOS_HABITO_VALIDOS = ["descanso", "distraccion", "ejercicio", "sueno", "otro"]
TIPOS_ACTIVIDAD_VALIDOS = ["estudio", "practica", "repaso"]

# ── Construcción del prompt ─────────────────────────────

# Construye el prompt que se envía a Gemini con el contexto del usuario
def construir_prompt(texto_usuario: str, materias: List[Materia]) -> str:
    lista_materias = "\n".join(
        f"  - id={m.id}: {m.nombre}" for m in materias
    ) if materias else "  (el usuario no tiene materias registradas)"

    prompt = f"""Eres un asistente académico. Tu tarea es extraer datos estructurados del texto de un estudiante.

MATERIAS DEL ESTUDIANTE:
{lista_materias}

TEXTO DEL ESTUDIANTE:
"{texto_usuario}"

INSTRUCCIONES:
1. Extrae los hábitos mencionados (sueño, distracciones, ejercicio, descanso, u otros)
2. Extrae las sesiones de estudio mencionadas (materia, hora de inicio, hora de fin)
3. Si el estudiante menciona una materia, busca el mejor match de la lista de materias
4. Si no puedes determinar una hora exacta de estudio, usa null
5. Clasifica cada hábito en: descanso, distraccion, ejercicio, sueno, u otro
6. Para el campo "tipo_actividad" usa: estudio, practica, o repaso
7. Genera una respuesta breve, motivadora y personalizada

RESPONDE SOLO CON UN JSON válido (sin markdown, sin ```json) con esta estructura exacta:
{{
    "habitos": [
        {{
            "tipo": "descanso|distraccion|ejercicio|sueno|otro",
            "duracion_minutos": 30,
            "notas": "descripción breve opcional"
        }}
    ],
    "registros": [
        {{
            "materia_id": 1,
            "hora_inicio": "15:00",
            "hora_fin": "17:00",
            "tipo_actividad": "estudio|practica|repaso",
            "descripcion": "descripción breve opcional"
        }}
    ],
    "respuesta": "Respuesta motivadora y personalizada para el estudiante. Máximo 3 oraciones."
}}

Si el estudiante no menciona hábitos, devuelve una lista vacía "habitos": []
Si el estudiante no menciona estudio, devuelve una lista vacía "registros": []
Siempre genera una "respuesta" aunque no haya datos que extraer."""

    return prompt


# ── Llamada a Gemini ────────────────────────────────────

# Envía el prompt a Google Gemini y retorna la respuesta en texto
def llamar_gemini(prompt: str) -> str:
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Error al llamar a Gemini: {e}")
        raise


# ── Parseo de la respuesta ──────────────────────────────

# Convierte el texto JSON de Gemini en un diccionario estructurado
def parsear_respuesta(respuesta_texto: str) -> Dict[str, Any]:
    try:
        # Limpiar posibles marcadores de markdown
        texto_limpio = respuesta_texto.strip()
        if texto_limpio.startswith("```"):
            texto_limpio = texto_limpio.split("\n", 1)[1]
        if texto_limpio.endswith("```"):
            texto_limpio = texto_limpio.rsplit("```", 1)[0]
        texto_limpio = texto_limpio.strip()

        datos = json.loads(texto_limpio)

        # Validar estructura mínima
        if "habitos" not in datos:
            datos["habitos"] = []
        if "registros" not in datos:
            datos["registros"] = []
        if "respuesta" not in datos:
            datos["respuesta"] = "Datos registrados correctamente."

        return datos

    except json.JSONDecodeError as e:
        logger.error(f"Error al parsear respuesta de Gemini: {e}")
        logger.error(f"Texto recibido: {respuesta_texto}")
        return {
            "habitos": [],
            "registros": [],
            "respuesta": "No pude procesar tu mensaje. Intenta ser más específico con los tiempos y materias.",
        }


# ── Guardado en base de datos ───────────────────────────

# Guarda los hábitos extraídos en la tabla datos_habitos
def _guardar_habitos(db: Session, usuario_id: int, habitos: List[Dict]) -> int:
    guardados = 0
    for habito in habitos:
        tipo = habito.get("tipo", "otro").lower()
        if tipo not in TIPOS_HABITO_VALIDOS:
            tipo = "otro"

        duracion = habito.get("duracion_minutos", 0)
        if not isinstance(duracion, (int, float)) or duracion <= 0:
            continue

        db_habito = DatoHabitual(
            usuario_id=usuario_id,
            tipo=tipo,
            duracion_minutos=int(duracion),
            notas=habito.get("notas"),
            fecha=datetime.utcnow(),
        )
        db.add(db_habito)
        guardados += 1

    return guardados


# Guarda los registros de estudio extraídos en la tabla registros_diarios
def _guardar_registros(
    db: Session, usuario_id: int, registros: List[Dict],
    materias_usuario: List[Materia]
) -> int:
    hoy = datetime.utcnow().date()
    guardados = 0

    ids_materias_validas = {m.id for m in materias_usuario}

    for registro in registros:
        materia_id = registro.get("materia_id")
        if materia_id and materia_id not in ids_materias_validas:
            materia_id = None

        hora_inicio_str = registro.get("hora_inicio")
        hora_fin_str = registro.get("hora_fin")

        if not hora_inicio_str or not hora_fin_str:
            continue

        try:
            h_inicio = datetime.strptime(str(hora_inicio_str), "%H:%M")
            h_fin = datetime.strptime(str(hora_fin_str), "%H:%M")
        except ValueError:
            try:
                h_inicio = datetime.strptime(str(hora_inicio_str), "%H:%M:%S")
                h_fin = datetime.strptime(str(hora_fin_str), "%H:%M:%S")
            except ValueError:
                logger.warning(f"No se pudo parsear hora: {hora_inicio_str} - {hora_fin_str}")
                continue

        hora_inicio = datetime.combine(hoy, h_inicio.time())
        hora_fin = datetime.combine(hoy, h_fin.time())

        if hora_fin <= hora_inicio:
            hora_fin += timedelta(days=1)

        tipo_act = registro.get("tipo_actividad", "estudio").lower()
        if tipo_act not in TIPOS_ACTIVIDAD_VALIDOS:
            tipo_act = "estudio"

        db_registro = RegistroDiario(
            usuario_id=usuario_id,
            materia_id=materia_id,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            tipo_actividad=tipo_act,
            descripcion=registro.get("descripcion"),
            fecha=datetime.utcnow(),
        )
        db.add(db_registro)
        guardados += 1

    return guardados


# ── Función principal ───────────────────────────────────

# Función principal que orquesta todo el flujo: texto → IA → BD → respuesta
def procesar_registro_usuario(
    db: Session,
    usuario_id: int,
    texto: str,
    materias: List[Materia],
) -> Dict[str, Any]:
    # Construir y enviar el prompt
    prompt = construir_prompt(texto, materias)
    respuesta_texto = llamar_gemini(prompt)
    datos = parsear_respuesta(respuesta_texto)

    # Guardar en base de datos
    habitos_guardados = _guardar_habitos(db, usuario_id, datos["habitos"])
    registros_guardados = _guardar_registros(
        db, usuario_id, datos["registros"], materias
    )

    if habitos_guardados > 0 or registros_guardados > 0:
        db.commit()

    logger.info(
        f"Usuario {usuario_id}: {habitos_guardados} hábitos, "
        f"{registros_guardados} registros guardados"
    )

    return {
        "respuesta": datos["respuesta"],
        "habitos_extraidos": datos["habitos"],
        "registros_extraidos": datos["registros"],
        "habitos_guardados": habitos_guardados,
        "registros_guardados": registros_guardados,
    }