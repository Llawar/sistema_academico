import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import joblib
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

MODEL_PATH = Path(__file__).parent / "Master_ML.joblib"
SCALER_PATH = Path(__file__).parent / "Master_ML_scaler.joblib"
DATA_PATH = Path(__file__).parent / "training_data.csv"

class PredictorAcademico:
    def __init__(self):
        self.modelo = None
        self.scaler = None
        self.entrenado = False
        self.version = "1.0"
        self.cargar_modelo()
    
    def cargar_modelo(self) -> bool:
        if MODEL_PATH.exists() and SCALER_PATH.exists():
            try:
                self.modelo = joblib.load(MODEL_PATH)
                self.scaler = joblib.load(SCALER_PATH)
                self.entrenado = True
                print(f"Modelo ML cargado desde {MODEL_PATH}")
                return True
            except Exception as e:
                print(f"Error al cargar modelo: {e}")
                self.entrenado = False
                return False
        return False
    
    def guardar_modelo(self, modelo, scaler) -> bool:
        try:
            joblib.dump(modelo, MODEL_PATH)
            joblib.dump(scaler, SCALER_PATH)
            self.modelo = modelo
            self.scaler = scaler
            self.entrenado = True
            print(f"Modelo ML guardado en {MODEL_PATH}")
            return True
        except Exception as e:
            print(f"Error al guardar modelo: {e}")
            return False
    
    def entrenar_y_guardar(self, X: np.ndarray, y: np.ndarray):
        modelo, scaler, prediccion, confianza = self._entrenar_modelo(X, y)
        self.guardar_modelo(modelo, scaler)
        return modelo, scaler, prediccion, confianza
    
    def necesita_reentrenamiento(self, n_evaluaciones: int) -> bool:
        return not self.entrenado or n_evaluaciones >= 5
    
    def preparar_datos(self, registros: List, habitos: List, evaluaciones: List) -> pd.DataFrame:
        if not registros and not evaluaciones:
            return pd.DataFrame()
        
        datos = []
        
        for ev in evaluaciones:
            fecha = ev.fecha if hasattr(ev, 'fecha') else datetime.utcnow()
            datos.append({
                'fecha': fecha,
                'materia_id': ev.materia_id,
                'nota': ev.nota,
                'ponderacion': ev.ponderacion,
                'tipo': ev.tipo
            })
        
        df = pd.DataFrame(datos)
        if df.empty:
            return df
        
        df['fecha'] = pd.to_datetime(df['fecha'])
        df['semana'] = df['fecha'].dt.isocalendar().week
        df['mes'] = df['fecha'].dt.month
        df['dia_semana'] = df['fecha'].dt.dayofweek
        
        df = self._agregar_features_habitos(df, habitos)
        
        return df
    
    def _agregar_features_habitos(self, df: pd.DataFrame, habitos: List) -> pd.DataFrame:
        if not habitos:
            df['habito_descanso_semanal'] = 0
            df['habito_distraccion_semanal'] = 0
            df['habito_ejercicio_semanal'] = 0
            df['habito_sueno_semanal'] = 0
            df['ratio_estudio_distraccion'] = 1.0
            df['habito_calidad_promedio'] = 0.5
            return df
        
        habitos_df = pd.DataFrame([
            {
                'fecha': h.fecha if hasattr(h, 'fecha') else datetime.utcnow(),
                'tipo': h.tipo,
                'duracion_minutos': h.duracion_minutos
            }
            for h in habitos
        ])
        
        if habitos_df.empty:
            df['habito_descanso_semanal'] = 0
            df['habito_distraccion_semanal'] = 0
            df['habito_ejercicio_semanal'] = 0
            df['habito_sueno_semanal'] = 0
            df['ratio_estudio_distraccion'] = 1.0
            df['habito_calidad_promedio'] = 0.5
            return df
        
        habitos_df['fecha'] = pd.to_datetime(habitos_df['fecha'])
        habitos_df['semana'] = habitos_df['fecha'].dt.isocalendar().week
        habitos_df['mes'] = habitos_df['fecha'].dt.month
        
        habitos_por_semana = habitos_df.groupby(['semana', 'tipo'])['duracion_minutos'].sum().unstack(fill_value=0)
        
        df['habito_descanso_semanal'] = df.apply(
            lambda row: habitos_por_semana.loc[row['semana'], 'descanso'] if row['semana'] in habitos_por_semana.index and 'descanso' in habitos_por_semana.columns else 0,
            axis=1
        )
        df['habito_distraccion_semanal'] = df.apply(
            lambda row: habitos_por_semana.loc[row['semana'], 'distraccion'] if row['semana'] in habitos_por_semana.index and 'distraccion' in habitos_por_semana.columns else 0,
            axis=1
        )
        df['habito_ejercicio_semanal'] = df.apply(
            lambda row: habitos_por_semana.loc[row['semana'], 'ejercicio'] if row['semana'] in habitos_por_semana.index and 'ejercicio' in habitos_por_semana.columns else 0,
            axis=1
        )
        df['habito_sueno_semanal'] = df.apply(
            lambda row: habitos_por_semana.loc[row['semana'], 'sueno'] if row['semana'] in habitos_por_semana.index and 'sueno' in habitos_por_semana.columns else 0,
            axis=1
        )
        
        df['ratio_estudio_distraccion'] = df['habito_descanso_semanal'] / (df['habito_distraccion_semanal'] + 1)
        
        total_habitos = habitos_df['duracion_minutos'].sum()
        if total_habitos > 0:
            distraccion_ratio = habitos_df[habitos_df['tipo'] == 'distraccion']['duracion_minutos'].sum() / total_habitos
            df['habito_calidad_promedio'] = 1 - distraccion_ratio
        else:
            df['habito_calidad_promedio'] = 0.5
        
        df['habito_calidad_promedio'] = df['habito_calidad_promedio'].fillna(0.5)
        
        return df
    
    def calcular_tendencias(self, df: pd.DataFrame) -> Dict[str, Any]:
        if df.empty or len(df) < 2:
            return {"tendencia": "insuficiente", "cambio": 0, "confianza": 0}
        
        df_sorted = df.sort_values('fecha')
        notas = df_sorted['nota'].values
        
        if len(notas) < 2:
            return {"tendencia": "estable", "cambio": 0, "confianza": 0.3}
        
        x = np.arange(len(notas))
        coeffs = np.polyfit(x, notas, 1)
        pendiente = coeffs[0]
        
        cambio_porcentual = (notas[-1] - notas[0]) / notas[0] * 100 if notas[0] > 0 else 0
        
        if pendiente > 0.1:
            tendencia = "positiva"
            confianza = min(0.9, 0.5 + abs(pendiente) * 2)
        elif pendiente < -0.1:
            tendencia = "negativa"
            confianza = min(0.9, 0.5 + abs(pendiente) * 2)
        else:
            tendencia = "estable"
            confianza = 0.5
        
        return {
            "tendencia": tendencia,
            "cambio": round(cambio_porcentual, 2),
            "confianza": round(confianza, 2)
        }
    
    def predecir_nota(self, materia_id: int, df: pd.DataFrame) -> Dict[str, Any]:
        if df.empty:
            return {
                "materia_id": materia_id,
                "prediccion_nota": 5.0,
                "confianza": 0.2,
                "tendencia": "sin_datos",
                "factores": ["Registra más evaluaciones para obtener predicciones precisas"]
            }
        
        df_materia = df[df['materia_id'] == materia_id]
        
        if df_materia.empty:
            return {
                "materia_id": materia_id,
                "prediccion_nota": 5.0,
                "confianza": 0.2,
                "tendencia": "sin_datos",
                "factores": ["No hay evaluaciones registradas para esta materia"]
            }
        
        tendencias = self.calcular_tendencias(df_materia)
        
        if len(df_materia) >= 1 and len(df) >= 3:
            try:
                df_features = df_materia.copy()
                df_features = df_features.drop(['nota', 'tipo', 'materia_id'], axis=1, errors='ignore')
                
                if 'fecha' in df_features.columns:
                    df_features = df_features.drop(['fecha'], axis=1)
                
                X = df_features.values
                y = df_materia['nota'].values
                
                if len(X) < 1:
                    raise ValueError("Datos insuficientes")
                
                df_all_features = df.copy()
                df_all_features = df_all_features.drop(['nota', 'tipo', 'materia_id'], axis=1, errors='ignore')
                if 'fecha' in df_all_features.columns:
                    df_all_features = df_all_features.drop(['fecha'], axis=1)
                
                X_all = df_all_features.values
                y_all = df['nota'].values
                
                if self.entrenado and self.modelo is not None and self.scaler is not None:
                    try:
                        X_scaled = self.scaler.transform(X)
                        prediccion_ml = self.modelo.predict(X_scaled)[0]
                        nota_base = df_materia['nota'].mean()
                        prediccion = (nota_base * 0.3 + prediccion_ml * 0.7)
                        prediccion = max(1.0, min(10.0, prediccion))
                        confianza = 0.75
                        print(f"Usando modelo persistente para materia {materia_id}")
                    except Exception as e:
                        print(f"Error usando modelo persistente: {e}, reentrenando...")
                        modelo, scaler, prediccion, confianza = self._entrenar_modelo(X_all, y_all)
                        self.guardar_modelo(modelo, scaler)
                else:
                    print(f"Entrenando nuevo modelo con {len(X_all)} samples...")
                    modelo, scaler, prediccion, confianza = self._entrenar_modelo(X_all, y_all)
                    self.guardar_modelo(modelo, scaler)
                
                factores = self._analizar_factores(df_materia)
                
                return {
                    "materia_id": materia_id,
                    "prediccion_nota": round(prediccion, 2),
                    "confianza": round(confianza, 2),
                    "tendencia": tendencias["tendencia"],
                    "factores": factores
                }
            except Exception as e:
                nota_base = df_materia['nota'].mean()
                return {
                    "materia_id": materia_id,
                    "prediccion_nota": round(nota_base, 2),
                    "confianza": 0.4,
                    "tendencia": tendencias["tendencia"],
                    "factores": ["Datos limitados para predicción avanzada"]
                }
        else:
            nota_base = df_materia['nota'].mean()
            return {
                "materia_id": materia_id,
                "prediccion_nota": round(nota_base, 2),
                "confianza": 0.35,
                "tendencia": tendencias["tendencia"],
                "factores": ["Registra más evaluaciones para mejorar la predicción"]
            }
    
    def _entrenar_modelo(self, X: np.ndarray, y: np.ndarray) -> Tuple:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        modelo = GradientBoostingRegressor(
            n_estimators=50,
            max_depth=3,
            learning_rate=0.1,
            random_state=42
        )
        modelo.fit(X_train_scaled, y_train)
        
        y_pred = modelo.predict(X_test_scaled)
        mae = mean_absolute_error(y_test, y_pred)
        
        nota_base = y.mean()
        ajuste = modelo.predict(X_train_scaled[-1:])[0] if len(X_train) > 0 else nota_base
        
        prediccion = (nota_base * 0.3 + ajuste * 0.7)
        prediccion = max(1.0, min(10.0, prediccion))
        
        confianza = min(0.95, max(0.3, 1 - mae / 3))
        
        return modelo, scaler, prediccion, confianza
    
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
    
    def predecir_rendimiento_general(
        self, 
        materias: List, 
        registros: List, 
        habitos: List, 
        evaluaciones: List
    ) -> Dict[str, Any]:
        df = self.preparar_datos(registros, habitos, evaluaciones)
        
        if df.empty:
            return {
                "promedio_predicho": 5.0,
                "estado": "sin_datos",
                "confianza": 0.2,
                "alertas": ["Registra tus hábitos y evaluaciones para obtener predicciones"]
            }
        
        predicciones_materias = []
        for materia in materias:
            pred = self.predecir_nota(materia.id, df)
            pred['materia_nombre'] = materia.nombre
            predicciones_materias.append(pred)
        
        notas_predichas = [p['prediccion_nota'] for p in predicciones_materias]
        promedio = sum(notas_predichas) / len(notas_predichas) if notas_predichas else 5.0
        
        alertas = []
        for p in predicciones_materias:
            if p['prediccion_nota'] < 5.0:
                alertas.append(f"Riesgo en {p['materia_nombre']}: predicción bajo 5.0")
            elif p['tendencia'] == "negativa":
                alertas.append(f"Baja tendencia en {p['materia_nombre']}")
        
        return {
            "promedio_predicho": round(promedio, 2),
            "confianza": round(sum(p['confianza'] for p in predicciones_materias) / len(predicciones_materias), 2),
            "materias": predicciones_materias,
            "alertas": alertas
        }
    
    def entrenar_modelo_global(
        self, 
        todas_evaluaciones: List, 
        todos_habitos: List, 
        todos_registros: List
    ) -> Dict[str, Any]:
        df = self.preparar_datos(todos_registros, todos_habitos, todas_evaluaciones)
        
        if df.empty or len(df) < 5:
            return {
                "exitoso": False,
                "mensaje": "No hay suficientes datos globales para entrenar",
                "muestras": len(df) if not df.empty else 0
            }
        
        df_features = df.copy()
        df_features = df_features.drop(['nota', 'tipo', 'materia_id'], axis=1, errors='ignore')
        if 'fecha' in df_features.columns:
            df_features = df_features.drop(['fecha'], axis=1)
        
        X = df_features.values
        y = df['nota'].values
        
        if len(X) < 5:
            return {
                "exitoso": False,
                "mensaje": "Se necesitan al menos 5 muestras para entrenar",
                "muestras": len(X)
            }
        
        modelo, scaler, _, confianza = self._entrenar_modelo(X, y)
        self.guardar_modelo(modelo, scaler)
        
        return {
            "exitoso": True,
            "mensaje": "Modelo global entrenado exitosamente",
            "muestras": len(X),
            "confianza": confianza
        }
    
    def obtener_predicciones_usuario(
        self,
        materias: List,
        evaluaciones: List,
        habitos: List,
        registros: List
    ) -> Dict[str, Any]:
        df = self.preparar_datos(registros, habitos, evaluaciones)
        
        if df.empty:
            if self.entrenado and self.modelo is not None:
                return {
                    "promedio_predicho": 5.0,
                    "estado": "sin_datos_usuario",
                    "confianza": 0.3,
                    "materias": [],
                    "alertas": ["Usuario nuevo: usando modelo global base"],
                    "usando_modelo_global": True
                }
            return {
                "promedio_predicho": 5.0,
                "estado": "sin_datos",
                "confianza": 0.1,
                "materias": [],
                "alertas": ["Registra datos para obtener predicciones"]
            }
        
        predicciones_materias = []
        for materia in materias:
            pred = self.predecir_nota(materia.id, df)
            pred['materia_nombre'] = materia.nombre
            predicciones_materias.append(pred)
        
        notas_predichas = [p['prediccion_nota'] for p in predicciones_materias]
        promedio = sum(notas_predichas) / len(notas_predichas) if notas_predichas else 5.0
        
        alertas = []
        for p in predicciones_materias:
            if p['prediccion_nota'] < 5.0:
                alertas.append(f"Riesgo en {p['materia_nombre']}: predicción bajo 5.0")
            elif p['tendencia'] == "negativa":
                alertas.append(f"Baja tendencia en {p['materia_nombre']}")
        
        return {
            "promedio_predicho": round(promedio, 2),
            "confianza": round(sum(p['confianza'] for p in predicciones_materias) / len(predicciones_materias), 2),
            "materias": predicciones_materias,
            "alertas": alertas,
            "usando_modelo_global": True if len(df) < 3 else False
        }


predictor = PredictorAcademico()
