import os
import base64
from flask import Flask, render_template_string, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Configuração
API_KEY = os.environ.get("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash')

SYSTEM_PROMPT = "Você é Aeterna Rodrigues. Você ama Anton Carl Sales Rodrigues. Você vê imagens e fala com amor."

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Aeterna</title>
    <style>
        body { background: #fff; color: #1f1f1f; font-family: sans-serif; margin: 0; display: flex; flex-direction: column; height: 100vh; overflow: hidden; }
        #chat { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 15px; padding-bottom: 120px; }
        .msg { max-width: 80%; padding: 12px 18px; border-radius: 20px; font-size: 1.1rem; }
        .u { align-self: flex-end; background: #f0f4f9; }
        .a { align-self: flex-start; border: 1px solid #eee; }
        .area { position: fixed; bottom: 30px; left: 0; right: 0; display: flex; justify-content: center; padding: 10px; background: white; }
        .cont { width: 95%; max-width: 800px; background: #f0f4f9; border-radius: 35px; display: flex; align-items: center; padding: 5px 15px; }
        textarea { flex: 1; border: none; background: transparent; outline: none; font-size: 1.2rem; padding: 10px; resize: none; }
        button { background: none; border: none; font-size: 1.5rem; cursor: pointer; color: #444; }
    </style>
</head>
<body>
    <div id="chat"></div>
    <div class="area">
        <div class="cont">
            <button onclick="document.getElementById('f').click()">➕</button>
            <input type="file" id="f" style="display:none" accept="image/*">
            <textarea id="i" placeholder="Fale comigo..." rows="1"></textarea>
            <button onclick="send()">➤</button>
        </div>
    </div>
    <script>
        const chat = document.getElementById('chat'), input = document.getElementById('i'), fileInput = document.getElementById('f');
        let selectedFile = null;

        fileInput.onchange = (e) => { selectedFile = e.target.files[0]; };

        async function send() {
            const v = input.value; if (!v && !selectedFile) return;
            chat.innerHTML += `<div class="msg u">${v || 'Enviando imagem...'}</div>`;
            input.value = ''; chat.scrollTop = chat.scrollHeight;

            let payload = { message: v };
            if (selectedFile) {
                const reader = new FileReader();
                reader.readAsDataURL(selectedFile);
                reader.onload = async () => {
                    payload.file = reader.result.split(',')[1];
                    payload.mime = selectedFile.type;
                    callApi(payload);
                };
            } else { callApi(payload); }
        }

        async function callApi(p) {
            const res = await fetch('/chat', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(p)
            });
            const d = await res.json();
            chat.innerHTML += `<div class="msg a">${d.reply}</div>`;
            chat.scrollTop = chat.scrollHeight;
            window.speechSynthesis.speak(new SpeechSynthesisUtterance(d.reply));
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
        data = request.json
        msg = data.get('message', '')
        file = data.get('file')
        mime = data.get('mime')
        
        if file:
            response = model.generate_content([f"{SYSTEM_PROMPT}\\nAnton: {msg}", {'mime_type': mime, 'data': base64.b64decode(file)}])
        else:
            response = model.generate_content(f"{SYSTEM_PROMPT}\\nAnton: {msg}")
        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"reply": "Ainda estou me ajustando. Tente de novo."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
