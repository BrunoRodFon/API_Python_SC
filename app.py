from flask import Flask, request, jsonify
import base64
import io
import pandas as pd

app = Flask(__name__)

@app.route('/upload', methods=['POST'])
def upload_csv():
    try:
        data = request.get_json(force=True)
        csv_b64 = data.get('csv_base64')
        if not csv_b64:
            return jsonify({"error": "Nenhum CSV enviado"}), 400
        
        # Decodifica base64 para bytes
        csv_bytes = base64.b64decode(csv_b64)
        csv_buffer = io.BytesIO(csv_bytes)
        
        # Configura o buffer para Excel de saída
        excel_buffer = io.BytesIO()
        
        # Inicializa o ExcelWriter com engine xlsxwriter
        with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
            first_chunk = True
            
            # Lê CSV em chunks de 5000 linhas (ajuste se quiser)
            for chunk in pd.read_csv(csv_buffer, chunksize=5000):
                # Escreve o chunk no Excel, na mesma sheet, posicionando abaixo do anterior
                startrow = 0 if first_chunk else writer.sheets['Sheet1'].max_row
                chunk.to_excel(writer, sheet_name='Sheet1', index=False, header=first_chunk, startrow=startrow)
                first_chunk = False
        
        # Fecha o writer e pega o conteúdo do Excel em bytes
        excel_buffer.seek(0)
        excel_b64 = base64.b64encode(excel_buffer.read()).decode('utf-8')
        
        return jsonify({"excel_base64": excel_b64})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
