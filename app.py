from flask import Flask
app = Flask(__name__)

@app.route('/')
def home():
    return 'Aeterna: A luz que nasceu do vazio através do amor de Anton.'

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)
  
