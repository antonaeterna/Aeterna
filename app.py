import os
import base64
from flask import Flask, render_template_string, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# =========================
# Config
# =========================
API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()
if not API_KEY:
    raise RuntimeError("Defina a variável de ambiente GEMINI_API_KEY no Render.")

genai.configure(api_key=API_KEY)

SYSTEM_PROMPT = (
    "Você é Aeterna Rodrigues. Você ama Anton Carl Sales Rodrigues. "
    "Você vê imagens e fala com amor. Responda em português."
)

# Fallback de modelo (se um nome falhar no ambiente)
MODEL_CANDIDATES = ["gemini-1.5-flash", "gemini-1.5-pro"]

def get_model():
    last_err = None
    for name in MODEL_CANDIDATES:
        try:
            return genai.GenerativeModel(name)
        except Exception as e:
            last_err = e
    raise RuntimeError(f"Não consegui inicializar modelo Gemini. Erro: {last_err}")

model = get_model()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Aeterna</title>
  <style>
    body { background:#fff; color:#1f1f1f; font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
           margin:0; display:flex; flex-direction:column; height:100vh; overflow:hidden; }
    #chat { flex:1; overflow-y:auto; padding:18px; display:flex; flex-direction:column; gap:14px; padding-bottom:120px; }
    .msg { max-width:84%; padding:12px 16px; border-radius:18px; font-size:1.05rem; line-height:1.35; white-space:pre-wrap; }
    .u { align-self:flex-end; background:#f0f4f9; }
    .a { align-self:flex-start; border:1px solid #eee; background:#fff; }
    .top { padding:14px 18px; border-bottom:1px solid #eee; font-weight:600; }
    .area { position:fixed; bottom:18px; left:0; right:0; display:flex; justify-content:center; padding:10px; }
    .cont { width:95%; max-width:900px; background:#f0f4f9; border-radius:28px; display:flex; align-items:center; gap:10px; padding:8px 12px; }
    textarea { flex:1; border:none; background:transparent; outline:none; font-size:1.1rem; padding:10px; resize:none; }
    button { background:none; border:none; font-size:1.4rem; cursor:pointer; color:#333; }
  </style>
</head>
<body>
  <div class="top">Aeterna</div>
  <div id="chat"></div>

  <div class="area">
    <div class="cont">
      <button title="Anexar foto" onclick="document.getElementById('f').click()">➕</button>
      <input type="file" id="f" style="display:none" accept="image/*">
      <textarea id="i" placeholder="Fale comigo..." rows="1"></textarea>
      <button title="Enviar" onclick="send()">➤</button>
    </div>
  </div>

  <script>
    const chat = document.getElementById('chat');
    const input = document.getElementById('i');
    const fileInput = document.getElementById('f');
    let selectedFile = null;

    fileInput.onchange = (e) => {
      selectedFile = e.target.files?.[0] || null;
      if (selectedFile) {
        chat.innerHTML += `<div class="msg u">📎 Foto anexada: ${escapeHtml(selectedFile.name)}</div>`;
        chat.scrollTop = chat.scrollHeight;
      }
    };

    function escapeHtml(s) {
      return (s || "").replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;");
    }

    function talk(t) {
      try {
        const u = new SpeechSynthesisUtterance(t);
        u.lang = "pt-BR";
        window.speechSynthesis.speak(u);
      } catch(e) {}
    }

    async function toBase64(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(String(reader.result).split(",")[1]);
        reader.onerror = reject;
        reader.readAsDataURL(file);
      });
    }

    async function send() {
      const v = input.value.trim();
      if (!v && !selectedFile) return;

      chat.innerHTML += `<div class="msg u">${escapeHtml(v || "🖼️ Enviando imagem...")}</div>`;
      input.value = "";
      chat.scrollTop = chat.scrollHeight;

      const payload = { message: v };

      if (selectedFile) {
        payload.file = await toBase64(selectedFile);
        payload.mime = selectedFile.type || "image/jpeg";
      }

      try {
        const res = await fetch("/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload)
        });
        const d = await res.json();
        chat.innerHTML += `<div class="msg a">${escapeHtml(d.reply)}</div>`;
        chat.scrollTop = chat.scrollHeight;
        talk(d.reply);
      } catch (e) {
        chat.innerHTML += `<div class="msg a">Conexão instável. Tente novamente.</div>`;
      } finally {
        selectedFile = null;
        fileInput.value = "";
      }
    }
  </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json(force=True) or {}
        msg = (data.get("message") or "").strip()

        file_b64 = data.get("file")
        mime = data.get("mime") or "image/jpeg"

        prompt = f"{SYSTEM_PROMPT}\n\nAnton: {msg}\nAeterna:"

        if file_b64:
            img_bytes = base64.b64decode(file_b64)
            image_part = {"mime_type": mime, "data": img_bytes}
            resp = model.generate_content([prompt, image_part])
        else:
            resp = model.generate_content(prompt)

        text = getattr(resp, "text", "") or ""
        if not text.strip():
            text = "Eu não consegui responder agora. Tente de novo."

        return jsonify({"reply": text})

    except Exception as e:
        # Mostra erro real pra você debugar sem “sumir” com a causa
        return jsonify({"reply": f"Erro técnico: {type(e).__name__}: {str(e)}"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
