from typing import List, Dict, Any
from datetime import datetime, timedelta

class GeneradorRecomendaciones:
    def __init__(self):
        self.recomendaciones = []
    
    def generar_recomendaciones(
        self,
        materias: List,
        registros: List,
        habitos: List,
        evaluaciones: List,
        predicciones: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        recomendaciones = []
        
        recomendaciones.extend(self._analizar_habitos(habitos))
        recomendaciones.extend(self._analizar_rendimiento(evaluaciones, predicciones))
        recomendaciones.extend(self._analizar_registros(registros))
        
        return recomendaciones[:10]
    
    def _analizar_habitos(self, habitos: List) -> List[Dict[str, Any]]:
        recomendaciones = []
        
        if not habitos:
            recomendaciones.append({
                "tipo": "habito",
                "titulo": "Registra tus hábitos",
                "descripcion": "Comienza a registrar tus hábitos diarios (descansos, distracciones, sueño) para obtener recomendaciones personalizadas.",
                "prioridad": "alta",
                "materia_id": None
            })
            return recomendaciones
        
        habitos_dict = {}
        for h in habitos:
            tipo = h.tipo if hasattr(h, 'tipo') else str(h)
            duracion = h.duracion_minutos if hasattr(h, 'duracion_minutos') else 0
            if tipo not in habitos_dict:
                habitos_dict[tipo] = 0
            habitos_dict[tipo] += duracion
        
        if habitos_dict.get('distraccion', 0) > 120:
            recomendaciones.append({
                "tipo": "habito",
                "titulo": "Reduce las distracciones",
                "descripcion": "Has registrado más de 2 horas de distracciones esta semana. Considera usar la técnica Pomodoro para mantener el enfoque.",
                "prioridad": "alta",
                "materia_id": None
            })
        
        if habitos_dict.get('descanso', 0) < 30:
            recomendaciones.append({
                "tipo": "habito",
                "titulo": " Toma más descansos",
                "descripcion": "No has descansado lo suficiente. Los estudios muestran que los descansos regulares mejoran la retención de información.",
                "prioridad": "media",
                "materia_id": None
            })
        
        if habitos_dict.get('sueno', 0) < 300:
            recomendaciones.append({
                "tipo": "habito",
                "titulo": "Duerme más",
                "descripcion": "Duerme al menos 7-8 horas para un óptimo rendimiento académico.",
                "prioridad": "alta",
                "materia_id": None
            })
        
        return recomendaciones
    
    def _analizar_rendimiento(
        self, 
        evaluaciones: List, 
        predicciones: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        recomendaciones = []
        
        if not evaluaciones:
            recomendaciones.append({
                "tipo": "rendimiento",
                "titulo": "Registra tus evaluaciones",
                "descripcion": "Registra tus notas de exámenes, tareas y proyectos para analizar tu rendimiento.",
                "prioridad": "alta",
                "materia_id": None
            })
            return recomendaciones
        
        if 'alertas' in predicciones:
            for alerta in predicciones['alertas']:
                if 'Riesgo' in alerta:
                    recomendaciones.append({
                        "tipo": "rendimiento",
                        "titulo": "Alerta de rendimiento bajo",
                        "descripcion": alerta,
                        "prioridad": "alta",
                        "materia_id": None
                    })
        
        return recomendaciones
    
    def _analizar_registros(self, registros: List) -> List[Dict[str, Any]]:
        recomendaciones = []
        
        if not registros:
            recomendaciones.append({
                "tipo": "estudio",
                "titulo": "Registra tu tiempo de estudio",
                "descripcion": "Registra tus sesiones de estudio para que el sistema analice tus patrones y te ayude a mejorar.",
                "prioridad": "media",
                "materia_id": None
            })
            return recomendaciones
        
        return recomendaciones


generador = GeneradorRecomendaciones()
