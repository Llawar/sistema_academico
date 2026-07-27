"""
Módulo de predicción de rendimiento académico.

Contiene la lógica de Machine Learning para:
- Preparar features a partir de evaluaciones, registros y hábitos
- Entrenar y persistir un modelo GradientBoostingRegressor
- Predecir notas por materia y rendimiento general
- Analizar tendencias y factores que afectan el rendimiento
"""

import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

logger = logging.getLogger(__name__)


#  Rutas de archivos del modelo

MODEL_PATH = Path(__file__).parent / "Master_ML.joblib"
SCALER_PATH = Path(__file__).parent / "Master_ML_scaler.joblib"


#  Constantes de configuración

ESCALA_NOTA_MIN = 1.0
ESCALA_NOTA_MAX = 10.0
PESO_HISTORICO = 0.3
PESO_ML = 0.7
UMBRAL_PENDIENTE = 0.1
CONFIANZA_BASE_ML = 0.75
CONFIANZA_SIN_DATOS = 0.2
CONFIANZA_DATOS_LIMITADOS = 0.35
MIN_MUESTRAS_ENTRENAMIENTO = 5
MAE_REFERENCIA = 3.0
CONFIANZA_MIN = 0.3
CONFIANZA_MAX = 0.95
UMBRAL_ALERTA_NOTA = 5.0
REENTRENAMIENTO_CADA_N = 5
DEFAULT_NOTA_PREDICHA = 5.0
TIPOS_HABITO = ['descanso', 'distraccion', 'ejercicio', 'sueno']
COLUMNAS_EXCLUIR_FEATURES = ['nota', 'tipo', 'materia_id', 'fecha']


