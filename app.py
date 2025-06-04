from flask import Flask, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)  # 👈 Habilita CORS para todos los orígenes

DATA_FILE = "data/data.json"

def load_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

@app.route('/products', methods=['GET'])
def get_products():
    data = load_data()
    return jsonify(data)

if __name__ == '__main__':
    #app.run(debug=True)
    app.run(debug=True, host="0.0.0.0", port=10000)
