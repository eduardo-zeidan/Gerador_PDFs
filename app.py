# app.py

from flask import Flask, render_template, send_file, abort, jsonify
import pdf_gerador1
import pdf_gerador2
import pdf_gerador3
import os
import logging

app = Flask(__name__)

# Configurar o logging para o Flask
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Pasta onde os PDFs serão salvos
OUTPUT_FOLDER = "outputs"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

# Endpoint para gerar PDF 1 via AJAX
@app.route('/api/gerar_pdf1', methods=['POST'])
def api_gerar_pdf1():
    try:
        output_file = os.path.join(OUTPUT_FOLDER, "analise_dispersao.pdf")
        pdf_gerador1.gerar_pdf_analise_dispersao(output_file)
        if not os.path.exists(output_file):
            logging.error("O arquivo PDF de Análise de Dispersão não foi gerado.")
            return jsonify({'status': 'error', 'message': 'Erro ao gerar o PDF de Análise de Dispersão.'}), 500
        return jsonify({'status': 'success', 'file_path': output_file}), 200
    except Exception as e:
        logging.error(f"Erro ao gerar PDF 1: {e}")
        return jsonify({'status': 'error', 'message': 'Erro ao gerar o PDF de Análise de Dispersão.'}), 500

# Endpoint para gerar PDF 2 via AJAX
@app.route('/api/gerar_pdf2', methods=['POST'])
def api_gerar_pdf2():
    try:
        output_file = os.path.join(OUTPUT_FOLDER, "analise_zscore.pdf")
        pdf_gerador2.gerar_pdf(output_file)
        if not os.path.exists(output_file):
            logging.error("O arquivo PDF de Análise Z-Score não foi gerado.")
            return jsonify({'status': 'error', 'message': 'Erro ao gerar o PDF de Análise Z-Score.'}), 500
        return jsonify({'status': 'success', 'file_path': output_file}), 200
    except Exception as e:
        logging.error(f"Erro ao gerar PDF 2: {e}")
        return jsonify({'status': 'error', 'message': 'Erro ao gerar o PDF de Análise Z-Score.'}), 500

# Endpoint para gerar PDF 3 via AJAX
@app.route('/api/gerar_pdf3', methods=['POST'])
def api_gerar_pdf3():
    try:
        output_file = os.path.join(OUTPUT_FOLDER, "Variação_Diária.pdf")
        pdf_gerador3.gerar_pdf_variacao_diaria(output_file)
        if not os.path.exists(output_file):
            logging.error("O arquivo PDF de Variação Diária não foi gerado.")
            return jsonify({'status': 'error', 'message': 'Erro ao gerar o PDF de Variação Diária.'}), 500
        return jsonify({'status': 'success', 'file_path': output_file}), 200
    except Exception as e:
        logging.error(f"Erro ao gerar PDF 3: {e}")
        return jsonify({'status': 'error', 'message': 'Erro ao gerar o PDF de Variação Diária.'}), 500

# Endpoint para baixar arquivos PDF
@app.route('/download/<path:filename>')
def download_file(filename):
    try:
        return send_file(filename, as_attachment=True)
    except Exception as e:
        logging.error(f"Erro ao baixar o arquivo {filename}: {e}")
        abort(404, description="Arquivo não encontrado.")

if __name__ == '__main__':
    app.run(debug=True)
