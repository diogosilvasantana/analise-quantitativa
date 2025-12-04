import aiohttp
import asyncio
from bs4 import BeautifulSoup
import logging
import datetime
import random

logger = logging.getLogger("Bridge.Calendar")

class CalendarClient:
    def __init__(self):
        self.url = "https://br.investing.com/economic-calendar/"
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0"
        ]

    def _should_fetch(self, cache: list) -> bool:
        """
        Smart Polling Logic:
        1. If cache is empty -> Fetch.
        2. If there is a high impact event (3 stars) in the last 30 mins with no actual value -> Fetch.
        3. Else -> Skip.
        """
        if not cache:
            logger.info("🔍 Cache vazio. Iniciando primeira coleta...")
            return True

        now = datetime.datetime.now()
        
        for event in cache:
            # Parse event time (HH:MM)
            try:
                event_time_str = event.get("time", "")
                if ":" not in event_time_str: continue
                
                hour, minute = map(int, event_time_str.split(":"))
                event_dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # Check if event is in the past 30 mins or future 5 mins
                diff_minutes = (now - event_dt).total_seconds() / 60
                
                # If event passed recently (0 to 30 mins ago) AND has no actual value AND is high impact
                if 0 <= diff_minutes <= 30 and not event.get("actual") and event.get("impact", 0) >= 3:
                    logger.info(f"⚡ Evento Pendente Detectado: {event['event']} ({event['time']}). Buscando atualização...")
                    return True
                    
            except Exception:
                continue
                
        logger.debug("💤 Nenhum evento pendente. Usando cache.")
        return False

    async def fetch_events(self, session: aiohttp.ClientSession, current_cache: list = None):
        """
        Fetches economic calendar events with Smart Polling (Async).
        """
        if current_cache is None:
            current_cache = []

        # 1. Check if we need to fetch
        if not self._should_fetch(current_cache):
            return current_cache

        try:
            # 2. Jitter (Random Delay)
            delay = random.uniform(2, 6)
            logger.info(f"⏳ Aguardando {delay:.2f}s (Jitter)...")
            await asyncio.sleep(delay)

            headers = {
                "User-Agent": random.choice(self.user_agents),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Referer": "https://br.investing.com/",
                "Upgrade-Insecure-Requests": "1"
            }
            
            async with session.get(self.url, headers=headers, timeout=15) as response:
                if response.status in [403, 503]:
                    logger.warning(f"🛡️ Bloqueio detectado ({response.status}). Mantendo cache.")
                    return current_cache
                    
                if response.status != 200:
                    logger.warning(f"⚠️ Falha ao acessar Calendário: Status {response.status}")
                    return current_cache

                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
            
            table = soup.find("table", id="economicCalendarData")
            
            if not table:
                logger.warning("⚠️ Tabela do calendário não encontrada.")
                return current_cache

            events = []
            rows = table.find("tbody").find_all("tr", class_="js-event-item")

            for row in rows:
                try:
                    # Extract Time
                    time_cell = row.find("td", class_="time")
                    event_time = time_cell.text.strip() if time_cell else ""
                    
                    # Extract Currency
                    # Use specific class 'flagCur' to avoid issues with multiple classes
                    currency_cell = row.find("td", class_="flagCur")
                    currency = currency_cell.text.strip() if currency_cell else ""
                    
                    # Filter Currency (USD or BRL only)
                    if currency not in ["USD", "BRL"]:
                        continue

                    # Extract Impact (Stars)
                    sentiment_cell = row.find("td", class_="sentiment")
                    impact = 0
                    if sentiment_cell:
                        impact = len(sentiment_cell.find_all("i", class_="grayFullBullishIcon"))
                    
                    # Filter Impact (2 or 3 stars)
                    if impact < 2:
                        continue

                    # Extract Event Name
                    event_cell = row.find("td", class_="event")
                    event_name = event_cell.find("a").text.strip() if event_cell and event_cell.find("a") else ""
                    
                    # Extract Values
                    actual = row.find("td", class_="act").text.strip()
                    forecast = row.find("td", class_="fore").text.strip()
                    previous = row.find("td", class_="prev").text.strip()

                    events.append({
                        "time": event_time,
                        "currency": currency,
                        "impact": impact,
                        "event": event_name,
                        "actual": actual,
                        "forecast": forecast,
                        "previous": previous
                    })
                except Exception:
                    continue
            
            logger.info(f"📅 Calendário atualizado: {len(events)} eventos relevantes.")
            return events

        except Exception as e:
            logger.error(f"❌ Erro ao buscar calendário: {e}")
            return current_cache
