import base64
import io
import pandas as pd
import tempfile
import zipfile
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_csv():
    data = request.get_json()
    file_content = base64.b64decode(data['arquivo'])

    # Usa um arquivo temporário para armazenar o zip
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_zip:
        zip_path = tmp_zip.name

    # Lê o conteúdo em chunks e escreve CSV temporário
    with tempfile.NamedTemporaryFile(mode='w+', suffix=".csv", delete=False, newline='', encoding='utf-8') as tmp_csv:
        csv_path = tmp_csv.name

        # Escreve o cabeçalho e dados em partes
        reader = pd.read_csv(io.BytesIO(file_content), chunksize=5000)
        for i, chunk in enumerate(reader):
            chunk.to_csv(tmp_csv, index=False, header=(i == 0))

    # Compacta o CSV em ZIP
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        zipf.write(csv_path, arcname='resultado.csv')

    # Retorna o ZIP em base64
    with open(zip_path, 'rb') as f:
        zip_base64 = base64.b64encode(f.read()).decode()

    return jsonify({'arquivo_zip_base64': zip_base64})
