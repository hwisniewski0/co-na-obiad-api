import requests
from bs4 import BeautifulSoup
import re
import json
from flask import Flask, jsonify, render_template, request
from datetime import datetime, timedelta
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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
                dzienne_menu = []
                current_day = None
                current_obiad = None
                skladniki = None
                alergeny = None 

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


def podziel_obiad(dane):
    wynik = []
    dzisiaj = datetime.now().date()

    for wpis in dane:
        obiad = wpis.get("obiad", "")
        zupa, drugie_danie = "", ""

        # Rozdzielenie na podstawie pierwszego nawiasu
        if "(" in obiad:
            czesci = obiad.split("(", 1)
            zupa = czesci[0].strip()
            if ")" in czesci[1]:
                drugie_danie = czesci[1].split(")", 1)[1].strip()

        # Usuwanie gramatury w nawiasach i zbędnych spacji
        zupa = re.sub(r"\s*\([^)]*\)", "", zupa).strip()
        drugie_danie = re.sub(r"\s*\([^)]*\)", "", drugie_danie).strip()

        # Zamiana wielokrotnych spacji i tabulatorów na pojedynczą spację
        zupa = re.sub(r"[\s\t]+", " ", zupa).strip()
        drugie_danie = re.sub(r"[\s\t]+", " ", drugie_danie).strip()

        # Czyszczenie składników
        wpis["skladniki"] = re.sub(r"[\s\t]+", " ", wpis.get("skladniki", "")).strip()

        # Dodanie nowych kluczy do wpisu
        wpis["zupa"] = zupa
        wpis["drugie_danie"] = drugie_danie
        del wpis["obiad"]  # Usunięcie oryginalnego klucza 'obiad'

        # Filtracja po dacie
        data_dnia = datetime.strptime(wpis["data_dnia"], "%Y-%m-%d").date()
        if data_dnia >= dzisiaj:
            wynik.append(wpis)

    return wynik



@app.route('/get_obiad', methods=['GET'])
def obiady():
    # Wywołanie funkcji i zwrócenie danych w formacie JSON
    menu_data = get_obiad()

    converted_menu = przeksztalc_json(menu_data)

    return jsonify(podziel_obiad(converted_menu))

@app.route('/version', methods=['GET'])
def version():
    return "1.0"

@app.route('/', methods=['GET'])
def main():
    return render_template('index.html')


# Funkcja wysyłająca e-mail
def send_email(content, sender_email):
    try:
        # Pobierz dane z zmiennych środowiskowych
        email_address = os.getenv('EMAIL_ADDRESS')
        email_password = os.getenv('EMAIL_PASSWORD')
        email_recipient = os.getenv('EMAIL_RECIPIENT')  # Odbiorca e-maila
        
        if not email_address or not email_password or not email_recipient:
            return False
        

        # Ustawienia SMTP (Google)
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        # Tworzenie wiadomości e-mail
        msg = MIMEMultipart()
        msg['From'] = email_address
        msg['To'] = email_recipient  # Używamy zmiennej środowiskowej EMAIL_RECIPIENT
        msg['Subject'] = "Wiadomość od użytkownika"

        # Treść wiadomości
        msg.attach(MIMEText(content, 'plain'))

        # Łączenie z serwerem SMTP
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(email_address, email_password)

        # Wysyłanie wiadomości
        server.sendmail(email_address, email_recipient, msg.as_string())
        server.quit()

        print("Wiadomość została wysłana.")
        return True
    except Exception as e:
        print(f"Błąd podczas wysyłania wiadomości e-mail: {e}")
        return False


@app.route('/send_email', methods=['GET'])
def send_email_api():
    # Odczytanie parametrów zapytania
    content = request.args.get('content')
    sender_email = request.args.get('sender')

    if not content or not sender_email:
        return jsonify({"error": "Brakuje argumentów 'content' lub 'sender'"}), 400

    # Wywołanie funkcji wysyłającej e-mail
    success = send_email(content, sender_email)
    
    if success:
        return jsonify({"message": "Wiadomość e-mail została wysłana pomyślnie!"}), 200
    else:
        return jsonify({"error": "Wystąpił błąd podczas wysyłania e-maila"}), 500




if __name__ == '__main__':
    app.run(host="0.0.0.0",port=8080)