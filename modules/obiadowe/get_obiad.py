import requests
from bs4 import BeautifulSoup
import re


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
