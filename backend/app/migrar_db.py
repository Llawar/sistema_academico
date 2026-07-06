import sqlite3
import os
from datetime import datetime

# ══════════════════════════════════════════
# Configuración
# ══════════════════════════════════════════

# Ruta de tu base de datos (ajusta si es necesario)
DB_PATHS = [
    "app/academico.db",
    "academico.db",
]

def encontrar_db():
    """Busca la base de datos en las rutas posibles."""
    for path in DB_PATHS:
        if os.path.exists(path):
            return path
    return None

# ══════════════════════════════════════════
# Script principal
# ══════════════════════════════════════════

def migrar():
    db_path = encontrar_db()

    if not db_path:
        print("ERROR: No se encontró academico.db")
        print("Busqué en:", DB_PATHS)
        return

    print(f"Base de datos encontrada: {db_path}")

    # 1. Crear backup
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"Creando backup: {backup_path}")

    import shutil
    shutil.copy2(db_path, backup_path)
    print("Backup creado correctamente\n")

    # 2. Conectar a la BD
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 3. Verificar que la tabla existe y tiene las columnas
    cursor.execute("PRAGMA table_info(usuarios)")
    columnas = [col[1] for col in cursor.fetchall()]
    print(f"Columnas actuales: {columnas}\n")

    if 'carrera' not in columnas and 'semestre' not in columnas:
        print("Las columnas 'carrera' y 'semestre' ya no existen.")
        print("No hay nada que migrar.")
        conn.close()
        os.remove(backup_path)
        return

    # 4. Definir columnas a conservar (las que NO eliminamos)
    columnas_a_conservar = [
        col for col in columnas
        if col not in ('carrera', 'semestre')
    ]
    columnas_str = ', '.join(columnas_a_conservar)
    print(f"Columnas a conservar: {columnas_a_conservar}\n")

    # 5. Crear tabla temporal con la nueva estructura
    print("Paso 1: Creando tabla temporal...")

    cursor.execute(f"""
        CREATE TABLE usuarios_nueva (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR(255) NOT NULL UNIQUE,
            hashed_password VARCHAR(255) NOT NULL,
            nombre VARCHAR(255) NOT NULL,
            objetivo_promedio FLOAT DEFAULT 7.0,
            created_at DATETIME
        )
    """)

    # 6. Copiar datos de la tabla vieja a la nueva
    print("Paso 2: Copiando datos...")

    cursor.execute(f"""
        INSERT INTO usuarios_nueva ({columnas_str})
        SELECT {columnas_str}
        FROM usuarios
    """)

    filas_copiadas = cursor.rowcount
    print(f"  {filas_copiadas} usuarios migrados\n")

    # 7. Eliminar tabla vieja
    print("Paso 3: Eliminando tabla vieja...")
    cursor.execute("DROP TABLE usuarios")

    # 8. Renombrar tabla nueva
    print("Paso 4: Renombrando tabla nueva...")
    cursor.execute("ALTER TABLE usuarios_nueva RENAME TO usuarios")

    # 9. Guardar cambios
    conn.commit()

    # 10. Verificar resultado
    print("\nVerificando migración...")
    cursor.execute("PRAGMA table_info(usuarios)")
    nuevas_columnas = [col[1] for col in cursor.fetchall()]
    print(f"Columnas nuevas: {nuevas_columnas}")

    cursor.execute("SELECT COUNT(*) FROM usuarios")
    total = cursor.fetchone()[0]
    print(f"Total usuarios: {total}")

    conn.close()

    # 11. Resumen
    print("\n" + "=" * 50)
    print("MIGRACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 50)
    print(f"  Backup guardado en: {backup_path}")
    print(f"  Usuarios migrados:  {filas_copiadas}")
    print(f"  Columnas eliminadas: carrera, semestre")
    print(f"\nAhora reinicia el backend:")
    print(f"  python -m uvicorn app.main:app --reload --port 8000")


if __name__ == "__main__":
    print("=" * 50)
    print("MIGRACIÓN: Eliminar carrera y semestre")
    print("=" * 50 + "\n")

    confirmacion = input("¿Continuar? (s/n): ").strip().lower()

    if confirmacion == 's':
        try:
            migrar()
        except Exception as e:
            print(f"\nERROR: {e}")
            print("\nSi algo salió mal, restaura el backup:")
            print("  Solo renombra el archivo .backup a academico.db")
    else:
        print("Migración cancelada.")