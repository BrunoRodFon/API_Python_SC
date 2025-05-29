from flask import Flask, request, send_file
import pandas as pd
import io

app = Flask(__name__)

@app.route("/")
def home():
    return "API de Conversão de CSV para Excel com Tabela está ativa!"

@app.route("/conversor", methods=["POST"])
def converter_csv_para_excel():
    if 'file' not in request.files:
        return "Arquivo CSV não encontrado na requisição", 400

    file = request.files['file']

    try:
        # Lê o CSV em um DataFrame
        df = pd.read_csv(file)

        # Cria um arquivo Excel em memória
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Planilha1', index=False)

            # Formatar como tabela (opcional, pode ser detalhado depois)

        output.seek(0)

        return send_file(
            output,
            download_name="arquivo_convertido.xlsx",
            as_attachment=True,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

    except Exception as e:
        return f"Erro ao processar o arquivo: {str(e)}", 500
