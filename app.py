import base64
import io
import os
import pandas as pd
from flask import Flask, request, jsonify, send_file
from tempfile import NamedTemporaryFile

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_csv():
    data = request.get_json()
    if not data or 'csv_base64' not in data:
        return jsonify({'error': 'Nenhum CSV enviado'}), 400

    try:
        # Decodificar CSV
        csv_bytes = base64.b64decode(data['csv_base64'])
        csv_file = io.BytesIO(csv_bytes)

        # Criar arquivo Excel temporário
        with NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp_excel:
            output_excel_path = tmp_excel.name

        # Criar primeira parte do Excel
        first_chunk = True
        for chunk in pd.read_csv(csv_file, chunksize=1000):
            with pd.ExcelWriter(output_excel_path, engine='openpyxl', mode='a' if not first_chunk else 'w') as writer:
                chunk.to_excel(writer, sheet_name='Dados', index=False, header=first_chunk, startrow=writer.sheets['Dados'].max_row if not first_chunk else 0)
            first_chunk = False

        # Enviar como resposta
        with open(output_excel_path, 'rb') as f:
            excel_data = f.read()

        os.remove(output_excel_path)

        return send_file(
            io.BytesIO(excel_data),
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='arquivo.xlsx'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500
