from flask import Flask, jsonify
from bs4 import BeautifulSoup
import requests
import re
from collections import OrderedDict

app = Flask(__name__)

def fetch_obiad_data():
    url = "http://dualcafe.leszno.eu/obiady-domowe"
    response = requests.get(url)
    
    if response.status_code != 200:
        return {"error": "Nie udało się załadować strony."}
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Znalezienie dat tygodni
    tygodniowe_daty = []
    for p in soup.find_all('p'):
        tekst = p.get_text(strip=True)
        if re.search(r'\d{1,2} [a-ząćęłńóśżź]+ – \d{1,2} [a-ząćęłńóśżź]+', tekst, re.IGNORECASE):
            tygodniowe_daty.append(tekst)

    # Pobieranie tabel
    wszystkie_tabele = soup.find_all('table')
    
    if len(tygodniowe_daty) != len(wszystkie_tabele):
        return {"error": "Nie zgadza się liczba dat i tabel."}
    
    dane = []
    for data, tabela in zip(tygodniowe_daty, wszystkie_tabele):
        dni = OrderedDict()
        wiersze = tabela.find_all('tr')
        dzien = None  # Zmienna do śledzenia aktualnego dnia
        for wiersz in wiersze:
            komorki = wiersz.find_all('td')
            tekst_komorek = [komorka.text.strip() for komorka in komorki]
            
            # Rozpoznanie dnia tygodnia
            if len(tekst_komorek) >= 2 and any(d in tekst_komorek[0] for d in ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek"]):
                dzien = tekst_komorek[0]
                obiad = tekst_komorek[1]
                dni[dzien] = {"obiad": obiad, "skladniki": "", "alergeny": []}
            
            # Rozpoznanie składników
            elif len(tekst_komorek) >= 2 and "skład surowcowy" in tekst_komorek[0].lower() and dzien:
                dni[dzien]["skladniki"] = tekst_komorek[1]
            
            # Rozpoznanie alergenów
            elif len(tekst_komorek) >= 2 and "alergeny" in tekst_komorek[0].lower() and dzien:
                dni[dzien]["alergeny"] = tekst_komorek[1].split(", ")
        
        dane.append({
            "tydzien": data,
            "dni": dni
        })
    
    return dane

@app.route('/')
def home():
    return "API z obiadami. Użyj endpointu /get_obiad."

@app.route('/get_obiad')
def get_obiad():
    data = fetch_obiad_data()
    return jsonify(data)

@app.route('/version')
def version():
    return "1.0.0"
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

