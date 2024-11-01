#pip install pyopenssl
import os
from flask import Flask, flash, request, redirect, render_template, jsonify
from werkzeug.utils import secure_filename

from pythonProject.WebAppAI import HFinvoicereceipt, SpacyLeavesParser
from pythonProject.WebAppAI import HFQAItalian
#from pythonProject.WebAppAI.HFDocQuery import HFDocQuery

debug = True
UPLOAD_FOLDER = 'D:/temp/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif'}

ALLOWED_EXTENSIONS_CHATBOT = {'pdf'}

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1000 * 1000
app.config['SECRET_KEY'] = '12345'

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def allowed_file_chatbot(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_CHATBOT

@app.route("/")
def def_home():
    message = "This it root"
    return render_template('index.html',
                           message=message)
# Per invio scontrino
@app.route('/sendReceipt', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Controlla id del file part sia wuello ammesso
        if 'receipt-image' not in request.files :
            flash('No file part')
            return redirect(request.url)
        file = request.files['receipt-image']
        # Se l'utente non seleziona nessun file, il browser invia
        # un file vuoto senza nome.
        if file.filename == '':
            flash('Nessun file selezionato')
            return redirect(request.url)
        # Controlla che il file abbia l'estensione ammessa
        if file and allowed_file(file.filename):
            # Controlla che il nome del file abbia caratteri NON validi
            filename = secure_filename(file.filename)
            if (debug) :
                print(filename)
            # Salva il file nella cartella configurata
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Invoca la componente IA Python che incapsula il funzionamento dell'OCR
            jsonresponse = HFinvoicereceipt.readInfo(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if (debug):
                print(jsonresponse)
            return jsonresponse
    return jsonify(error='Metodo request non ammesso'), 403

# Invio file per Q&A
@app.route('/sendContext', methods=['GET', 'POST'])
def upload_file_QA():
    if (request.method == 'POST' or request.method == 'GET') :
        # Controlla id del file part sia wuello ammesso
        if 'QA-file' not in request.files :
            flash('No file part')
            data = {
                "filename": "",
                "num_pages": 0,
                "status": "KO",
                "reason": "context_is_missing"
            }
            return jsonify(data)
        file = request.files['QA-file']
        # Se l'utente non seleziona nessun file, il browser invia
        # un file vuoto senza nome.
        if file.filename == '':
            flash('Nessun file selezionato')
            data = {
                "filename": "",
                "num_pages": 0,
                "status": "KO",
                "reason": "context_is_missing"
            }
            return jsonify(data)
        # Controlla che il file abbia l'estensione ammessa
        if file and allowed_file_chatbot(file.filename):
            # Controlla che il nome del file abbia caratteri NON validi
            filename = secure_filename(file.filename)
            if (debug) :
                print(filename)
            # Salva il file nella cartella configurata
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Invoca la componente IA Python che incapsula il funzionamento dell'OCR
            jsonresponse = HFQAItalian.prepare_context_for_question(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            if (debug):
                print(jsonresponse)
            return jsonresponse
        else:
            data = {
                "filename": "",
                "num_pages": 0,
                "status": "KO",
                "reason": "extension_not_allowed"
            }
            return jsonify(data)

    return jsonify(error='Metodo request non ammesso'), 403

# Invio domanda per Q&A
@app.route('/answerQuestion', methods=['GET', 'POST'])
def answer_question():
    if request.method == 'GET':
            question = request.args.get('QA-question')
            print(question)
            jsonresponse = HFQAItalian.ask_for_question(question)
            if (debug):
                print(jsonresponse)
            return jsonresponse
    return jsonify(error='Metodo request non ammesso'), 403

# Invio comando
@app.route('/analyzeCommand', methods=['GET', 'POST'])
def analyze_command():
    if request.method == 'GET':
            command = request.args.get('command')
            print(command)
            jsonresponse = SpacyLeavesParser.readInfo(command)
            if (debug):
                print(jsonresponse)
            return jsonresponse
    return jsonify(error='Metodo request non ammesso'), 403


@app.route("/<template>")
def def_template(template):
    message = "This template redirect"
    return render_template(f'{template}.html',message=message)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True, ssl_context='adhoc')
