"""
API para obtener información de usuarios.

Los endpoints disponibles son:
- GET /users: devuelve una lista de todos los usuarios en la base de datos.
- GET /users/{profesion}: devuelve una lista de usuarios con la profesión especificada.
- POST /users: crea un nuevo usuario en la base de datos.
- PUT /users/{id}: actualiza un usuario existente en la base de datos.

La API devuelve objetos de tipo UserInDB, que contiene los siguientes campos:
- id: un entero que representa el id del usuario en la base de datos.
- username: un string que representa el nombre de usuario.
- nacimiento: un string que representa la fecha de nacimiento en formato "YYYY-MM-DD".
- numero: un string que representa el número de teléfono.
- gmail: un string que representa el correo electrónico del usuario.
- profesion: un string que representa la profesión del usuario.
- certificado_N: un string que representa el certificado N del usuario.
"""

import uvicorn
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr
import sqlite3
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from contextlib import contextmanager
from typing import Optional

app = FastAPI(
    title="API de Usuarios",
    description="API para obtener información de usuarios",
    version="1.0.0"
)

# Configurar CORS de manera más flexible
origins = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:5501",
    "http://127.0.0.1:5501",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserCreate(BaseModel):
    """
    Clase para crear un nuevo usuario.

    Contiene los siguientes campos:
    - username: un string que representa el nombre de usuario.
    - nacimiento: un string que representa la fecha de nacimiento en formato "YYYY-MM-DD".
    - numero: un string que representa el número de teléfono.
    - gmail: un string que representa el correo electrónico del usuario.
    - profesion: un string que representa la profesión del usuario.
    - certificado_N: un string que representa el certificado N del usuario.
    """
    username: str
    nacimiento: str
    numero: str
    gmail: EmailStr
    profesion: str
    certificado_N: str

class UserUpdate(BaseModel):
    """
    Clase para actualizar un usuario existente.

    Contiene los siguientes campos:
    - username: un string que representa el nombre de usuario.
    - nacimiento: un string que representa la fecha de nacimiento en formato "YYYY-MM-DD".
    - numero: un string que representa el número de teléfono.
    - gmail: un string que representa el correo electrónico del usuario.
    - profesion: un string que representa la profesión del usuario.
    - certificado_N: un string que representa el certificado N del usuario.
    """
    username: str
    nacimiento: str
    numero: str
    gmail: EmailStr
    profesion: str
    certificado_N: Optional[str] = None

class UserInDB(UserCreate):
    """
    Clase que representa un usuario en la base de datos.

    Contiene los siguientes campos:
    - id: un entero que representa el id del usuario en la base de datos.
    - username: un string que representa el nombre de usuario.
    - nacimiento: un string que representa la fecha de nacimiento en formato "YYYY-MM-DD".
    - numero: un string que representa el número de teléfono.
    - gmail: un string que representa el correo electrónico del usuario.
    - profesion: un string que representa la profesión del usuario.
    - certificado_N: un string que representa el certificado N del usuario.
    """
    id: int

@contextmanager
def get_db_connection():
    """
    Context manager para obtener una conexión a la base de datos.

    La conexión se cierra automáticamente al salir del bloque with.
    """
    conn = sqlite3.connect("personas.db")
    try:
        yield conn
    finally:
        conn.close()

def nuevo_usuario(user: UserCreate) -> UserInDB:
    """
    Crea un nuevo usuario en la base de datos.

    Devuelve un objeto UserInDB que representa el usuario creado.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO personas (username, nacimiento, numero, gmail, profesion, certificado_N) VALUES (?, ?, ?, ?, ?, ?)",
            (user.username, user.nacimiento, user.numero, user.gmail, user.profesion, user.certificado_N)
        )
        user_id = cursor.lastrowid
        conn.commit()
    return UserInDB(id=user_id, **user.dict())

def obtener_usuarios() -> List[UserInDB]:
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM personas")
        rows = cursor.fetchall()
        for row in rows:
            print(f"Row length: {len(row)}, Row content: {row}")
            users = [UserInDB(id=row[0], username=row[1], nacimiento=row[2], numero=row[3], gmail=row[4], profesion=row[5], certificado_N=row[6])
                     for row in rows]
    return users

def obtener_usuarios_por_profesion(profesion: str) -> List[UserInDB]:
    """
    Devuelve una lista de usuarios con la profesión especificada.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM personas WHERE profesion = ?", (profesion,))
        users = [UserInDB(id=row[0], username=row[1], nacimiento=row[2], numero=row[3], gmail=row[4], profesion=row[5], certificado_N=row[6])
                 for row in cursor.fetchall()]
    return users

def editar_usuario(id: int, user: UserUpdate) -> UserInDB:
    """
    Actualiza un usuario existente en la base de datos.

    Devuelve un objeto UserInDB que representa el usuario actualizado.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE personas SET username=?, nacimiento=?, numero=?, gmail=?, profesion=?, certificado_N=? WHERE id=?",
            (user.username, user.nacimiento, user.numero, user.gmail, user.profesion, user.certificado_N, id)
        )
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        conn.commit()
    return UserInDB(id=id, **user.dict())

@app.get("/", response_model=List[UserInDB], tags=["Usuarios"])
async def obtener_todos_los_usuarios():
    """
    Devuelve una lista de todos los usuarios en la base de datos.
    """
    return obtener_usuarios()

@app.get("/users/{profesion}", response_model=List[UserInDB], tags=["Usuarios"])
async def obtener_usuarios_por_profesion_route(profesion: str):
    """
    Devuelve una lista de usuarios con la profesión especificada.

    Si no se encontraron usuarios con la profesión especificada, se devuelve un
    error 404.
    """
    users = obtener_usuarios_por_profesion(profesion)
    if not users:
        raise HTTPException(status_code=404, detail="No se encontraron usuarios con esta profesión")
    return users

@app.post("/users", response_model=UserInDB, tags=["Usuarios"])
async def crear_nuevo_usuario(user: UserCreate):
    """
    Crea un nuevo usuario en la base de datos.

    Devuelve el usuario creado en formato UserInDB.
    """
    return nuevo_usuario(user)

@app.put("/users/{id}", response_model=UserInDB, tags=["Usuarios"])
async def editar_usuario_route(id: int, user: UserUpdate):
    """
    Actualiza un usuario existente en la base de datos.

    Devuelve el usuario actualizado en formato UserInDB.

    Si el usuario no existe, se devuelve un error 404.
    """
    try:
        return editar_usuario(id, user)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

