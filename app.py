from flask import Flask, request, jsonify
import pandas as pd
import base64
from io import BytesIO

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_csv():
    # Verifica se o request tem JSON válido
    if not request.is_json:
        return jsonify({'error': 'Requisição deve ser JSON'}), 400
    
    data = request.get_json()

    if 'csv_base64' not in data:
        return jsonify({'error': 'Nenhum CSV enviado'}), 400

    try:
        # Decodifica o CSV base64 para bytes
        csv_bytes = base64.b64decode(data['csv_base64'])
        csv_buffer = BytesIO(csv_bytes)

        max_rows = 1000  # Limite de linhas para teste

        # Lê somente as primeiras max_rows linhas do CSV
        df = pd.read_csv(csv_buffer, nrows=max_rows)

        # Cria um Excel em memória
        output_excel = BytesIO()
        with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Dados Limitados')

        output_excel.seek(0)

        # Codifica o Excel em base64 para retorno
        excel_base64 = base64.b64encode(output_excel.read()).decode('utf-8')

        return jsonify({'excel_base64': excel_base64})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Para rodar localmente, pode usar debug=True e host='0.0.0.0' se quiser acessar externamente
    app.run(debug=True, host='0.0.0.0')
