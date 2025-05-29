from flask import Flask, request, jsonify
import pandas as pd
import base64
from io import StringIO
import os

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_csv():
    try:
        data = request.get_json()
        if not data or 'file_base64' not in data:
            return jsonify({"error": "Parâmetro 'file_base64' não encontrado"}), 400

        # Decodifica CSV
        file_data = base64.b64decode(data['file_base64'])
        csv_string = file_data.decode('utf-8')

        # Lê CSV em partes (melhora performance)
        chunks = pd.read_csv(StringIO(csv_string), chunksize=5000)

        # Gera Excel no disco
        output_path = '/tmp/arquivo.xlsx'
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            for i, chunk in enumerate(chunks):
                chunk.to_excel(writer, index=False, sheet_name=f"Parte{i+1}")

        # Lê o Excel gerado e converte para base64
        with open(output_path, 'rb') as f:
            excel_base64 = base64.b64encode(f.read()).decode('utf-8')

        return jsonify({
            "filename": "arquivo.xlsx",
            "file_base64": excel_base64
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()
