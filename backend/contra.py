import sqlite3
import bcrypt

# Función correcta para encriptar
def get_password_hash(password: str) -> str:
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed_bytes.decode('utf-8')

# Conectamos a la BD
conn = sqlite3.connect("app/academico.db")
cursor = conn.cursor()

# Generamos el hash seguro de "123456"
nuevo_hash = get_password_hash("12345678")

# Actualizamos a TODOS los usuarios
cursor.execute("UPDATE usuarios SET hashed_password = ?", (nuevo_hash,))
conn.commit()

print(f"✅ Éxito: Se actualizaron las contraseñas de {cursor.rowcount} usuarios.")
print("Todos los usuarios ahora pueden entrar con la contraseña:  123456")

conn.close()