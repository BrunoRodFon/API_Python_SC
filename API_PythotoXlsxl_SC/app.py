from flask import Flask, request, send_file
import pandas as pd
from openpyxl import load_workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
import tempfile

app = Flask(__name__)

@app.route("/convert", methods=["POST"])
def convert():
    if 'file' not in request.files:
        return {"error": "No file uploaded"}, 400

    file = request.files['file']
    df = pd.read_csv(file)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        excel_path = tmp.name
        df.to_excel(excel_path, index=False, sheet_name='Inventário')

        wb = load_workbook(excel_path)
        ws = wb.active
        table = Table(displayName="TabelaInventario", ref=ws.dimensions)
        style = TableStyleInfo(name="TableStyleMedium9", showRowStripes=True)
        table.tableStyleInfo = style
        ws.add_table(table)
        wb.save(excel_path)

        return send_file(excel_path, as_attachment=True, download_name="Inventario.xlsx")
