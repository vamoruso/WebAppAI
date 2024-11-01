#python -m spacy download en_core_web_md
#pip install spacy-langdetect
#pip install spacy dateparser
#pip install word2number
import spacy
import dateparser
from spacy.tokens import Span
from spacy.language import Language
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import re
from word2number import w2n
from datetime import datetime


debug=False

UNDEFINED_ACTION="und"
DEFAULT_ACTION="add"
ALL_DAY_LONG="All day"
# Action List
actions_list=["add","del","delete"]

# Mappa le magic words con le descrizioni delle assenze
leave_reasons_map = {
    ("medical","appointment"): "Medical Appointment",
    ("sick","ill","illness","disease"): "Sick Leave",
    ("family","emergency"):"Family Emergency",
    ("personal", "personal day","day off"):"Personal Day",
    ("vacancy","vacation","vacances","holiday"):"Vacation Leave",
    ("bereavement","die","murder"):"Bereavement Leave",
    ("child","son","care"):"Childcare Responsibilities",
    ("car","bus","train","traffic","transport"): "Car Trouble/Transportation Issues",
    ("jury","duty","judge"):"Jury Duty",
    ("blood","donation"):"Blood Donation"
}
# Mappa le magic verbs con le action da eseguire
actions_map = {
    ("add","insert","got","took","write","register","new"): "add",
    ("delete","remove","erase","cancel","excise","cut out"): "del",
}


# Frasi di esempio per lo unit test
sentences = [
    "Starting from 10-09-2024 to 10-15-2024 i'll be in child care",
    "delete id1",
    "delete row 1",
    "I'm on holiday on the 10th of September's",
    "tomorrow i've got a medical appointment",
    "yesterday i took a day off",
    "today i'm in family emergency",
    "add vacancy for the 10th of September from 9am  until 5 p.m.",
    "add vacancy for the 10th of September from 9 AM  until 5 PM.",
    "Add day off for tomorrow, starting from 9:00 A.M. until 11:00 A.M.",
    "On 10-09-2024 i'll be Sick Leave",
    "today i'm in vacancy",
    "bereavement leave for next three days",
    "jury duty from tomorrow for the next two weeks",
]

# Load the spaCy model
nlp = spacy.load("en_core_web_md")
#nlp = spacy.load("it_core_news_lg")

# Registra la funzione di parsing delle date
Span.set_extension("parsed_date", default=None)
# Custom component estrae date ed orari
@Language.component("date_component")
def date_component(doc):
    for ent in doc.ents:
        if ent.label_ in {"DATE","CARDINAL","TIME"}:
            try:
                parsed_date = dateparser.parse(ent.text)
                if parsed_date:
                    ent._.parsed_date = parsed_date
            except (ValueError, OverflowError):
                ent._.parsed_date = None

    return doc

# Aggiunge il componente alla pipeline
nlp.add_pipe('date_component', after="ner")

# Sostituisce numeri lettere con numeri in cifra. Ci serve per il parsing delle date
def replace_words_with_numbers(text):
    # Regular expression per cercare parole che rappresentano numeri
    number_words_pattern = re.compile(r'\b(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|'
                                      r'eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|'
                                      r'eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|'
                                      r'eighty|ninety|hundred|thousand|million|billion|trillion)\b', re.IGNORECASE)

    def replace_match(match):
        word = match.group(0)
        return str(w2n.word_to_num(word))

    # Sostituisce tutte le parole numeriche trovate con i loro equivalenti numerici
    result = number_words_pattern.sub(replace_match, text)
    return result

# Componente calcola le date con "next 3 days", "until next 1 week", "for 2 weeks", "for 1 month"
def calculate_dates(phrase, today=datetime.today()):

    # Estrae numeri dalla frase
    match = re.search(r'\b\d+(?!st|nd|rd|th)\b', phrase)
    if match:
        number = int(match.group())
    else:
        return None

    if "day" in phrase:
        last_date = today + timedelta(days=number)

    elif "week" in phrase:
        last_date = today + timedelta(days=number * 7)

    elif "month" in phrase:
        last_date = today + relativedelta(months=number)

    else:
        return None

    return last_date

def get_delete_id(phrase):
    phrase=replace_words_with_numbers(phrase)
    # Regex per trovare "id1" o "id 1" o "row 1" o row 1
    pattern = r'\b(?:id|row|ID|ROW|Id|Row)\s?(\d+)\b'
    match = re.search(pattern, phrase)
    if match:
        return match.group(1)  # Restituisce il numero ID trovato
    return None


