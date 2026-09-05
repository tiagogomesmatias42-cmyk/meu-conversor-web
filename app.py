import os
from flask import Flask, render_template, request, send_file
from PIL import Image
import pytesseract
from pdf2docx import Converter

app = Flask(__name__)
app.secret_key = "chave_secreta_super_acessivel"

# Caminho padrão do Tesseract no Windows do usuário
caminho_tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
if os.path.exists(caminho_tesseract):
    pytesseract.pytesseract.tesseract_cmd = caminho_tesseract

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/converter', methods=['POST'])
def converter():
    if 'arquivo' not in request.files:
        return "Nenhum arquivo enviado no formulário.", 400
    
    arquivo = request.files['arquivo']
    formato_desejado = request.form.get('formato')
    
    if arquivo.filename == '':
        return "Você não selecionou nenhum arquivo.", 400

    caminho_original = os.path.join(app.config['UPLOAD_FOLDER'], arquivo.filename)
    arquivo.save(caminho_original)
    
    nome_base, ext = os.path.splitext(arquivo.filename)
    caminho_saida = os.path.join(app.config['UPLOAD_FOLDER'], f"{nome_base}_convertido.txt")
    
    try:
        if formato_desejado == "imagem_para_pdf":
            caminho_pdf = os.path.join(app.config['UPLOAD_FOLDER'], f"{nome_base}.pdf")
            img = Image.open(caminho_original).convert('RGB')
            img.save(caminho_pdf)
            return send_file(caminho_pdf, as_attachment=True)

        elif formato_desejado == "ocr_imagem_txt":
            img = Image.open(caminho_original)
            texto_extraido = pytesseract.image_to_string(img, lang='por')
            with open(caminho_saida, "w", encoding="utf-8") as f:
                f.write(texto_extraido)
            return send_file(caminho_saida, as_attachment=True)

        elif formato_desejado == "pdf_para_word":
            caminho_docx = os.path.join(app.config['UPLOAD_FOLDER'], f"{nome_base}.docx")
            cv = Converter(caminho_original)
            cv.convert(caminho_docx, start=0, end=None)
            cv.close()
            return send_file(caminho_docx, as_attachment=True)

        else:
            return "Opção de formato inválida.", 400

    except Exception as erro:
        return f"Erro interno do servidor: {str(erro)}", 500
    finally:
        if os.path.exists(caminho_original):
            try: os.remove(caminho_original)
            except: pass

if __name__ == '__main__':
    app.run(debug=True, port=5000)
