from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import PIL.Image
import os

app = Flask(__name__)

# --- CONFIGURAÇÃO BLINDADA ---
# 1. Tenta pegar a chave do servidor (Render/Heroku)
CHAVE_API_GOOGLE = os.getenv("CHAVE_API_GOOGLE") 

# 2. Se não achar (ou seja, se estiver no seu PC), usa essa fixa:
if not CHAVE_API_GOOGLE:
    CHAVE_API_GOOGLE = "AIzaSyCwS-qwEmr8ZnMIYIKaWkHcmCTR9qKAf2k"

genai.configure(api_key=CHAVE_API_GOOGLE)

# --- AUTO-DETECÇÃO INTELIGENTE ---
nome_modelo_atual = "gemini-1.5-flash" 
try:
    # print("🔍 Configurando IA...") # Comentei para limpar o terminal
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            if 'flash' in m.name:
                nome_modelo_atual = m.name
                break
except Exception as e:
    print(f"⚠️ Aviso: Usando padrão. Detalhe: {e}")

model = genai.GenerativeModel(nome_modelo_atual)

@app.route('/')
def home():
    return render_template('index.html')

# --- CHAT ---
@app.route('/api/lash_chat', methods=['POST'])
def lash_chat():
    msg = request.json.get('msg')
    prompt = f"Aja como LASH HELPER, sócia da Ana Clara. Responda curto e com emojis: {msg}"
    try:
        response = model.generate_content(prompt)
        return jsonify({'resposta': response.text})
    except Exception as e:
        print(f"Erro Chat: {e}")
        return jsonify({'resposta': "Amiga, a conexão com a IA oscilou. Tente de novo! ✨"})

# --- VISAGISMO ---
@app.route('/api/lash_vision', methods=['POST'])
def lash_vision():
    if 'imagem' not in request.files: return jsonify({'resposta': "Cadê a foto? 📸"})
    
    try:
        img = PIL.Image.open(request.files['imagem'])
        prompt = "Analise esse olho para extensão de cílios. Diga: 1. Formato 2. Mapping Ideal. Seja breve."
        
        response = model.generate_content([prompt, img])
        return jsonify({'resposta': response.text})
    except Exception as e:
        print(f"Erro Vision: {e}")
        return jsonify({'resposta': "⚠️ Não consegui ver a foto. Tente outra!"})

if __name__ == '__main__':
    # O servidor usa o Gunicorn, então ele ignora isso.
    # O seu PC usa isso para rodar.
    app.run(host='0.0.0.0', port=5000, debug=True)