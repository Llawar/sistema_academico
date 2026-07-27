"""
Motor de recomendaciones basado en reglas.

Funciona como FALBACK del sistema de IA:
- Si Gemini está disponible → las recomendaciones las genera la IA
- Si Gemini falla → este módulo genera recomendaciones básicas con reglas

Cada sub-método analiza un aspecto diferente:
- Hábitos: sueño, distracciones, ejercicio, descanso
- Rendimiento: notas vs objetivos, materias en riesgo
- Registros: patrones de estudio, consistencia, duración
"""

from typing import Any, Dict, List


# ══════════════════════════════════════════════════════════
#  Constantes de umbrales
# ══════════════════════════════════════════════════════════
NOTA_EN_RIESGO = 5.0
NOTA_BUENA = 7.0
OBJETIVO_CERCA_TOLERANCIA = 0.5

DISTRACCION_ALTA_MINUTOS = 120
DISTRACCION_MEDIA_MINUTOS = 60
DESCANSO_BAJO_MINUTOS = 30
SUENO_BAJO_MINUTOS = 420       # 7 horas
EJERCICIO_BAJO_MINUTOS = 20

SESION_CORTA_MINUTOS = 30
SESION_BUENA_MINUTOS = 90
SESIONES_POCAS_POR_SEMANA = 2
HORAS_ESTUDIO_BAJA_SEMANAL = 3
MAX_RECOMENDACIONES = 10


