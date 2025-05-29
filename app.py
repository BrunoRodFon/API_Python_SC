import base64
import io
import os
import pandas as pd
from flask import Flask, request, jsonify, send_file
from zipfile import ZipFile

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

        # Caminho temporário
        output_excel = 'output.xlsx'
        writer = pd.ExcelWriter(output_excel, engine='openpyxl')

        # Ler e salvar por partes
        chunk_size = 1000
        chunk_iter = pd.read_csv(csv_file, chunksize=chunk_size)

        for i, chunk in enumerate(chunk_iter):
            sheet_name = f'Lote{i + 1}'
            chunk.to_excel(writer, sheet_name=sheet_name, index=False)

        writer.close()

        # Compactar para envio
        zip_buffer = io.BytesIO()
        with ZipFile(zip_buffer, 'w') as zip_file:
            zip_file.write(output_excel, arcname='output.xlsx')

        zip_buffer.seek(0)
        os.remove(output_excel)

        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name='arquivo_excel.zip'
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500
