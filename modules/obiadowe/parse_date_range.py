from datetime import datetime

MONTHS_PL = {
    "stycznia": 1, "lutego": 2, "marca": 3, "kwietnia": 4, "maja": 5, "czerwca": 6,
    "lipca": 7, "sierpnia": 8, "września": 9, "października": 10, "listopada": 11, "grudnia": 12
}



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

