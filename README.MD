# Co Na Obiad API

Co Na Obiad API to aplikacja, która udostępnia dane o menu obiadowym w formie API. Została stworzona z myślą o udostępnieniu uczniom i nauczycielom informacji o dostępnych posiłkach w łatwej do przetworzenia formie.

## Link do API

Aplikacja jest hostowana na [Render.com](https://render.com/) i dostępna pod adresem:

[https://co-na-obiad-api.onrender.com](https://co-na-obiad-api.onrender.com)

## Funkcje

- **Pobieranie menu**: API umożliwia pobranie codziennego menu na podstawie daty.
- **Format JSON**: Menu jest zwracane w formacie JSON, który jest łatwy do przetworzenia przez aplikacje.
- **Aktualizacja menu**: Możliwość przekształcania menu z formatu HTML na JSON.

## Jak używać

1. Aby uzyskać menu obiadowe na konkretny dzień, wyślij zapytanie GET na endpoint `/get_obiad`.
2. Odpowiedź API zawiera menu w formacie JSON z datą, dniem tygodnia oraz szczegółami posiłków.

