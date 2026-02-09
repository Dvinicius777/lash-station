import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from PIL import Image

app = Flask(__name__)

# --- DIAGNÓSTICO (VAI APARECER NO LOG DO RENDER) ---
print("="*30)
try:
    print(f"🔎 VERSÃO DA BIBLIOTECA: {genai.__version__}")
except:
    print("🔎 VERSÃO DA BIBLIOTECA: Não consegui ler!")
print("="*30)

CHAVE_API_GOOGLE = os.getenv("CHAVE_API_GOOGLE")
if CHAVE_API_GOOGLE:
    genai.configure(api_key=CHAVE_API_GOOGLE)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/lash_chat', methods=['POST'])
def lash_chat():
    try:
        dados = request.json
        msg = dados.get('msg', '')
        
        # TENTATIVA 1: Usa o modelo Flash (Novo)
        # Se der erro, vamos ver no log
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"Aja como Mentora Lash. Responda curto: {msg}"
        response = model.generate_content(prompt)
        return jsonify({'resposta': response.text})
    except Exception as e:
        print(f"❌ ERRO NO CHAT: {e}")
        # TENTATIVA 2: Se o Flash falhar, tenta o Pro (Antigo/Garantido)
        try:
            print("🔄 Tentando modelo antigo (gemini-pro)...")
            model_old = genai.GenerativeModel("gemini-pro")
            response = model_old.generate_content(prompt)
            return jsonify({'resposta': response.text + " (Respondido pelo modelo backup)"})
        except Exception as e2:
            return jsonify({'resposta': f"Erro total: {e} | {e2}"})

@app.route('/api/lash_vision', methods=['POST'])
def visagismo():
    if 'imagem' not in request.files: return jsonify({"resposta": "Cadê a foto?"}), 400
    arquivo = request.files['imagem']
    if arquivo.filename == '': return jsonify({"resposta": "Sem foto."}), 400

    try:
        img = Image.open(arquivo.stream)
        if img.mode != 'RGB': img = img.convert('RGB')
        img.thumbnail((1024, 1024))

        model = genai.GenerativeModel('gemini-1.5-flash')
        
        prompt = "Analise este olho para extensão de cílios. Formato e Mapping recomendado."
        response = model.generate_content([prompt, img])
        return jsonify({"resposta": response.text})

    except Exception as e:
        print(f"❌ ERRO VISION: {e}")
        return jsonify({"resposta": f"Erro técnico: {e}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
