# app.py
import os
import base64
import uuid
import pandas as pd
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Pastas para salvar arquivos temporários
UPLOAD_FOLDER = "temp_uploads"
RESULT_FOLDER = "temp_results"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

@app.route("/start-job", methods=["POST"])
def start_job():
    data = request.get_json()

    if not data or "csv_base64" not in data:
        return jsonify({"error": "Campo 'csv_base64' ausente"}), 400

    try:
        job_id = str(uuid.uuid4())
        filename = f"{secure_filename(job_id)}.csv"
        filepath = os.path.join(UPLOAD_FOLDER, filename)

        # Decodifica e salva o CSV
        csv_data = base64.b64decode(data["csv_base64"])
        with open(filepath, "wb") as f:
            f.write(csv_data)

        # Inicia o processamento assíncrono
        process_csv_in_background(job_id, filepath)

        return jsonify({"job_id": job_id}), 202

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/get-job-result", methods=["GET"])
def get_job_result():
    job_id = request.args.get("job_id")
    if not job_id:
        return jsonify({"error": "Parâmetro 'job_id' ausente"}), 400

    xlsx_path = os.path.join(RESULT_FOLDER, f"{secure_filename(job_id)}.xlsx")
    if os.path.exists(xlsx_path):
        return send_file(xlsx_path, as_attachment=True, download_name=f"{job_id}.xlsx")

    return jsonify({"status": "processing"}), 202

def process_csv_in_background(job_id, filepath):
    # Executa em background — simulado por agora como execução síncrona
    try:
        df = pd.read_csv(filepath)
        xlsx_path = os.path.join(RESULT_FOLDER, f"{secure_filename(job_id)}.xlsx")
        df.to_excel(xlsx_path, index=False, engine='openpyxl')
    except Exception as e:
        print(f"[ERRO] Falha no job {job_id}: {e}")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
