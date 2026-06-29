import pytest
import numpy as np
from datetime import datetime


class TestPredictor:
    def test_preparar_datos_vacio(self):
        from app.ml.predictor import PredictorAcademico
        predictor = PredictorAcademico()
        df = predictor.preparar_datos([], [], [])
        assert df.empty

    def test_preparar_datos_con_evaluaciones(self, test_evaluacion):
        from app.ml.predictor import PredictorAcademico
        predictor = PredictorAcademico()
        df = predictor.preparar_datos([], [], [test_evaluacion])
        assert not df.empty
        assert "nota" in df.columns
        assert "materia_id" in df.columns

    def test_preparar_datos_con_habitos_solo(self, test_habito):
        from app.ml.predictor import PredictorAcademico
        predictor = PredictorAcademico()
        
        class MockEvaluacion:
            def __init__(self):
                self.fecha = datetime.now()
                self.materia_id = 1
                self.nota = 7.0
                self.ponderacion = 1.0
                self.tipo = "examen"
        
        mock_eval = MockEvaluacion()
        df = predictor.preparar_datos([], [test_habito], [mock_eval])
        assert "habito_calidad_promedio" in df.columns

    def test_calcular_tendencias_sin_datos(self):
        from app.ml.predictor import PredictorAcademico
        predictor = PredictorAcademico()
        import pandas as pd
        df = pd.DataFrame()
        tendencia = predictor.calcular_tendencias(df)
        assert tendencia["tendencia"] == "insuficiente"

    def test_calcular_tendencias_positiva(self):
        from app.ml.predictor import PredictorAcademico
        predictor = PredictorAcademico()
        import pandas as pd
        df = pd.DataFrame({
            "fecha": [datetime(2024, 1, 1), datetime(2024, 1, 2), datetime(2024, 1, 3)],
            "nota": [5.0, 6.0, 7.0]
        })
        tendencia = predictor.calcular_tendencias(df)
        assert tendencia["tendencia"] == "positiva"

    def test_calcular_tendencias_negativa(self):
        from app.ml.predictor import PredictorAcademico
        predictor = PredictorAcademico()
        import pandas as pd
        df = pd.DataFrame({
            "fecha": [datetime(2024, 1, 1), datetime(2024, 1, 2), datetime(2024, 1, 3)],
            "nota": [7.0, 6.0, 5.0]
        })
        tendencia = predictor.calcular_tendencias(df)
        assert tendencia["tendencia"] == "negativa"

    def test_predecir_nota_sin_datos(self, test_materia):
        from app.ml.predictor import PredictorAcademico
        predictor = PredictorAcademico()
        import pandas as pd
        df = pd.DataFrame()
        pred = predictor.predecir_nota(test_materia.id, df)
        assert pred["prediccion_nota"] == 5.0
        assert pred["confianza"] == 0.2

    def test_predecir_rendimiento_sin_datos(self):
        from app.ml.predictor import PredictorAcademico
        predictor = PredictorAcademico()
        result = predictor.predecir_rendimiento_general([], [], [], [])
        assert result["promedio_predicho"] == 5.0
        assert result["estado"] == "sin_datos"

    def test_entrenar_modelo_global_sin_datos(self):
        from app.ml.predictor import PredictorAcademico
        predictor = PredictorAcademico()
        result = predictor.entrenar_modelo_global([], [], [])
        assert result["exitoso"] == False

    def test_obtener_predicciones_usuario_sin_datos(self):
        from app.ml.predictor import PredictorAcademico
        predictor = PredictorAcademico()
        result = predictor.obtener_predicciones_usuario([], [], [], [])
        assert "estado" in result
        assert result["promedio_predicho"] == 5.0

    def test_features_habitos_incluidos(self, test_habito, test_evaluacion):
        from app.ml.predictor import PredictorAcademico
        predictor = PredictorAcademico()
        df = predictor.preparar_datos([], [test_habito], [test_evaluacion])
        
        expected_features = [
            "habito_descanso_semanal",
            "habito_distraccion_semanal", 
            "habito_ejercicio_semanal",
            "habito_sueno_semanal",
            "ratio_estudio_distraccion",
            "habito_calidad_promedio"
        ]
        
        for feature in expected_features:
            assert feature in df.columns

    def test_prediccion_rango_valido(self, test_materia, test_evaluacion):
        from app.ml.predictor import PredictorAcademico
        predictor = PredictorAcademico()
        import pandas as pd
        df = predictor.preparar_datos([], [], [test_evaluacion])
        pred = predictor.predecir_nota(test_materia.id, df)
        assert 1.0 <= pred["prediccion_nota"] <= 10.0
