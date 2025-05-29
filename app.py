from flask import Flask, request, send_file
import pandas as pd
from openpyxl import load_workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
from io import BytesIO

app = Flask(__name__)

@app.route("/converter", methods=["POST"])
def converter_csv():
    if "file" not in request.files:
        return "Arquivo CSV não enviado", 400

    file = request.files["file"]
    df = pd.read_csv(file)

    # Cria o arquivo Excel na memória
    output = BytesIO()
    df.to_excel(output, index=False, sheet_name="Inventario")
    output.seek(0)

    wb = load_workbook(output)
    ws = wb["Inventario"]

    ref = f"A1:{chr(65 + len(df.columns) - 1)}{len(df) + 1}"
    tabela = Table(displayName="TabelaInventario", ref=ref)
    estilo = TableStyleInfo(name="TableStyleMedium9", showRowStripes=True)
    tabela.tableStyleInfo = estilo
    ws.add_table(tabela)

    final_output = BytesIO()
    wb.save(final_output)
    final_output.seek(0)

    return send_file(
        final_output,
        download_name="Inventario_Com_Tabela.xlsx",
        as_attachment=True,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

if __name__ == "__main__":
    app.run(debug=True)
