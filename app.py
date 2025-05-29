from flask import Flask, request, send_file, jsonify
import pandas as pd
import io
import base64
import zipfile
import os
import uuid

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_csv():
    try:
        data = request.get_json()
        if not data or 'file' not in data:
            return jsonify({'error': 'Nenhum arquivo enviado'}), 400

        # Decode base64
        csv_data = base64.b64decode(data['file'])
        csv_buffer = io.BytesIO(csv_data)

        # Read CSV into pandas DataFrame
        df = pd.read_csv(csv_buffer)

        # Criar Excel com estilo de TABELA
        output_excel = io.BytesIO()
        with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Dados')
            workbook = writer.book
            worksheet = writer.sheets['Dados']
            max_row = df.shape[0] + 1
            max_col = df.shape[1]
            col_letter = chr(64 + max_col) if max_col <= 26 else 'Z'
            table_range = f"A1:{col_letter}{max_row}"

            from openpyxl.worksheet.table import Table, TableStyleInfo
            tab = Table(displayName="Tabela1", ref=table_range)
            style = TableStyleInfo(name="TableStyleMedium9", showFirstColumn=False,
                                   showLastColumn=False, showRowStripes=True, showColumnStripes=False)
            tab.tableStyleInfo = style
            worksheet.add_table(tab)

        # Voltar para o início do buffer
        output_excel.seek(0)

        # Criar um ZIP com o Excel dentro
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr('arquivo_convertido.xlsx', output_excel.read())
        zip_buffer.seek(0)

        return send_file(
            zip_buffer,
            mimetype='application/zip',
            as_attachment=True,
            download_name='convertido.zip'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
