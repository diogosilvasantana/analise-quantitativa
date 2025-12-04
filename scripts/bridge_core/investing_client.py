import aiohttp
import asyncio
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import logging
import random
import datetime

logger = logging.getLogger("Bridge.Investing")

class InvestingClient:
    def __init__(self):
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0"
        ]

    async def scrape_ticker(self, session: aiohttp.ClientSession, name: str, url: str):
        if "awesomeapi" in url:
            return await self._fetch_api(session, name, url)

        try:
            # Jitter (Random Delay)
            delay = random.uniform(1, 3)
            await asyncio.sleep(delay)

            headers = {
                "User-Agent": random.choice(self.user_agents),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                "Referer": "https://br.investing.com/",
                "Upgrade-Insecure-Requests": "1",
                "Sec-Ch-Ua": '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"Windows"',
                "Sec-Fetch-Dest": "document",
                "Sec-Fetch-Mode": "navigate",
                "Sec-Fetch-Site": "same-origin",
                "Sec-Fetch-User": "?1",
                "Connection": "keep-alive"
            }
            
            async with session.get(url, headers=headers, timeout=15) as response:
                if response.status != 200:
                    logger.warning(f"⚠️ Falha ao acessar {name}: Status {response.status}")
                    return None
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
            
            # Selectors (Robust)
            price_element = soup.find(class_="text-5xl")
            if not price_element:
                price_element = soup.find(attrs={"data-test": "instrument-price-last"})
            if not price_element:
                price_element = soup.select_one("div[data-test='instrument-header-details'] div[data-test='instrument-header-last-price']")
            
            change_element = soup.find(attrs={"data-test": "instrument-price-change-percent"})
            if not change_element:
                 change_element = soup.find(lambda tag: tag.name == "span" and "instrument-price-change-percent" in str(tag.get("data-test", "")))
            if not change_element:
                change_element = soup.select_one("div[data-test='instrument-header-details'] div[data-test='instrument-header-net-change-percentage']")

            price_str = price_element.text.strip() if price_element else "N/A"
            change_str = change_element.text.strip() if change_element else "N/A"
            
            if price_str == "N/A":
                return None

            # Parse Price
            clean_price = price_str.replace('.', '').replace(',', '.')
            try:
                price = float(clean_price)
            except:
                price = 0.0
            
            # Parse Change
            clean_change = change_str.replace('%', '').replace('(', '').replace(')', '').replace(',', '.').replace('+', '')
            try:
                change_pct = float(clean_change)
            except:
                change_pct = 0.0
            
            # Calculate absolute variation (approximate)
            variation = price * (change_pct / 100)
            
            logger.info(f"✅ {name}: {price} ({change_pct}%)")
            
            return {
                "valor": price,
                "var": variation,
                "var_pct": change_pct,
                "timestamp": datetime.datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro no scraping de {name}: {e}")
            return None

    async def _fetch_api(self, session: aiohttp.ClientSession, name: str, url: str):
        try:
            async with session.get(url, timeout=10) as response:
                if response.status != 200:
                    logger.warning(f"⚠️ Falha na API {name}: Status {response.status}")
                    return None
                
                data = await response.json()
                # AwesomeAPI format: {"USDBRL": {"bid": "...", "pctChange": "...", ...}}
                if "USDBRL" in data:
                    item = data["USDBRL"]
                    price = float(item["bid"])
                    change_pct = float(item["pctChange"])
                    variation = float(item.get("varBid", 0.0))
                    
                    logger.info(f"✅ {name} (API): {price} ({change_pct}%)")
                    
                    return {
                        "valor": price,
                        "var": variation,
                        "var_pct": change_pct,
                        "timestamp": datetime.datetime.now().isoformat()
                    }
                return None
        except Exception as e:
            logger.error(f"❌ Erro na API {name}: {e}")
            return None
