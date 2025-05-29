import os
from flask import Flask, request, jsonify
import pandas as pd
import base64
from io import StringIO

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_csv():
    try:
        data = request.get_json()
        if not data or 'file_base64' not in data:
            return jsonify({"error": "Parâmetro 'file_base64' não encontrado"}), 400

        file_data = base64.b64decode(data['file_base64'])
        csv_string = file_data.decode('utf-8')
        df = pd.read_csv(StringIO(csv_string))

        # Caminho temporário
        temp_path = "/tmp/output.xlsx"

        # Salva arquivo Excel em disco temporário
        with pd.ExcelWriter(temp_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False)

        # Lê arquivo Excel salvo em disco e converte para base64
        with open(temp_path, "rb") as f:
            excel_bytes = f.read()

        excel_base64 = base64.b64encode(excel_bytes).decode('utf-8')

        # Remove o arquivo temporário se quiser
        os.remove(temp_path)

        return jsonify({
            "rows": len(df),
            "columns": list(df.columns),
            "preview": df.head(3).to_dict(orient="records"),
            "excel_base64": excel_base64
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()
