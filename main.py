import requests
from bs4 import BeautifulSoup
import re
import json
from flask import Flask, jsonify, render_template
from datetime import datetime, timedelta

app = Flask(__name__)




MONTHS_PL = {
    "stycznia": 1, "lutego": 2, "marca": 3, "kwietnia": 4, "maja": 5, "czerwca": 6,
    "lipca": 7, "sierpnia": 8, "września": 9, "października": 10, "listopada": 11, "grudnia": 12
}





def get_obiad():
    # URL do strony z obiadami
    url = "http://dualcafe.leszno.eu/obiady-domowe"

    # Wczytanie strony
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        # Zbiera daty tygodniowe
        tygodniowe_daty = []
        for p in soup.find_all('p'):
            tekst = p.get_text(strip=True)
            if re.search(r'\d{1,2} [a-ząćęłńóśżź]+ -\d{1,2} [a-ząćęłńóśżź]+(?:&nbsp;)*', tekst, re.IGNORECASE) or \
                re.search(r'\d{1,2} [a-ząćęłńóśżź]+ – \d{1,2} [a-ząćęłńóśżź]+', tekst, re.IGNORECASE) or \
                re.search(r'\d{1,2} [a-ząćęłńóśżź]+–\d{1,2} [a-ząćęłńóśżź]+', tekst, re.IGNORECASE) or \
                re.search(r'\d{1,2} [a-ząćęłńóśżź]+ - \d{1,2} [a-ząćęłńóśżź]+', tekst, re.IGNORECASE) or \
                re.search(r'\d{1,2} [a-ząćęłńóśżź]+-\d{1,2} [a-ząćęłńóśżź]+', tekst, re.IGNORECASE):
                tygodniowe_daty.append(tekst)

        # Inicjalizacja słownika do przechowywania menu
        menu_data = {}

        # Pobieranie wszystkich tabel i przypisanie ich do dat
        wszystkie_tabele = soup.find_all('table')

        # Sprawdzamy, czy liczba tabel i dat się zgadza
        if len(tygodniowe_daty) == len(wszystkie_tabele):
            # Przechodzimy przez każdą datę tygodniową i tabelę
            for data, tabela in zip(tygodniowe_daty, wszystkie_tabele):
                dzienne_menu = []  # Lista na dni w danym tygodniu
                current_day = None  # Zmienna do przechowywania aktualnego dnia tygodnia
                current_obiad = None  # Zmienna do przechowywania aktualnego obiadu
                skladniki = None  # Zmienna do przechowywania składników
                alergeny = None  # Zmienna do przechowywania alergenów

                wiersze = tabela.find_all('tr')

                # Przechodzimy przez wszystkie wiersze tabeli dla aktualnego tygodnia
                for wiersz in wiersze:
                    komorki = wiersz.find_all('td')
                    tekst_komorek = [komorka.text.strip() for komorka in komorki]

                    # Przypadek, gdy mamy dane o dniu i obiedzie
                    if len(tekst_komorek) >= 2 and any(dzien in tekst_komorek[0] for dzien in ["Poniedziałek", "Wtorek", "Środa", "Czwartek", "Piątek"]):
                        # Jeśli poprzedni dzień ma przypisane składniki i alergeny, dodajemy je do menu
                        if current_day:
                            if current_obiad:
                                dzienne_menu.append({
                                    "dzien": current_day,
                                    "obiad": current_obiad,
                                    "skladniki": skladniki,
                                    "alergeny": alergeny
                                })
                        # Ustalamy nowy dzień i obiad
                        current_day = tekst_komorek[0]
                        current_obiad = tekst_komorek[1]
                        skladniki = None  # Reset składników
                        alergeny = None  # Reset alergenów

                    # Przypadek, gdy mamy składniki
                    elif len(tekst_komorek) >= 2 and "skład" in tekst_komorek[0].lower():
                        skladniki = tekst_komorek[1]

                    # Przypadek, gdy mamy alergeny
                    elif len(tekst_komorek) >= 2 and "alergeny" in tekst_komorek[0].lower():
                        alergeny = tekst_komorek[1]

                # Dodajemy ostatni dzień, jeśli istnieje
                if current_day:
                    dzienne_menu.append({
                        "dzien": current_day,
                        "obiad": current_obiad,
                        "skladniki": skladniki,
                        "alergeny": alergeny
                    })

                # Dodajemy zebrane menu do słownika, przypisując do odpowiedniego tygodnia
                menu_data[data] = dzienne_menu

            return menu_data
        else:
            return {"error": "Liczba dat i tabel nie zgadza się. Sprawdź strukturę HTML strony."}
    else:
        return {"error": f"Błąd podczas ładowania strony: {response.status_code}"}



def parse_date_range(date_range, year=None):
    """
    Parsuje zakres dat w formacie 'DD miesiąc - DD miesiąc' lub 'DD miesiąc - DD'.
    Normalizuje znaki łącznika. Jeśli brakuje roku, zostanie dodany bieżący.
    """
    if not year:
        year = datetime.now().year

    # Normalizacja znaków łącznika
    normalized_range = date_range.replace("–", "-").replace("—", "-").strip()

    try:
        # Rozdzielenie zakresu na części
        start, end = normalized_range.split("-")
        start = start.strip()
        end = end.strip()

        # Parsowanie początkowej daty
        start_day, start_month = start.split()
        start_date = datetime(year, MONTHS_PL[start_month], int(start_day))

        # Parsowanie końcowej daty
        if " " in end:  # Jeśli jest dzień i miesiąc
            end_day, end_month = end.split()
            end_date = datetime(year, MONTHS_PL[end_month], int(end_day))
        else:  # Jeśli tylko dzień (zakładamy ten sam miesiąc co początkowy)
            end_date = datetime(year, start_date.month, int(end))

        return start_date, end_date
    except Exception as e:
        raise ValueError(f"Nieprawidłowy format tygodnia: {date_range}") from e

def przeksztalc_json(weekly_json):
    daily_menu = []

    for week, days in weekly_json.items():
        try:
            start_date, end_date = parse_date_range(week)
        except ValueError as e:
            raise ValueError(f"Nieprawidłowy format tygodnia: {week}") from e

        delta = (end_date - start_date).days + 1
        week_dates = [start_date + timedelta(days=i) for i in range(delta)]

        for day_data, date in zip(days, week_dates):
            daily_entry = {
                "data_tygodnia": week,
                "data_dnia": date.strftime("%Y-%m-%d"),
                "dzien": day_data["dzien"],
                "obiad": day_data["obiad"],
                "skladniki": day_data.get("skladniki", ""),
                "alergeny": day_data.get("alergeny", "")
            }
            daily_menu.append(daily_entry)

    daily_menu.sort(key=lambda x: x["data_dnia"])
    return daily_menu




@app.route('/get_obiad', methods=['GET'])
def obiady():
    # Wywołanie funkcji i zwrócenie danych w formacie JSON
    menu_data = get_obiad()

    converted_menu = przeksztalc_json(menu_data)
    return jsonify(converted_menu)

@app.route('/version', methods=['GET'])
def version():
    return "1.0.0"

@app.route('/', methods=['GET'])
def main():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
