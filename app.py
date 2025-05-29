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

        # Decodifica o conteúdo base64
        file_data = base64.b64decode(data['file_base64'])
        csv_string = file_data.decode('utf-8')

        # Converte CSV em DataFrame
        df = pd.read_csv(StringIO(csv_string))

        # Exemplo: retornar o número de linhas e colunas
        return jsonify({
            "rows": len(df),
            "columns": list(df.columns),
            "preview": df.head(3).to_dict(orient="records")
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()
