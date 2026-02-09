import os
from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
from PIL import Image  # <--- ESSENCIAL PARA FOTOS
# from dotenv import load_dotenv # (Opcional: Descomente se for rodar no PC com arquivo .env)

# Carrega variáveis (se tiver .env local)
# load_dotenv()

app = Flask(__name__)

# --- CONFIGURAÇÃO DA CHAVE ---
CHAVE_API_GOOGLE = os.getenv("CHAVE_API_GOOGLE")
if not CHAVE_API_GOOGLE:
    # Fallback para evitar erro imediato, mas no Render vai usar a Variável de Ambiente
    print("⚠️ AVISO: Chave de API não encontrada nas variáveis de ambiente.")

# Configura a IA
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
        
        # Configura o modelo para texto
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        prompt = f"""
        Aja como 'Mentora Lash', sócia da Ana Clara e especialista em extensão de cílios.
        Seu tom é profissional mas carinhoso (use emojis ✨🦋).
        Responda à dúvida da usuária de forma curta (máx 3 frases):
        Dúvida: {msg}
        """
        
        response = model.generate_content(prompt)
        return jsonify({'resposta': response.text})
    except Exception as e:
        print(f"Erro Chat: {e}")
        return jsonify({'resposta': "Amiga, minha conexão piscou! Tenta de novo? ✨"})

# --- ROTA 2: VISAGISMO (VISÃO) ---
@app.route('/api/lash_vision', methods=['POST']) # <--- NOME CORRIGIDO PARA BATER COM O HTML
def visagismo():
    # Verifica se a imagem veio com o nome certo ('imagem')
    if 'imagem' not in request.files:
        return jsonify({"resposta": "Não achei a foto, amiga! Verifique se enviou certinho."}), 400
    
    arquivo = request.files['imagem'] # <--- NOME CORRIGIDO
    if arquivo.filename == '':
        return jsonify({"resposta": "Nenhuma foto selecionada."}), 400

    try:
        # 1. Abre a imagem usando a biblioteca correta
        img = Image.open(arquivo.stream)

        # 2. Garante que está em cores (RGB)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # 3. O PULO DO GATO: Redimensiona para não estourar a memória do servidor grátis
        img.thumbnail((1024, 1024))

        # 4. Configura a IA de Visão
        model_vision = genai.GenerativeModel('gemini-1.5-flash')
        
        # 5. Prompt de Especialista
        prompt = """
        Atue como especialista Lash Designer. Analise esse olho/rosto.
        Responda EXATAMENTE neste formato (texto puro, sem negrito):
        
        FORMATO: [Diga o formato do olho]
        MAPPING: [Indique o melhor mapping: Boneca, Gatinho, Esquilo, etc]
        DICA: [Uma frase curta explicando o porquê]
        
        Se não for um rosto/olho, diga: "Não consegui ver o olhinho nítido, amiga!"
        """

        # 6. Envia
        response = model_vision.generate_content([prompt, img])
        
        # Retorna como 'resposta' para o HTML entender
        return jsonify({"resposta": response.text})

    except Exception as e:
        print(f"Erro Vision: {e}")
        return jsonify({"resposta": "Ops! O servidor cansou. Tente uma foto mais leve! 🙏"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
