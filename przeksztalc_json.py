from datetime import timedelta
from parse_date_range import parse_date_range

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
                "data_dnia": date.strftime("%d-%m-%Y"),
                "dzien": day_data["dzien"],
                "obiad": day_data["obiad"],
                "skladniki": day_data.get("skladniki", ""),
                "alergeny": day_data.get("alergeny", "")
            }
            daily_menu.append(daily_entry)

    daily_menu.sort(key=lambda x: x["data_dnia"])
    return daily_menu