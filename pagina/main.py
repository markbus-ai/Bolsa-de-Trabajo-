from flask import Flask, render_template, request, redirect, url_for
import requests
import json

app = Flask(__name__)

API_URL = "http://localhost:8002"  # Asegúrate de que esta URL coincida con la de tu API

# @app.route('/')
# def index():
#     response = requests.get(f"{API_URL}/users")
#     if response.status_code == 200:
#         users = response.json()
#         return render_template('index.html', users=users)
#     else:
#         return "Error al obtener los usuarios", 500

@app.route('/users/<profesion>')
def users_by_profession(profesion):
    response = requests.get(f"{API_URL}/users/{profesion}")
    if response.status_code == 200:
        users = response.json()
        return render_template('users_by_profession.html', users=users, profesion=profesion)
    else:
        return "Error al obtener los usuarios por profesión", 500

users = []

@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        new_user = {
            "id": int(request.form['id']),
            "username": request.form['username'],
            "nacimiento": request.form['nacimiento'],
            "numero": request.form['numero'],
            "gmail": request.form['gmail'],
            "profesion": request.form['profesion']
        }
        print("Tipo de nuevo usuario:", type(new_user))
        print("Nuevo usuario añadido:", new_user)
        url = f'{API_URL}/users'
        response = requests.post(url, json=new_user)
        return response.json()
        users.append(new_user)
        
        # Guardar en un archivo JSON
        with open('users.json', 'w') as f:
            json.dump(users, f)
        
        return redirect(url_for('index'))
    return render_template('add_user.html')

@app.route('/')
def index():
    print("Tipo de users:", type(users))
    print("Contenido de users:", users)
    for user in users:
        print("Tipo de usuario:", type(user))
        print("Contenido de usuario:", user)
    return render_template('index.html', users=users)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
