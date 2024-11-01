import os
from flask import jsonify
from transformers import BertTokenizerFast, BertForQuestionAnswering
from transformers import pipeline
import re
import PyPDF2

tokenizer = BertTokenizerFast.from_pretrained("osiria/bert-italian-cased-question-answering")
model = BertForQuestionAnswering.from_pretrained("osiria/bert-italian-cased-question-answering")

pipeline_qa = pipeline("question-answering", model=model, tokenizer=tokenizer)

question_context=""
num_pages=0
current_file_name=""


# "Come posso iniziare?"
def readInfo(context,question):
    result=pipeline_qa(context=context,
                  question=question)
    return result

def readInfoFromPDFfile(filename,question):
    text=extract_text(filename=filename)
    text=clean_text(text)
    return readInfo(context=text,question=question)

def clean_text(text):
    # Rimuove sommario, indice, titoli mediante l'uso di regular expressions
    cleaned_text = re.sub(r'Summary:.*?Index:', '', text, flags=re.DOTALL)
    cleaned_text = re.sub(r'Title:.*', '', cleaned_text, flags=re.DOTALL)
    cleaned_text = re.sub(r'Appendix.*', '', cleaned_text, flags=re.DOTALL)
    cleaned_text = re.sub(r'Section.*', '', cleaned_text, flags=re.DOTALL)

    return cleaned_text.strip()

def extract_text(filename):
    global num_pages
    global current_file_name
    # Estrae il nome del file senza estensione
    nome_file = os.path.basename(filename)
    # Estrae solo il nome del file (senza directory o estensione)
    nome_base = os.path.splitext(nome_file)[0]
    current_file_name = nome_base
    # Legge ed estrae testo dal PDF
    pdf_file = open(filename, 'rb')
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    num_pages = len(pdf_reader.pages)
    text = ''
    for page_num in range(num_pages):
        page = pdf_reader.pages[page_num]
        text += page.extract_text()
    return text

def prepare_context_for_question(filename):
    return jsonify(prepare_context_for_question_raw(filename))

def prepare_context_for_question_raw(filename):
    global question_context
    question_context = extract_text(filename)
    question_context = clean_text(question_context)
    print(filename + " " + question_context)
    if (question_context.strip()) :
                data = {
                    "filename": current_file_name,
                    "num_pages": num_pages,
                    "status": "OK",
                    "reason": ""
                }
    else :
                data = {
                    "filename": current_file_name,
                    "num_pages": 0,
                    "status": "KO",
                    "reason": "context_is_missing"
                }
    return data

def ask_for_question(question):
    return jsonify(ask_for_question_raw(question))
def ask_for_question_raw(question):
    global  question_context
    answer=readInfo(question_context,question)
    if (len(answer)>0):
        data = {
            "question": question,
            "answer": answer,
            "status": "OK",
            "reason": ""
        }
    else:
        data = {
            "question": question,
            "answer": "",
            "status": "KO",
            "reason": "no_empty_text"
        }
    return data

def unitTest():

    prepare_context_for_question_raw("D:/Universita/Dispense/Tesi_Materiale/Manuale_duso_esempio.pdf")
    print(ask_for_question_raw("A cosa serve il Software per Gestione Spese e OCR Scontrini?"))
    print(ask_for_question_raw("Quali sono i formati accettati?"))
    print(ask_for_question_raw("Su quali sistemi operativi può essere installato?"))
    print(ask_for_question_raw("Come protegge le sessioni?"))

if __name__ == '__main__':
    unitTest()