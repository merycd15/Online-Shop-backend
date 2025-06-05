from flask import Flask, jsonify, request, redirect, url_for, render_template_string
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import json
import pandas as pd
from dotenv import load_dotenv
from pathlib import Path

# Cargar variables de entorno
load_dotenv(dotenv_path=Path('.') / '.env')


DATA_FILE = "data/data.json"
UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {'xlsx'}

# Flask
app = Flask(__name__)
CORS(app)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Credenciales desde .env
VALID_USERNAME = os.getenv("MYAPP_USERNAME")
VALID_PASSWORD = os.getenv("MYAPP_PASSWORD")


print("Usuario cargado:", VALID_USERNAME)
print("Password cargado:", VALID_PASSWORD)
# Configuración

# Crear carpetas necesarias
os.makedirs("data", exist_ok=True)
os.makedirs("uploads", exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

# Página de login
@app.route('/excel', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            return redirect(url_for('upload_excel'))
        return "Credenciales inválidas", 401
    return render_template_string('''
        <form method="POST">
            Usuario: <input name="username" type="text" /><br/>
            Contraseña: <input name="password" type="password" /><br/>
            <input type="submit" value="Ingresar" />
        </form>
    ''')

# Página para subir el Excel
@app.route('/upload', methods=['GET', 'POST'])
def upload_excel():
    if request.method == 'POST':
        file = request.files.get('file')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            df = pd.read_excel(filepath)
            # Asegurarse de que tenga las columnas correctas
            if not {'id', 'title', 'price', 'category', 'image'}.issubset(df.columns):
                return "Formato de Excel incorrecto", 400

            # Convertir a lista de dicts
            data = df.to_dict(orient='records')
            save_data(data)
            return "Archivo cargado y datos actualizados correctamente"

        return "Archivo inválido", 400
    return render_template_string('''
        <form method="POST" enctype="multipart/form-data">
            Subí tu archivo Excel (.xlsx): <input type="file" name="file" /><br/>
            <input type="submit" value="Cargar" />
        </form>
    ''')

# Endpoint para servir los productos al frontend
@app.route('/products', methods=['GET'])
def get_products():
    try:
        data = load_data()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)


