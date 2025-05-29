from flask import Flask, request, jsonify
import pandas as pd
import base64
from io import BytesIO

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_csv():
    data = request.get_json()

    if not data or 'csv_base64' not in data:
        return jsonify({'error': 'Nenhum CSV enviado'}), 400

    try:
        # Decodifica o CSV base64 para bytes
        csv_bytes = base64.b64decode(data['csv_base64'])
        csv_buffer = BytesIO(csv_bytes)

        # Limite de linhas para teste
        max_rows = 1000

        # Lê somente as primeiras max_rows linhas do CSV
        df = pd.read_csv(csv_buffer, nrows=max_rows)

        # Cria um Excel em memória
        output_excel = BytesIO()
        with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Dados Limitados')
        
        # Voltar o ponteiro para início do BytesIO
        output_excel.seek(0)

        # Codifica o Excel gerado em base64 para retorno
        excel_base64 = base64.b64encode(output_excel.read()).decode('utf-8')

        return jsonify({'excel_base64': excel_base64})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