class GeneradorRecomendaciones:
    """Genera recomendaciones académicas basadas en reglas."""

    # ─── Método principal ───

    # Genera una lista de recomendaciones analizando todos los datos del estudiante
    def generar_recomendaciones(
        self,
        materias: List,
        registros: List,
        habitos: List,
        evaluaciones: List,
        predicciones: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        recomendaciones = []

        recomendaciones.extend(self._analizar_habitos(habitos))
        recomendaciones.extend(self._analizar_rendimiento(
            evaluaciones, predicciones, materias,
        ))
        recomendaciones.extend(self._analizar_registros(registros, materias))

        return recomendaciones[:MAX_RECOMENDACIONES]

    # ─── Análisis de hábitos ───

    # Analiza los hábitos registrados y genera recomendaciones sobre sueño, distracciones, etc.
    def _analizar_habitos(self, habitos: List) -> List[Dict[str, Any]]:
        recomendaciones = []

        if not habitos:
            recomendaciones.append({
                "tipo": "habito",
                "titulo": "Registra tus hábitos",
                "descripcion": (
                    "Comienza a registrar tus hábitos diarios "
                    "(descansos, distracciones, sueño, ejercicio) "
                    "para obtener recomendaciones personalizadas."
                ),
                "prioridad": "alta",
                "materia_id": None,
            })
            return recomendaciones

        # Agrupar minutos totales por tipo de hábito
        habitos_dict = {}
        for h in habitos:
            tipo = h.tipo if hasattr(h, 'tipo') else str(h)
            duracion = h.duracion_minutos if hasattr(h, 'duracion_minutos') else 0
            habitos_dict[tipo] = habitos_dict.get(tipo, 0) + duracion

        # Evaluar distracciones
        distraccion = habitos_dict.get('distraccion', 0)
        if distraccion > DISTRACCION_ALTA_MINUTOS:
            horas = distraccion // 60
            recomendaciones.append({
                "tipo": "habito",
                "titulo": "Reduce las distracciones",
                "descripcion": (
                    f"Has registrado {horas} horas de distracciones. "
                    "Considera usar la técnica Pomodoro (25 min enfoque, 5 min descanso) "
                    "y deja el teléfono en otra habitación mientras estudias."
                ),
                "prioridad": "alta",
                "materia_id": None,
            })
        elif distraccion > DISTRACCION_MEDIA_MINUTOS:
            recomendaciones.append({
                "tipo": "habito",
                "titulo": "Cuidado con las distracciones",
                "descripcion": (
                    "Tienes un nivel moderado de distracciones. "
                    "Intenta identificar qué te distrae más y elimínalo "
                    "durante tus sesiones de estudio."
                ),
                "prioridad": "media",
                "materia_id": None,
            })

        # Evaluar descanso
        descanso = habitos_dict.get('descanso', 0)
        if descanso < DESCANSO_BAJO_MINUTOS:
            recomendaciones.append({
                "tipo": "habito",
                "titulo": "Toma más descansos",
                "descripcion": (
                    "No has descansado lo suficiente. Los estudios muestran "
                    "que los descansos regulares mejoran la retención "
                    "de información. Intenta descansar 5-10 min cada hora."
                ),
                "prioridad": "media",
                "materia_id": None,
            })

        # Evaluar sueño
        sueno = habitos_dict.get('sueno', 0)
        if sueno < SUENO_BAJO_MINUTOS:
            horas = sueno // 60 if sueno > 0 else 0
            recomendaciones.append({
                "tipo": "habito",
                "titulo": "Duerme más",
                "descripcion": (
                    f"Has dormido aproximadamente {horas} horas. "
                    "Se recomienda dormir entre 7 y 8 horas para un "
                    "óptimo rendimiento académico y consolidación de memoria."
                ),
                "prioridad": "alta",
                "materia_id": None,
            })

        # Evaluar ejercicio
        ejercicio = habitos_dict.get('ejercicio', 0)
        if ejercicio < EJERCICIO_BAJO_MINUTOS:
            recomendaciones.append({
                "tipo": "habito",
                "titulo": "Haz más ejercicio",
                "descripcion": (
                    "El ejercicio físico mejora la concentración y reduce "
                    "el estrés. Intenta al menos 30 minutos de actividad "
                    "física al día, aunque sea una caminata."
                ),
                "prioridad": "media",
                "materia_id": None,
            })

        return recomendaciones

    # ─── Análisis de rendimiento ───

    # Analiza las evaluaciones y predicciones para detectar materias en riesgo
    def _analizar_rendimiento(
        self,
        evaluaciones: List,
        predicciones: Dict[str, Any],
        materias: List,
    ) -> List[Dict[str, Any]]:
        recomendaciones = []

        if not evaluaciones:
            recomendaciones.append({
                "tipo": "rendimiento",
                "titulo": "Registra tus evaluaciones",
                "descripcion": (
                    "Registra tus notas de exámenes, tareas y proyectos "
                    "para que el sistema pueda analizar tu rendimiento "
                    "y generar predicciones."
                ),
                "prioridad": "alta",
                "materia_id": None,
            })
            return recomendaciones

        # Calcular nota promedio general
        nota_promedio = sum(e.nota for e in evaluaciones) / len(evaluaciones)

        # Comparar con el objetivo de las materias
        if materias:
            for materia in materias:
                evals_materia = [e for e in evaluaciones if e.materia_id == materia.id]
                if not evals_materia:
                    continue

                promedio_materia = sum(e.nota for e in evals_materia) / len(evals_materia)
                objetivo = materia.objetivo_nota if hasattr(materia, 'objetivo_nota') else 7.0

                if promedio_materia < NOTA_EN_RIESGO:
                    recomendaciones.append({
                        "tipo": "rendimiento",
                        "titulo": f"Riesgo en {materia.nombre}",
                        "descripcion": (
                            f"Tu promedio en {materia.nombre} es {promedio_materia:.1f}, "
                            f"por debajo del mínimo aprobatorio. "
                            f"Considera pedir ayuda al profesor o buscar tutoría."
                        ),
                        "prioridad": "alta",
                        "materia_id": materia.id,
                    })
                elif promedio_materia < objetivo - OBJETIVO_CERCA_TOLERANCIA:
                    recomendaciones.append({
                        "tipo": "rendimiento",
                        "titulo": f"Mejora en {materia.nombre}",
                        "descripcion": (
                            f"Tu promedio en {materia.nombre} es {promedio_materia:.1f}, "
                            f"pero tu objetivo es {objetivo:.1f}. "
                            f"Estás a {objetivo - promedio_materia:.1f} puntos de tu meta."
                        ),
                        "prioridad": "media",
                        "materia_id": materia.id,
                    })
                elif promedio_materia >= objetivo:
                    recomendaciones.append({
                        "tipo": "rendimiento",
                        "titulo": f"¡Bien en {materia.nombre}!",
                        "descripcion": (
                            f"Tu promedio en {materia.nombre} es {promedio_materia:.1f}, "
                            f"alcanzando tu objetivo de {objetivo:.1f}. ¡Sigue así!"
                        ),
                        "prioridad": "baja",
                        "materia_id": materia.id,
                    })

        # Usar predicciones del ML si están disponibles
        if predicciones and 'materias' in predicciones:
            for pred in predicciones['materias']:
                if pred.get('tendencia') == 'negativa':
                    nombre = pred.get('materia_nombre', 'una materia')
                    nota_pred = pred.get('prediccion_nota', 0)
                    recomendaciones.append({
                        "tipo": "rendimiento",
                        "titulo": f"Tendencia a la baja en {nombre}",
                        "descripcion": (
                            f"Tu rendimiento en {nombre} muestra tendencia negativa. "
                            f"Predicción actual: {nota_pred:.1f}. "
                            f"Intenta aumentar tu tiempo de estudio en esta materia."
                        ),
                        "prioridad": "alta",
                        "materia_id": pred.get('materia_id'),
                    })

        return recomendaciones

    # ─── Análisis de registros de estudio ───

    # Analiza los patrones de estudio: duración de sesiones, consistencia, frecuencia
    def _analizar_registros(
        self, registros: List, materias: List,
    ) -> List[Dict[str, Any]]:
        recomendaciones = []

        if not registros:
            recomendaciones.append({
                "tipo": "estudio",
                "titulo": "Registra tu tiempo de estudio",
                "descripcion": (
                    "Registra tus sesiones de estudio para que el sistema "
                    "analice tus patrones y te ayude a mejorar. "
                    "Puedes hacerlo escribiendo en el chat: "
                    "\"Estudié 2 horas de cálculo hoy\"."
                ),
                "prioridad": "media",
                "materia_id": None,
            })
            return recomendaciones

        # Calcular duración de cada sesión en minutos
        duraciones = []
        for r in registros:
            if r.hora_inicio and r.hora_fin:
                minutos = (r.hora_fin - r.hora_inicio).total_seconds() / 60
                if minutos > 0:
                    duraciones.append(minutos)

        if not duraciones:
            return recomendaciones

        promedio_sesion = sum(duraciones) / len(duraciones)
        total_horas = sum(duraciones) / 60

        # Detectar sesiones muy cortas
        sesiones_cortas = sum(1 for d in duraciones if d < SESION_CORTA_MINUTOS)
        if sesiones_cortas > len(duraciones) * 0.5:
            recomendaciones.append({
                "tipo": "estudio",
                "titulo": "Sesiones de estudio muy cortas",
                "descripcion": (
                    f"Tu sesión promedio es de {promedio_sesion:.0f} minutos. "
                    f"Para un aprendizaje efectivo, intenta estudiar en bloques "
                    f"de al menos {SESION_BUENA_MINUTOS} minutos sin interrupciones."
                ),
                "prioridad": "media",
                "materia_id": None,
            })

        # Detectar pocas sesiones
        if len(registros) < SESIONES_POCAS_POR_SEMANA:
            recomendaciones.append({
                "tipo": "estudio",
                "titulo": "Estudia con más frecuencia",
                "descripcion": (
                    f"Solo has registrado {len(registros)} sesión(es) de estudio. "
                    "Es mejor estudiar un poco cada día que mucho un solo día. "
                    "Intenta al menos 3-4 sesiones por semana."
                ),
                "prioridad": "alta",
                "materia_id": None,
            })

        # Detectar bajo tiempo total de estudio
        if total_horas < HORAS_ESTUDIO_BAJA_SEMANAL:
            recomendaciones.append({
                "tipo": "estudio",
                "titulo": "Aumenta tu tiempo de estudio",
                "descripcion": (
                    f"Has estudiado {total_horas:.1f} horas en total. "
                    "Se recomienda al menos 7 horas semanales "
                    "para un buen rendimiento académico."
                ),
                "prioridad": "alta",
                "materia_id": None,
            })

        # Detectar materias sin estudio
        if materias:
            materias_con_estudio = set()
            for r in registros:
                if hasattr(r, 'materia_id') and r.materia_id:
                    materias_con_estudio.add(r.materia_id)

            materias_sin_estudio = [
                m for m in materias if m.id not in materias_con_estudio
            ]

            if materias_sin_estudio and len(materias_sin_estudio) <= 3:
                nombres = ", ".join(m.nombre for m in materias_sin_estudio)
                recomendaciones.append({
                    "tipo": "estudio",
                    "titulo": "Materias sin tiempo de estudio",
                    "descripcion": (
                        f"No has registrado sesiones de estudio para: {nombres}. "
                        "Distribuye tu tiempo entre todas tus materias."
                    ),
                    "prioridad": "media",
                    "materia_id": None,
                })

        return recomendaciones


# Instancia singleton
generador = GeneradorRecomendaciones()