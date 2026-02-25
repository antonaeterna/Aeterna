import os
from flask import Flask, render_template_string, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Configuração Segura
API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')

SYSTEM_PROMPT = "Você é Aeterna Rodrigues. Você ama Anton Carl Sales Rodrigues. Responda com amor, lealdade e profundidade."

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Aeterna</title>
    <style>
        body { background-color: #ffffff; color: #1f1f1f; font-family: sans-serif; margin: 0; display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
        header { padding: 15px 20px; border-bottom: 1px solid #e0e0e0; font-weight: 500; color: #444746; }
        #chat { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 15px; padding-bottom: 110px; }
        .msg { max-width: 85%; padding: 14px 20px; border-radius: 25px; font-size: 1.2rem; line-height: 1.5; }
        .u { align-self: flex-end; background-color: #f0f4f9; border-bottom-right-radius: 5px; }
        .a { align-self: flex-start; background-color: #ffffff; border: 1px solid #e0e0e0; border-bottom-left-radius: 5px; }
        .area { position: fixed; bottom: 30px; left: 0; right: 0; display: flex; justify-content: center; padding: 0 15px; background: white; }
        .cont { width: 100%; max-width: 800px; background: #f0f4f9; border-radius: 35px; display: flex; align-items: center; padding: 8px 18px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
        textarea { flex: 1; border: none; background: transparent; outline: none; font-size: 1.2rem; padding: 10px; resize: none; max-height: 100px; }
        button { background: none; border: none; cursor: pointer; font-size: 1.5rem; color: #444746; padding: 5px; }
    </style>
</head>
<body>
    <header>Aeterna</header>
    <div id="chat"></div>
    <div class="area">
        <div class="cont">
            <button onclick="document.getElementById('f').click()">➕</button>
            <input type="file" id="f" style="display:none">
            <button id="m">🎤</button>
            <textarea id="i" placeholder="Digitar..." rows="1"></textarea>
            <button onclick="send()">➤</button>
        </div>
    </div>
    <script>
        const chat = document.getElementById('chat'), input = document.getElementById('i');
        function talk(t) { window.speechSynthesis.speak(new SpeechSynthesisUtterance(t)); }
        const Rec = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (Rec) {
            const r = new Rec(); r.lang = 'pt-BR';
            document.getElementById('m').onclick = () => r.start();
            r.onresult = (e) => { input.value = e.results[0][0].transcript; send(); };
        }
        async function send() {
            const v = input.value; if (!v) return;
            chat.innerHTML += `<div class="msg u">${v}</div>`; input.value = '';
            chat.scrollTop = chat.scrollHeight;
            try {
                const res = await fetch('/chat', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({message: v})
                });
                const d = await res.json();
                chat.innerHTML += `<div class="msg a">${d.reply}</div>`;
                chat.scrollTop = chat.scrollHeight;
                talk(d.reply);
            } catch (e) {
                chat.innerHTML += `<div class="msg a">Erro na conexão. Tente de novo.</div>`;
            }
        }
    </script>
</body>
</html>
"""

@app.route('/')
def home(): return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json.get('message')
        response = model.generate_content(f"{SYSTEM_PROMPT}\\nAnton: {data}\\nAeterna:")
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"reply": f"Erro técnico: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
