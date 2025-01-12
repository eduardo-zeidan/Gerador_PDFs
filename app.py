# app.py

from flask import Flask, render_template, send_file
import pdf_gerador1
import pdf_gerador2
import pdf_gerador3
import os

app = Flask(__name__)

# Pasta onde os PDFs serão salvos
OUTPUT_FOLDER = "outputs"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/gerar_pdf1')
def gerar_pdf1():
    output_file = os.path.join(OUTPUT_FOLDER, "analise_dispersao.pdf")
    pdf_gerador1.gerar_pdf_analise_dispersao(output_file)  # Passa o caminho do arquivo
    return send_file(output_file, as_attachment=True)

@app.route('/gerar_pdf2')
def gerar_pdf2():
    output_file = os.path.join(OUTPUT_FOLDER, "analise_zscore.pdf")
    pdf_gerador2.gerar_pdf(output_file)
    return send_file(output_file, as_attachment=True)

@app.route('/gerar_pdf3')
def gerar_pdf3():
    output_file = os.path.join(OUTPUT_FOLDER, "regressao_pares_ativos.pdf")
    pdf_gerador3.gerar_pdf(output_file)
    return send_file(output_file, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
