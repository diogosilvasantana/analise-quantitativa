import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import datetime

def debug_calendar():
    url = "https://br.investing.com/economic-calendar/"
    ua = UserAgent()
    headers = {
        "User-Agent": ua.chrome,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Referer": "https://br.investing.com/",
        "Upgrade-Insecure-Requests": "1"
    }

    print(f"🔍 Acessando {url}...")
    try:
        response = requests.get(url, headers=headers, timeout=15)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code != 200:
            print("❌ Falha na requisição.")
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find("table", id="economicCalendarData")
        
        if not table:
            print("❌ Tabela 'economicCalendarData' NÃO encontrada.")
            # Salvar HTML para analise se precisar
            # with open("debug_calendar.html", "w", encoding="utf-8") as f:
            #     f.write(response.text)
            return

        print("✅ Tabela encontrada. Analisando linhas...")
        rows = table.find("tbody").find_all("tr", class_="js-event-item")
        print(f"Total de linhas de evento encontradas: {len(rows)}")

        for i, row in enumerate(rows):
            try:
                # Time
                time_cell = row.find("td", class_="time")
                event_time = time_cell.text.strip() if time_cell else "N/A"
                
                # Currency
                currency_cell = row.find("td", class_="left flagCur")
                currency = currency_cell.text.strip() if currency_cell else "N/A"
                
                # Impact
                sentiment_cell = row.find("td", class_="sentiment")
                impact = 0
                if sentiment_cell:
                    impact = len(sentiment_cell.find_all("i", class_="grayFullBullishIcon"))
                
                # Event
                event_cell = row.find("td", class_="event")
                event_name = event_cell.text.strip() if event_cell else "N/A"

                print(f"[{i}] {event_time} | {currency} | ⭐ {impact} | {event_name}")

            except Exception as e:
                print(f"Erro na linha {i}: {e}")

    except Exception as e:
        print(f"❌ Erro fatal: {e}")

if __name__ == "__main__":
    debug_calendar()
