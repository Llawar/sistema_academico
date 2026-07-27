"""
Script para reentrenar el modelo ML directamente desde la base de datos.
Ejecutar: python reentrenar.py
"""

import sys
import os

# Agregar el directorio app al path para imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from app.core.database import SessionLocal
from app.models.models import Evaluacion, DatoHabitual, RegistroDiario
from app.ml.predictor import predictor


def main():
    print("=" * 50)
    print("  REENTRENAMIENTO DEL MODELO ML")
    print("=" * 50)

    # Conectar directamente a la BD
    db = SessionLocal()
    try:
        print("\nConsultando base de datos...")
        evaluaciones = db.query(Evaluacion).all()
        habitos = db.query(DatoHabitual).all()
        registros = db.query(RegistroDiario).all()

        print(f"  Evaluaciones encontradas: {len(evaluaciones)}")
        print(f"  Hábitos encontrados:      {len(habitos)}")
        print(f"  Registros encontrados:    {len(registros)}")

        if len(evaluaciones) < 5:
            print("\n  Se necesitan al menos 5 evaluaciones para entrenar.")
            print("  Registra más evaluaciones y vuelve a intentar.")
            return

        print("\nEntrenando modelo...")
        resultado = predictor.entrenar_modelo_global(
            evaluaciones, habitos, registros
        )

        if resultado["exitoso"]:
            print(f"\n  ✅ Modelo entrenado exitosamente")
            print(f"  Muestras usadas: {resultado['muestras']}")
            print(f"  Confianza:       {resultado['confianza']}")
        else:
            print(f"\n  ❌ No se pudo entrenar: {resultado['mensaje']}")

    finally:
        db.close()

    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()