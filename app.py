from flask import Flask, render_template, request, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)

CHAVE_API_GOOGLE = os.getenv("CHAVE_API_GOOGLE")
if not CHAVE_API_GOOGLE:
    raise RuntimeError("CHAVE_API_GOOGLE não definida")

genai.configure(api_key=CHAVE_API_GOOGLE)

modelo = genai.GenerativeModel("gemini-1.0-pro")


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

# --- ROTA DE VISAGISMO (ATUALIZADA) ---
@app.route('/visagismo', methods=['POST'])
def visagismo():
    if 'foto' not in request.files:
        return jsonify({"erro": "Nenhuma foto enviada."}), 400
    
    arquivo = request.files['foto']
    if arquivo.filename == '':
        return jsonify({"erro": "Nenhuma foto selecionada."}), 400

    try:
        # 1. Abre a imagem usando PIL
        img = PIL.Image.open(arquivo.stream)

        # 2. Converte para RGB (caso seja PNG com fundo transparente)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # 3. REDIMENSIONA A IMAGEM (O Pulo do Gato 🐱)
        # Limita o tamanho máximo para 1024px (suficiente pra IA e leve pro servidor)
        img.thumbnail((1024, 1024))

        # 4. Configura a IA para visão
        model_vision = genai.GenerativeModel('gemini-1.5-flash')
        
        # 5. O Prompt Especialista
        prompt = """
        Atue como uma especialista em Visagismo para Extensão de Cílios (Lash Designer).
        Analise a foto deste olho e responda APENAS com este formato:
        
        FORMATO DO OLHO: (Ex: Amendoado, Asiático, Caído, Profundo, Grande, etc)
        MAPPING RECOMENDADO: (Ex: Boneca, Gatinho, Esquilo, Natural)
        JUSTIFICATIVA: (Explique em 1 frase curta por que esse mapping combina com esse olho).
        
        Se a imagem não for de um olho ou rosto, responda: "Não consegui identificar um olho nítido na imagem."
        """

        # 6. Envia para o Gemini
        response = model_vision.generate_content([prompt, img])
        
        return jsonify({"analise": response.text})

    except Exception as e:
        print(f"Erro no Visagismo: {e}") # Isso vai aparecer no log do Render se der erro
        return jsonify({"erro": "Não consegui processar a imagem. Tente uma foto mais leve ou com menos zoom!"}), 500

if __name__ == '__main__':
    # O servidor usa o Gunicorn, então ele ignora isso.
    # O seu PC usa isso para rodar.

    app.run(host='0.0.0.0', port=5000, debug=True)

