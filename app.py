import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from PIL import Image  # <--- CORREÇÃO 1: Importação essencial para fotos

app = Flask(__name__)

# --- CONFIGURAÇÃO DA CHAVE ---
CHAVE_API_GOOGLE = os.getenv("CHAVE_API_GOOGLE")
if not CHAVE_API_GOOGLE:
    print("⚠️ AVISO: Chave de API não encontrada (ok se estiver rodando localmente sem env)")

if CHAVE_API_GOOGLE:
    genai.configure(api_key=CHAVE_API_GOOGLE)

# --- ROTAS ---

@app.route('/')
def home():
    return render_template('index.html')

# --- ROTA 1: CHAT DA MENTORA ---
@app.route('/api/lash_chat', methods=['POST'])
def lash_chat():
    try:
        dados = request.json
        msg = dados.get('msg', '')
        
        # Usa o modelo Flash que é mais rápido e barato
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
        Aja como 'Mentora Lash', sócia da Ana Clara e especialista em extensão de cílios.
        Seu tom é profissional mas carinhoso (use emojis ✨🦋).
        Responda à dúvida de forma curta e direta (máx 3 frases).
        Dúvida: {msg}
        """
        
        response = model.generate_content(prompt)
        return jsonify({'resposta': response.text})
    except Exception as e:
        print(f"Erro Chat: {e}")
        return jsonify({'resposta': "Amiga, a conexão piscou! Tenta de novo? ✨"})

# --- ROTA 2: VISAGISMO (CORRIGIDA) ---
@app.route('/api/lash_vision', methods=['POST']) # <--- CORREÇÃO 2: Nome da rota igual ao HTML
def visagismo():
    # <--- CORREÇÃO 3: Procura por 'imagem' em vez de 'foto'
    if 'imagem' not in request.files:
        return jsonify({"resposta": "Não achei a foto, amiga! Tente novamente."}), 400
    
    arquivo = request.files['imagem']
    if arquivo.filename == '':
        return jsonify({"resposta": "Nenhuma foto selecionada."}), 400

    try:
        # 1. Abre a imagem corretamente
        img = Image.open(arquivo.stream)

        # 2. Garante que está em cores (RGB)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # 3. REDIMENSIONA (Essencial para o servidor grátis não travar)
        img.thumbnail((1024, 1024))

        # 4. Configura a IA
        model_vision = genai.GenerativeModel('gemini-1.5-flash')
        
        # 5. Prompt Especialista
        prompt = """
        Atue como especialista Lash Designer. Analise esse olho/rosto.
        Responda EXATAMENTE neste formato (sem negrito):
        
        FORMATO: [Formato do olho]
        MAPPING: [Melhor mapping: Boneca, Gatinho, Esquilo, etc]
        DICA: [Uma frase curta explicando o porquê]
        
        Se não for um olho, diga: "Não consegui ver o olhinho nítido, amiga!"
        """

        response = model_vision.generate_content([prompt, img])
        return jsonify({"resposta": response.text})

    except Exception as e:
        print(f"Erro Vision: {e}")
        return jsonify({"resposta": "O servidor cansou. Tente uma foto mais leve! 🙏"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