def extract_reason(text):
    return extract_text(text, leave_reasons_map)

def extract_action(text):
    action = extract_text(text,actions_map)
    if (action is None):
        action=DEFAULT_ACTION
    return action

def extract_text(text,mappa):
    for words, phrase in mappa.items():
        # Crea regex pattern per cercare le parole della mappa
        pattern = r'\b(' + '|'.join(re.escape(word) for word in words) + r')\b'
        if re.search(pattern, text, re.IGNORECASE):
            return phrase
    return None

def extract_date_regexp(text):
    # Regular expression pattern per cercare le date come "10th September"
    date_pattern = r'(\d{1,2})(st|nd|rd|th)?\s*(?:of\s+)?(January|February|March|April|May|June|July|August|September|October|November|December)'

    match = re.search(date_pattern, text)
    if match:
        day = int(match.group(1))
        month = match.group(3)
        # Converte il nome mese in un numero
        #
        month_number = datetime.strptime(month, "%B").month
        # Create a datetime object with the current year
        date = datetime(datetime.today().year, month_number, day)
        return date
    else:
        return None

def replace_am_pm(text):
    # Sostituisci le varianti con punti
    text = text.replace("A.M.", "AM")
    text = text.replace("P.M.", "PM")
    text = text.replace("a.m.", "AM")
    text = text.replace("p.m.", "PM")
    return text

def get_from_to_other(number):
    return "_from" if number == 0 else "_to" if number == 1 else "_"+str(number)

def format_2d(hours_minutes):
    return f"{hours_minutes:02d}"

#Calcola la durata come differenza fra ore
def calculate_duration(start_time, end_time):
    # Converte testo con orari in oggetti datetime
    start = datetime.strptime(start_time, "%H:%M")
    end = datetime.strptime(end_time, "%H:%M")

    # Calcola la differenza
    duration = end - start

    # Estrae ore e minuti dalla durata
    hours, remainder = divmod(duration.seconds, 3600)
    minutes = remainder // 60

    # RiFormatta come HH:MM
    return f"{hours:02}:{minutes:02}"
# Rimuove ore, minuti e second dalla data
def remove_time_from_date(date):
    try:
            date_time_obj = datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f' if '.' in date else '%Y-%m-%d %H:%M:%S')
            # Replace the time part with '00:00:00'
            new_date_time_obj = date_time_obj.replace(hour=0, minute=0, second=0, microsecond=0)
    except ValueError as e:
            if (debug):
                print(remove_time_from_date.__name__ + ' ' + e)
    return new_date_time_obj.strftime('%Y-%m-%d')
# Converte le date in 24 ore.
def convert_to_24_hours(time_str):
    try:
        # Converte ora da formato 12-hour a formato datetime object
        if ':' in time_str and ' ' in time_str:
            time_obj = datetime.strptime(time_str, '%I:%M %p')
        elif ' ' in time_str:
            time_obj = datetime.strptime(time_str, '%I %p')
        else:
            time_obj = datetime.strptime(time_str, '%I%p')
        # Convert the datetime object to a string in 24-hour format
        return time_obj.strftime('%H:%M')
    except ValueError as e:
        if (debug):
                print(convert_to_24_hours.__name__ + ' ' +e)
        return time_str
#Concatena le date  con gli orari estratti dalla frase
def concatenate_date_time(date,time_str):
    try:
        # Converti la stringa di data in un oggetto datetime
        date_time_obj = datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f' if '.' in date else '%Y-%m-%d %H:%M:%S')
        # Combina la data e l'ora in un nuovo formato
        new_date_time_str = date_time_obj.strftime('%Y-%m-%d') + ' ' + time_str
    except ValueError:
            return date
    return new_date_time_str





