<h1 align="left">Web App IA </h1>

###

<p align="left">Questo repository è collegato al progetto software per la tesi di laurea del corso L31 di Vincenzo Amoruso dell'AA 2024/25 della <b>Università Telematica Unipegaso</b> </p>
<p align="left">Corso di laurea in :<b>Informatica per le aziende digitali L-31</b> </p>
<p align="left">Relatore :<b>Prof. Stefano D&apos;Urso</b> </p>
<p align="left">Insegnamento di :<b>&quot;Tecnologie Web&quot;</b></p>
<p align="left">Titolo della tesi : <b>&quot;Intelligenza Artificiale e sue applicazioni in informatica gestionale&quot;</b></p>
<p align="left">Obiettivo: <b>Il progetto applica con esempi pratici al software gestionale alcune delle potenzialità della intelligenza artificiale.</b></p>

## Preparazione ambiente server Python

### Installare Python scaricabile dall'link 
    https://www.python.org/ftp/python/3.10.4/python-3.10.4-amd64.exe
### Creazione ambiente virtuale Python del server con il comando
    python -m venv D:\User\vincw\WebAppAI
### Attivazione ambiente virtuale 
    D:\Users\vincw\WebAppAI\venv\Scripts\activate 
### Nell'ambiente virtuale (venv) D:\Users\vincw\WebAppAI  eseguire il comando per installare tutti i pacchetti necessari
    pip install requirements.txt 
### Nell'ambiente virtuale (venv) D:\Users\vincw\WebAppAI  eseguire il comando per installare il pacchetto per l'uso del protocollo https
    pip install pyopenssl 
### Nell'ambiente virtuale (venv) D:\Users\vincw\WebAppAI  eseguire il comando per installare il modello spaCy
    python -m spacy download en_core_web_md
### Per avviare il web server Flask eseguire il comando
````
  python.exe D:\Users\vincw\WebAppAI\IAWebAppFlaskServer.py
````

## Screenshots di test

### Applicazione IA con OCR per riconoscimento uno scontrino fiscale
    
<table>
<tr>
<td><img src="https://github.com/vamoruso/WebAppAI/blob/main/screenshots/OCR/OCR_screen_1_1.png" style="width: 50%; height: 50%" /> </td>
<td><img src="https://github.com/vamoruso/WebAppAI/blob/main/screenshots/OCR/OCR_screen_1.png" style="width: 50%; height: 50%" /> </td>
<td><img src="https://github.com/vamoruso/WebAppAI/blob/main/screenshots/OCR/OCR_screen_2.png" style="width: 50%; height: 50%" /> </td>
<td><img src="https://github.com/vamoruso/WebAppAI/blob/main/screenshots/OCR/OCR_screen_3.png" style="width: 50%; height: 50%" /> </td>
</tr>  
</table>
    
### Applicazione pratica di IA con analisi del testo di un manuale pdf

<table>
   <tr>
    <td><img src="https://github.com/vamoruso/WebAppAI/blob/main/screenshots/Chatbot/Chatbot_screen1.png" style="width: 50%; height: 50%"/> </td>
    <td><img src="https://github.com/vamoruso/WebAppAI/blob/main/screenshots/Chatbot/Chatbot_screen2.png" style="width: 50%; height: 50%"/> </td>
    <td><img src="https://github.com/vamoruso/WebAppAI/blob/main/screenshots/Chatbot/Chatbot_screen3.png" style="width: 50%; height: 50%"/> </td>
    <td><img src="https://github.com/vamoruso/WebAppAI/blob/main/screenshots/Chatbot/Chatbot_screen4.png" style="width: 50%; height: 50%"/> </td>
    <td><img src="https://github.com/vamoruso/WebAppAI/blob/main/screenshots/Chatbot/Chatbot_screen5.png" style="width: 50%; height: 50%"/> </td>
   </tr>
</table>  
    
### Applicazione IA di WebSpeech API ed analisi NLP con Spacy

<table>
<tr>
<td><img src="https://github.com/vamoruso/WebAppAI/blob/main/screenshots/absences_vocal_command/AssenzeDaComandoVocale_screen1.png" style="width: 50%; height: 50%"/> </td>
<td><img src="https://github.com/vamoruso/WebAppAI/blob/main/screenshots/absences_vocal_command/AssenzeDaComandoVocale_screen2.png" style="width: 50%; height: 50%"/> </td>
<td><img src="https://github.com/vamoruso/WebAppAI/blob/main/screenshots/absences_vocal_command/AssenzeDaComandoVocale_screen3.png" style="width: 50%; height: 50%"/> </td>
<td><img src="https://github.com/vamoruso/WebAppAI/blob/main/screenshots/absences_vocal_command/AssenzeDaComandoVocale_screen4.png" style="width: 50%; height: 50%"/> </td>
<td><img src="https://github.com/vamoruso/WebAppAI/blob/main/screenshots/absences_vocal_command/AssenzeDaComandoVocale_screen5.png" style="width: 50%; height: 50%"/> </td>  
</tr>  
</table>   

###

<h2 align="left">Vincenzo Amoruso <cite>2024</cite></h2>

###

<h2 align="left">Il progetto utilizza le seguenti tecnologie</h2>

###

<div align="left">
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/html5/html5-original.svg" height="40" alt="html5 logo"  />
  <img width="12" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/css3/css3-original.svg" height="40" alt="jquery logo"  />
  <img width="12" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/bootstrap/bootstrap-original.svg" height="40" alt="bootstrap logo"  />
  <img width="12" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/javascript/javascript-original.svg" height="40" alt="javascript logo"  />
  <img width="12" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/jquery/jquery-original.svg" height="40" alt="jquery logo"  />
  <img width="12" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/handlebars/handlebars-original.svg" height="40" alt="handlebars logo"  />
  <img width="12" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/flask/flask-original.svg" height="40" alt="flask logo"  />
  <img width="12" />
  <img src="https://cdn.jsdelivr.net/gh/devicons/devicon/icons/python/python-original.svg" height="40" alt="python logo"  />
</div>

###
