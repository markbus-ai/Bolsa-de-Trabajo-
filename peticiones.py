import requests
import reflex as rx

def obtener_todos_los_usuarios():
    url = 'http://localhost:8000/users'
    response = requests.get(url)
    return response.json()

def obtener_usuarios_por_profesion(profesion):
    url = f'http://localhost:8000/users/{profesion}'
    response = requests.get(url)
    return response.json()

def nuevo_usuario(user):
    url = 'http://localhost:8000/users'
    response = requests.post(url, json=user)
    return response.json()

user = {
    "id": 4,
    "username": "pedro",
    "nacimiento": "1990-01-01",
    "numero": "123456789",
    "gmail": "pedro@pedro",
    "profesion": "programador"
}
nuevo_usuario(user)