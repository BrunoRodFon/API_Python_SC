from flask import Flask, request, jsonify
import pandas as pd
import base64
from io import StringIO, BytesIO

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_csv():
    try:
        data = request.get_json()
        if not data or 'file_base64' not in data:
            return jsonify({"error": "Parâmetro 'file_base64' não encontrado"}), 400

        # Decodifica o conteúdo base64 (CSV)
        file_data = base64.b64decode(data['file_base64'])
        csv_string = file_data.decode('utf-8')

        # Converte CSV em DataFrame
        df = pd.read_csv(StringIO(csv_string))

        # Gerar Excel na memória
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Planilha1')
        output.seek(0)

        # Codificar Excel em base64 para retornar na resposta JSON
        excel_base64 = base64.b64encode(output.read()).decode('utf-8')

        # Retornar o arquivo Excel codificado em base64 para o Power Automate
        return jsonify({
            "rows": len(df),
            "columns": list(df.columns),
            "excel_base64": excel_base64
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()
