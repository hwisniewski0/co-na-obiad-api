import re
from datetime import datetime

def podziel_obiad(dane):
    wynik = []
    dzisiaj = datetime.now().date()

    for wpis in dane:
        obiad = wpis.get("obiad", "")
        zupa, drugieDanie = "", ""

        # Rozdzielenie na podstawie pierwszego nawiasu
        if "(" in obiad:
            czesci = obiad.split("(", 1)
            zupa = czesci[0].strip()
            if ")" in czesci[1]:
                drugieDanie = czesci[1].split(")", 1)[1].strip()

        # Usuwanie gramatury w nawiasach i zbędnych spacji
        zupa = re.sub(r"\s*\([^)]*\)", "", zupa).strip()
        drugieDanie = re.sub(r"\s*\([^)]*\)", "", drugieDanie).strip()

        # Zamiana wielokrotnych spacji i tabulatorów na pojedynczą spację
        zupa = re.sub(r"[\s\t]+", " ", zupa).strip()
        drugieDanie = re.sub(r"[\s\t]+", " ", drugieDanie).strip()

        # Czyszczenie składników
        wpis["skladniki"] = re.sub(r"[\s\t]+", " ", wpis.get("skladniki", "")).strip()

        # Dodanie nowych kluczy do wpisu
        wpis["zupa"] = zupa
        wpis["drugieDanie"] = drugieDanie
        del wpis["obiad"]  # Usunięcie oryginalnego klucza 'obiad'

        # Filtracja po dacie
        data_dnia = datetime.strptime(wpis["data_dnia"], "%d-%m-%Y").date()
        if data_dnia >= dzisiaj:
            wynik.append(wpis)

    return wynik