def readInfo(sentence):
    doc = nlp(sentence)
    print("=================")
    print(sentence)

    absence = {}
    # parse reason
    if (extract_reason(sentence) is not None):
        absence['reason']=extract_reason(sentence);

    # parse action
    for token in doc:
        if token.pos_ == "VERB":
            if debug:
                print(f"Text: {token.text}  VERBO")
            absence['action'] = token.text
        else:
            if debug:
                print(f"Text: {token.text} --> {token.pos_}")
            if token.pos_ == "NOUN" and 'reason' not in absence:
                absence['reason'] = str(token.text)
    # Se NLP non ha trovato l'action manca l'action lo estriamo
    if 'action' not in absence:
        absence['action'] = extract_action(sentence)

    if (absence['action'] not in actions_list):
        absence['action']=DEFAULT_ACTION

    # Se l'azione è una cancellazione cerca di recuperare l'id della riga che si vuole cancellare
    if (absence['action'] == 'del' or absence['action'] == 'delete'):
        id = get_delete_id(sentence)
        if (id is None):
            absence['action'] = UNDEFINED_ACTION
        else:
            absence['id'] = id
    else:
        # Se l'azione non è cancellazione e manca la motivazione della assenza il comando non è valido.
        if ('reason' not in absence):
            absence['action'] = UNDEFINED_ACTION


    # parse date
    date_prog=0
    time_prog = 0
    for ent in doc.ents:
        if (ent.label_ in {"DATE","CARDINAL","TIME"}) and ent._.parsed_date is not None:
            if debug:
                print(f"Text: {ent.text}, Parsed Date: {ent._.parsed_date}")
            if ent.label_ in {"DATE","CARDINAL"}:
                absence['date' + get_from_to_other(date_prog)] = str(ent._.parsed_date)
                date_prog += 1
            elif ent.label_ == "TIME":
                parsed_time = ent._.parsed_date
                if (parsed_time):
                    hours = parsed_time.hour
                    minutes = parsed_time.minute
                    absence['time' + get_from_to_other(time_prog)] = format_2d(hours)+":"+format_2d(minutes)+":00"
                    if (debug):
                        print(absence['time' + get_from_to_other(time_prog)])
                    time_prog += 1

    # Parse degli orari
    try:
        # Regex pattern per cercare orari come  '9:00 AM', '5:00 PM' etc..etc..
        time_pattern = r'\b\d{1,2}(?::\d{2}(?::\d{2}(?:\.\d{1,6})?)?)?\s*(?:AM|PM|am|pm|A\.M\.|P\.M\.|a\.m\.|p\.m\.)?\b(?<![\d\/])'
        time_matches = re.findall(time_pattern, replace_am_pm(sentence))
        if (debug):
           print("Regex len -->" + str(len(time_matches)))
        #Ora da
        if (len(time_matches)>0):
           absence['time' + get_from_to_other(0)] = convert_to_24_hours(time_matches[0])
           if (debug):
                print("Regex " + time_matches[0])
        #Ora a
        if (len(time_matches) > 1):
           absence['time' + get_from_to_other(1)] = convert_to_24_hours(time_matches[1])
           if (debug):
                print("Regex " +time_matches[1])
    except ValueError as e:
        print(e)



    # Se il motore Spacy NON ha trovato date, tentiamo di estrarre le date con re e pattern regexp
    if 'date_from' not in absence:
        date_from=extract_date_regexp(sentence)
        if (date_from is None):
            absence['date'+get_from_to_other(0)] = str(datetime.today())
        else:
            absence['date' + get_from_to_other(0)]=str(date_from)

    # Se il motore Spacy non trova la data fine, allora prova verificare il pattern 1 week, 2 months etc.etc... per calcolare la data fine
    if 'date_to' not in absence:
        try:
            data_from_date = datetime.strptime(absence['date_from'], '%Y-%m-%d %H:%M:%S.%f')
        except ValueError as e:
            data_from_date = datetime.strptime(absence['date_from'], '%Y-%m-%d %H:%M:%S')
        if debug:
            print('data_from_date -->' + str(data_from_date))
        #
        absence['date'+get_from_to_other(1)] = str(calculate_dates(replace_words_with_numbers(sentence),data_from_date))

    # se c'è la data da ma manca la data a. Le due date sono uguale
    if 'date_from' in absence and ('date_to' not in absence or absence['date_to'] == 'None') :
        absence['date_to'] = absence['date_from']

    # Se non sono specicati gli orari nel testo la durata è tutto il giorno ed azzero eventuali orari residui nelle date
    if 'time_from' not in absence and 'time_to' not in absence:
        absence['duration']=ALL_DAY_LONG
        absence['date_from']=remove_time_from_date(absence['date_from'])
        absence['date_to'] = remove_time_from_date(absence['date_to'])

    # Se sono specificati gli orari inizio e fine si calcola la durata
    if 'time_from' in absence and 'time_to' in absence:
        absence['duration']=calculate_duration(absence['time_from'],absence['time_to'])
        absence['date_from']=concatenate_date_time(absence['date_from'], absence['time_from'])
        absence['date_to']  =concatenate_date_time(absence['date_to'], absence['time_to'])


    print("-->" + str(absence))
    return absence

def unitTest():
    global debug
    debug = False
    for sentence in sentences:
        readInfo(sentence)

if __name__ == '__main__':
    unitTest()