class PredictorAcademico:
    """Motor de predicción académica basado en GradientBoostingRegressor."""

    # ─── Inicialización ───
    def __init__(self):
        """Inicializa el predictor y carga el modelo persistido si existe."""
        self.modelo = None
        self.scaler = None
        self.entrenado = False
        self.version = "1.0"
        self._lock = threading.Lock()
        self.cargar_modelo()

    # ─── Persistencia del modelo ───

    # Carga el modelo y el scaler desde los archivos .joblib
    def cargar_modelo(self) -> bool:
        if MODEL_PATH.exists() and SCALER_PATH.exists():
            try:
                self.modelo = joblib.load(MODEL_PATH)
                self.scaler = joblib.load(SCALER_PATH)
                self.entrenado = True
                logger.info(f"Modelo ML cargado desde {MODEL_PATH}")
                return True
            except Exception as e:
                logger.error(f"Error al cargar modelo: {e}")
                self.entrenado = False
                return False
        return False

    # Guarda el modelo y el scaler en archivos .joblib (thread-safe)
    def guardar_modelo(self, modelo, scaler) -> bool:
        with self._lock:
            try:
                joblib.dump(modelo, MODEL_PATH)
                joblib.dump(scaler, SCALER_PATH)
                self.modelo = modelo
                self.scaler = scaler
                self.entrenado = True
                logger.info(f"Modelo ML guardado en {MODEL_PATH}")
                return True
            except Exception as e:
                logger.error(f"Error al guardar modelo: {e}")
                return False

    # Entrena un modelo con los datos proporcionados y lo guarda
    def entrenar_y_guardar(self, X: np.ndarray, y: np.ndarray):
        modelo, scaler, prediccion, confianza = self._entrenar_modelo(X, y)
        self.guardar_modelo(modelo, scaler)
        return modelo, scaler, prediccion, confianza

    # Verifica si el modelo necesita reentrenarse según la cantidad de evaluaciones
    def necesita_reentrenamiento(self, n_evaluaciones: int) -> bool:
        return not self.entrenado or n_evaluaciones >= REENTRENAMIENTO_CADA_N

    # ─── Preparación de datos ───

    # Construye el DataFrame combinando evaluaciones, registros de estudio y hábitos
    def preparar_datos(self, registros: List, habitos: List, evaluaciones: List) -> pd.DataFrame:
        if not registros and not evaluaciones:
            return pd.DataFrame()

        datos = []
        for ev in evaluaciones:
            fecha = ev.fecha if hasattr(ev, 'fecha') else datetime.utcnow()

            # Buscar registros de estudio asociados a la materia de la evaluación
            registros_materia = [r for r in registros if r.materia_id == ev.materia_id] if registros else []
            total_minutos_estudio = sum(r.duracion_minutos for r in registros_materia)
            n_sesiones = len(registros_materia)

            datos.append({
                'fecha': fecha,
                'materia_id': ev.materia_id,
                'nota': ev.nota,
                'ponderacion': ev.ponderacion,
                'tipo': ev.tipo,
                'minutos_estudio_materia': total_minutos_estudio,
                'n_sesiones_estudio': n_sesiones,
            })

        df = pd.DataFrame(datos)
        if df.empty:
            return df

        # Extraer componentes temporales
        df['fecha'] = pd.to_datetime(df['fecha'])
        df['semana'] = df['fecha'].dt.isocalendar().week
        df['mes'] = df['fecha'].dt.month
        df['dia_semana'] = df['fecha'].dt.dayofweek

        # Agregar features derivados de hábitos
        df = self._agregar_features_habitos(df, habitos)

        return df

    # Agrega features semanales derivados de los hábitos de estudio
    def _agregar_features_habitos(self, df: pd.DataFrame, habitos: List) -> pd.DataFrame:
        # Inicializar todas las columnas con valores por defecto
        defaults = {f'habito_{tipo}_semanal': 0 for tipo in TIPOS_HABITO}
        defaults.update({
            'ratio_estudio_distraccion': 1.0,
            'habito_calidad_promedio': 0.5,
        })
        for col, val in defaults.items():
            df[col] = val

        if not habitos:
            return df

        # Convertir hábitos a DataFrame
        habitos_df = pd.DataFrame([{
            'fecha': h.fecha if hasattr(h, 'fecha') else datetime.utcnow(),
            'tipo': h.tipo,
            'duracion_minutos': h.duracion_minutos,
        } for h in habitos])

        if habitos_df.empty:
            return df

        habitos_df['fecha'] = pd.to_datetime(habitos_df['fecha'])
        habitos_df['semana'] = habitos_df['fecha'].dt.isocalendar().week

        # Agrupar minutos de hábito por semana y tipo
        habitos_por_semana = (
            habitos_df
            .groupby(['semana', 'tipo'])['duracion_minutos']
            .sum()
            .unstack(fill_value=0)
        )

        # Mapear cada tipo de hábito al DataFrame (vectorizado, sin apply)
        for tipo in TIPOS_HABITO:
            col_name = f'habito_{tipo}_semanal'
            if tipo in habitos_por_semana.columns:
                df[col_name] = df['semana'].map(habitos_por_semana[tipo]).fillna(0)

        # Ratio descanso vs distracción
        df['ratio_estudio_distraccion'] = (
            df['habito_descanso_semanal'] / (df['habito_distraccion_semanal'] + 1)
        )

        # Calidad promedio basada en la proporción de tiempo en distracciones
        total_habitos = habitos_df['duracion_minutos'].sum()
        if total_habitos > 0:
            distraccion_ratio = (
                habitos_df[habitos_df['tipo'] == 'distraccion']['duracion_minutos'].sum()
                / total_habitos
            )
            df['habito_calidad_promedio'] = 1 - distraccion_ratio
        else:
            df['habito_calidad_promedio'] = 0.5

        df['habito_calidad_promedio'] = df['habito_calidad_promedio'].fillna(0.5)

        return df

    # ─── Utilidades de features ───

    # Extrae la matriz de features numéricas eliminando columnas no predictoras
    def _extraer_features(self, df: pd.DataFrame) -> np.ndarray:
        columnas_validas = [c for c in COLUMNAS_EXCLUIR_FEATURES if c in df.columns]
        df_features = df.drop(columns=columnas_validas)
        return df_features.values

    # ─── Análisis de tendencias ───

    # Calcula la tendencia de rendimiento usando regresión lineal sobre las notas
    def calcular_tendencias(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df.empty or len(df) < 2:
            return {"tendencia": "insuficiente", "cambio": 0, "confianza": 0}

        notas = df.sort_values('fecha')['nota'].values
        x = np.arange(len(notas))
        pendiente = np.polyfit(x, notas, 1)[0]

        cambio_porcentual = (
            (notas[-1] - notas[0]) / notas[0] * 100 if notas[0] > 0 else 0
        )

        if pendiente > UMBRAL_PENDIENTE:
            tendencia = "positiva"
            confianza = min(0.9, 0.5 + abs(pendiente) * 2)
        elif pendiente < -UMBRAL_PENDIENTE:
            tendencia = "negativa"
            confianza = min(0.9, 0.5 + abs(pendiente) * 2)
        else:
            tendencia = "estable"
            confianza = 0.5

        return {
            "tendencia": tendencia,
            "cambio": round(cambio_porcentual, 2),
            "confianza": round(confianza, 2),
        }

    # ─── Predicción por materia ───

    # Genera una respuesta estándar cuando no hay datos suficientes
    def _prediccion_sin_datos(self, materia_id: int, mensaje: str) -> Dict[str, Any]:
        return {
            "materia_id": materia_id,
            "prediccion_nota": DEFAULT_NOTA_PREDICHA,
            "confianza": CONFIANZA_SIN_DATOS,
            "tendencia": "sin_datos",
            "factores": [mensaje],
        }

    # Predice la nota esperada para una materia específica usando el modelo ML
    def predecir_nota(self, materia_id: int, df: pd.DataFrame) -> Dict[str, Any]:
        if df.empty:
            return self._prediccion_sin_datos(
                materia_id,
                "Registra más evaluaciones para obtener predicciones precisas",
            )

        df_materia = df[df['materia_id'] == materia_id]
        if df_materia.empty:
            return self._prediccion_sin_datos(
                materia_id,
                "No hay evaluaciones registradas para esta materia",
            )

        tendencias = self.calcular_tendencias(df_materia)
        factores = self._analizar_factores(df_materia)

        # Intentar predicción con modelo ML si hay datos suficientes
        if (self.entrenado and self.modelo is not None
                and self.scaler is not None
                and len(df) >= MIN_MUESTRAS_ENTRENAMIENTO):
            try:
                X = self._extraer_features(df_materia)
                X_scaled = self.scaler.transform(X)
                prediccion_ml = self.modelo.predict(X_scaled).mean()
                nota_base = df_materia['nota'].mean()

                prediccion = nota_base * PESO_HISTORICO + prediccion_ml * PESO_ML
                prediccion = max(ESCALA_NOTA_MIN, min(ESCALA_NOTA_MAX, prediccion))
                confianza = CONFIANZA_BASE_ML

                logger.info(f"Predicción ML para materia {materia_id}: {prediccion:.2f}")
            except Exception as e:
                logger.warning(f"Error en predicción ML para materia {materia_id}: {e}")
                prediccion = df_materia['nota'].mean()
                confianza = CONFIANZA_DATOS_LIMITADOS
        else:
            # Fallback: usar el promedio histórico de la materia
            prediccion = df_materia['nota'].mean()
            confianza = CONFIANZA_DATOS_LIMITADOS

        return {
            "materia_id": materia_id,
            "prediccion_nota": round(prediccion, 2),
            "confianza": round(confianza, 2),
            "tendencia": tendencias["tendencia"],
            "factores": factores,
        }

    # ─── Entrenamiento del modelo ───

    # Entrena un GradientBoostingRegressor y calcula métricas de calidad
    def _entrenar_modelo(self, X: np.ndarray, y: np.ndarray) -> Tuple:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42,
        )

        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        modelo = GradientBoostingRegressor(
            n_estimators=50,
            max_depth=3,
            learning_rate=0.1,
            random_state=42,
        )
        modelo.fit(X_train_scaled, y_train)

        # Evaluar calidad del modelo con el set de prueba
        y_pred = modelo.predict(X_test_scaled)
        mae = mean_absolute_error(y_test, y_pred)

        # Predicción representativa basada en el promedio del test set
        nota_base = y.mean()
        ajuste = modelo.predict(X_test_scaled).mean() if len(X_test) > 0 else nota_base

        prediccion = nota_base * PESO_HISTORICO + ajuste * PESO_ML
        prediccion = max(ESCALA_NOTA_MIN, min(ESCALA_NOTA_MAX, prediccion))

        confianza = min(CONFIANZA_MAX, max(CONFIANZA_MIN, 1 - mae / MAE_REFERENCIA))

        return modelo, scaler, prediccion, confianza

    # ─── Análisis de factores ───

    # Analiza factores que influyen en el rendimiento y devuelve recomendaciones
    def _analizar_factores(self, df: pd.DataFrame) -> List[str]:
        factores = []

        if len(df) < 3:
            return ["Registra más datos para análisis detallado"]

        nota_promedio = df['nota'].mean()

        if nota_promedio >= 7.0:
            factores.append("Mantén tu buen ritmo de estudio")
        elif nota_promedio >= 5.0:
            factores.append("Necesitas mejorar tu consistencia")
        else:
            factores.append("Considera pedir ayuda adicional")

        tendencias = self.calcular_tendencias(df)
        if tendencias["tendencia"] == "positiva":
            factores.append("Tu rendimiento está mejorando")
        elif tendencias["tendencia"] == "negativa":
            factores.append("Tu rendimiento está bajando, revisa tu método")

        if 'habito_distraccion_semanal' in df.columns:
            distraccion_promedio = df['habito_distraccion_semanal'].mean()
            if distraccion_promedio > 60:
                factores.append("ALERTA: Alto nivel de distracciones (>1h/semana)")
            elif distraccion_promedio > 30:
                factores.append("Reduce las distracciones para mejorar tu rendimiento")

        if 'habito_calidad_promedio' in df.columns:
            calidad = df['habito_calidad_promedio'].mean()
            if calidad < 0.3:
                factores.append("Tu calidad de hábitos es baja, afecta tu estudio")
            elif calidad > 0.7:
                factores.append("Buenos hábitos de estudio detectados")

        return factores

    # ─── Predicciones generales ───

    # Lógica compartida que genera predicciones para una lista de materias
    def _ejecutar_predicciones(self, materias: List, df: pd.DataFrame) -> Dict[str, Any]:
        predicciones_materias = []
        for materia in materias:
            pred = self.predecir_nota(materia.id, df)
            pred['materia_nombre'] = materia.nombre
            predicciones_materias.append(pred)

        notas_predichas = [p['prediccion_nota'] for p in predicciones_materias]
        promedio = (
            sum(notas_predichas) / len(notas_predichas)
            if notas_predichas else DEFAULT_NOTA_PREDICHA
        )

        confianza_prom = (
            sum(p['confianza'] for p in predicciones_materias) / len(predicciones_materias)
            if predicciones_materias else CONFIANZA_SIN_DATOS
        )

        # Generar alertas para materias en riesgo
        alertas = []
        for p in predicciones_materias:
            if p['prediccion_nota'] < UMBRAL_ALERTA_NOTA:
                alertas.append(
                    f"Riesgo en {p['materia_nombre']}: predicción bajo {UMBRAL_ALERTA_NOTA}"
                )
            elif p['tendencia'] == "negativa":
                alertas.append(f"Baja tendencia en {p['materia_nombre']}")

        return {
            "promedio_predicho": round(promedio, 2),
            "confianza": round(confianza_prom, 2),
            "materias": predicciones_materias,
            "alertas": alertas,
        }

    # Genera predicciones del rendimiento general combinando todas las materias
    def predecir_rendimiento_general(
        self,
        materias: List,
        registros: List,
        habitos: List,
        evaluaciones: List,
    ) -> Dict[str, Any]:
        df = self.preparar_datos(registros, habitos, evaluaciones)

        if df.empty:
            return {
                "promedio_predicho": DEFAULT_NOTA_PREDICHA,
                "estado": "sin_datos",
                "confianza": CONFIANZA_SIN_DATOS,
                "alertas": ["Registra tus hábitos y evaluaciones para obtener predicciones"],
            }

        return self._ejecutar_predicciones(materias, df)

    # Entrena el modelo global con datos agregados de todos los usuarios
    def entrenar_modelo_global(
        self,
        todas_evaluaciones: List,
        todos_habitos: List,
        todos_registros: List,
    ) -> Dict[str, Any]:
        df = self.preparar_datos(todos_registros, todos_habitos, todas_evaluaciones)

        if df.empty or len(df) < MIN_MUESTRAS_ENTRENAMIENTO:
            return {
                "exitoso": False,
                "mensaje": "No hay suficientes datos globales para entrenar",
                "muestras": len(df) if not df.empty else 0,
            }

        X = self._extraer_features(df)
        y = df['nota'].values

        if len(X) < MIN_MUESTRAS_ENTRENAMIENTO:
            return {
                "exitoso": False,
                "mensaje": f"Se necesitan al menos {MIN_MUESTRAS_ENTRENAMIENTO} muestras para entrenar",
                "muestras": len(X),
            }

        modelo, scaler, _, confianza = self._entrenar_modelo(X, y)
        self.guardar_modelo(modelo, scaler)

        logger.info(
            f"Modelo global entrenado: {len(X)} muestras, confianza={confianza:.2f}"
        )

        return {
            "exitoso": True,
            "mensaje": "Modelo global entrenado exitosamente",
            "muestras": len(X),
            "confianza": confianza,
        }

    # Obtiene predicciones personalizadas para un usuario específico
    def obtener_predicciones_usuario(
        self,
        materias: List,
        evaluaciones: List,
        habitos: List,
        registros: List,
    ) -> Dict[str, Any]:
        df = self.preparar_datos(registros, habitos, evaluaciones)

        if df.empty:
            # Si el modelo global existe, ofrecer predicciones base
            if self.entrenado and self.modelo is not None:
                return {
                    "promedio_predicho": DEFAULT_NOTA_PREDICHA,
                    "estado": "sin_datos_usuario",
                    "confianza": 0.3,
                    "materias": [],
                    "alertas": ["Usuario nuevo: usando modelo global base"],
                    "usando_modelo_global": True,
                }
            return {
                "promedio_predicho": DEFAULT_NOTA_PREDICHA,
                "estado": "sin_datos",
                "confianza": CONFIANZA_SIN_DATOS,
                "materias": [],
                "alertas": ["Registra datos para obtener predicciones"],
            }

        resultado = self._ejecutar_predicciones(materias, df)
        resultado["usando_modelo_global"] = len(df) < MIN_MUESTRAS_ENTRENAMIENTO
        return resultado


# Instancia singleton compartida por toda la aplicación
predictor = PredictorAcademico()