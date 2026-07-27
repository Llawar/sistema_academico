import jwt
import bcrypt

print("\n" + "="*50)
print("ARCHIVO BCRYPT CARGADO:", bcrypt.__file__)
print("HERRAMIENTAS DENTRO DE BCRYPT:", dir(bcrypt))
print("="*50 + "\n")

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from ..core.database import get_db, settings
from ..models.models import Usuario
from ..schemas.schemas import (
    UsuarioCreate, UsuarioResponse, LoginRequest, TokenResponse, UsuarioUpdate
)

router = APIRouter(prefix="/auth", tags=["Autenticación"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# Verifica contraseña con bcrypt
def verify_password(plain_password: str, hashed_password: str) -> bool:
    # Convertimos ambos textos a bytes con .encode('utf-8') para que bcrypt no se queje
    password_bytes = plain_password.encode('utf-8')
    hash_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hash_bytes)


# Genera hash de contraseña con bcrypt
def get_password_hash(password: str) -> str:
    # Convertimos la contraseña a bytes, la encriptamos, y la devolvemos como texto (.decode)
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)
    return hashed_bytes.decode('utf-8')


# Crea token JWT de acceso
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


# Obtiene usuario autenticado desde el token
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        user_id = int(user_id)
    except (jwt.InvalidTokenError, ValueError):
        raise credentials_exception
    
    user = db.query(Usuario).filter(Usuario.id == user_id).first()
    if user is None:
        raise credentials_exception
    return user


# Registra un nuevo usuario
@router.post("/register", response_model=UsuarioResponse)
def register(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    db_user = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    
    hashed_password = get_password_hash(usuario.password)
    db_usuario = Usuario(
        email=usuario.email,
        hashed_password=hashed_password,
        nombre=usuario.nombre,
        objetivo_promedio=usuario.objetivo_promedio
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)
    return db_usuario


# Inicia sesión y devuelve token JWT
@router.post("/login", response_model=TokenResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Usuario).filter(Usuario.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos"
        )
    
    access_token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(access_token=access_token, usuario=user)


# Obtiene perfil del usuario actual
@router.get("/me", response_model=UsuarioResponse)
def get_me(current_user: Usuario = Depends(get_current_user)):
    return current_user


# Actualiza perfil del usuario actual
@router.put("/me", response_model=UsuarioResponse)
def update_me(
    usuario_update: UsuarioUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if usuario_update.nombre is not None:
        current_user.nombre = usuario_update.nombre
    if usuario_update.objetivo_promedio is not None:
        current_user.objetivo_promedio = usuario_update.objetivo_promedio
    
    db.commit()
    db.refresh(current_user)
    return current_user
