import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from PIL import Image

app = Flask(__name__)

# --- CONFIGURAÇÃO DA CHAVE ---
CHAVE_API_GOOGLE = os.getenv("CHAVE_API_GOOGLE")
if CHAVE_API_GOOGLE:
    genai.configure(api_key=CHAVE_API_GOOGLE)

@app.route('/')
def home():
    return render_template('index.html')

# --- ROTA 1: CHAT (USANDO O MODELO CLÁSSICO) ---
@app.route('/api/lash_chat', methods=['POST'])
def lash_chat():
    try:
        dados = request.json
        msg = dados.get('msg', '')
        
        # TROCAMOS O 'flash' PELO 'gemini-pro' (QUE FUNCIONA EM TUDO)
        model = genai.GenerativeModel("gemini-pro")
        
        prompt = f"Aja como Mentora Lash. Responda curto e com carinho: {msg}"
        response = model.generate_content(prompt)
        return jsonify({'resposta': response.text})
    except Exception as e:
        print(f"❌ ERRO CHAT: {e}")
        return jsonify({'resposta': "Amiga, tenta de novo? A conexão oscilou! ✨"})

# --- ROTA 2: VISÃO (USANDO O MODELO CLÁSSICO DE VISÃO) ---
@app.route('/api/lash_vision', methods=['POST'])
def visagismo():
    if 'imagem' not in request.files: return jsonify({"resposta": "Cadê a foto?"}), 400
    arquivo = request.files['imagem']
    if arquivo.filename == '': return jsonify({"resposta": "Sem foto."}), 400

    try:
        img = Image.open(arquivo.stream)
        if img.mode != 'RGB': img = img.convert('RGB')
        img.thumbnail((1024, 1024))

        # TROCAMOS O 'flash' PELO 'gemini-pro-vision' (ESPECÍFICO PARA FOTOS ANTIGO)
        model = genai.GenerativeModel('gemini-pro-vision')
        
        prompt = """
        Atue como Lash Designer. Analise este olho.
        Responda neste formato:
        FORMATO: [Ex: Amendoado]
        MAPPING: [Ex: Gatinho]
        DICA: [Breve explicação]
        """
        
        response = model.generate_content([prompt, img])
        return jsonify({"resposta": response.text})

    except Exception as e:
        print(f"❌ ERRO VISION: {e}")
        return jsonify({"resposta": "O servidor não conseguiu ler a foto. Tente outra! 🙏"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
