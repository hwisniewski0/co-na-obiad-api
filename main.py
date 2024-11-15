from flask import Flask, jsonify
from bs4 import BeautifulSoup
import requests
import re

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
        dni = []
        wiersze = tabela.find_all('tr')
        for wiersz in wiersze:
            komorki = wiersz.find_all('td')
            tekst_komorek = [komorka.text.strip() for komorka in komorki]
            
            if len(tekst_komorek) >= 2 and any(dzien in tekst_komorek[0] for dzien in ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek"]):
                dni.append({
                    "dzien": tekst_komorek[0],
                    "obiad": tekst_komorek[1]
                })
            elif len(tekst_komorek) >= 2 and "Skład" in tekst_komorek[0]:
                dni[-1]["skladniki"] = tekst_komorek[1]
            elif len(tekst_komorek) >= 2 and "Alergeny" in tekst_komorek[0]:
                dni[-1]["alergeny"] = tekst_komorek[1].split(", ")

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)