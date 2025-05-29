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
        csv_bytes = base64.b64decode(data['csv_base64'])
        csv_buffer = BytesIO(csv_bytes)

        max_rows = 1000
        df = pd.read_csv(csv_buffer, nrows=max_rows)

        output_excel = BytesIO()
        with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Dados Limitados')
        
        output_excel.seek(0)
        excel_base64 = base64.b64encode(output_excel.read()).decode('utf-8').strip()

        return jsonify({'excel_base64': excel_base64})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
