import asyncio
import httpx
from bs4 import BeautifulSoup
from tentacles.base_tentacle import BaseTentacle

class QuotesTentacle(BaseTentacle):
    def __init__(self):
        super().__init__("quotes_tentacle")
        self.base_url = "http://quotes.toscrape.com"
        self.session = httpx.AsyncClient()

    async def run(self):
        try:
            self.logger.info("Quotes tentacle started.")
            state = self.load_state()
            start_page = state.get('page', 1) if state else 1
            page = start_page

            while not self.stop_event.is_set():
                await asyncio.sleep(0.1)
                self.update_detailed_status(f"Scraping page: {page}")
                url = f"{self.base_url}/page/{page}/"
                try:
                    response = await self.session.get(url)
                    response.raise_for_status()
                except httpx.HTTPError as e:
                    self.logger.error(f"Failed to fetch {url}: {e}")
                    self.update_detailed_status(f"Error: {e}")
                    self._status = 3
                    break

                soup = BeautifulSoup(response.text, 'html.parser')
                quotes = soup.find_all(class_='quote')

                if not quotes:
                    self.logger.info("No more quotes found. Tentacle finished.")
                    self.update_detailed_status("Finished")
                    self._status = 0
                    break

                for quote in quotes:
                    if self.stop_event.is_set():
                        break
                    text = quote.find(class_='text').get_text()
                    author = quote.find(class_='author').get_text()
                    self.logger.info(f"Scraped: '{text}' by {author}")

                self.save_state({'page': page})
                page += 1
                await asyncio.sleep(1)

            if self._status != 3:
                self._status = 0
            self.logger.info("Quotes tentacle finished.")
        except Exception as e:
            self.logger.exception("Fatal error in QuotesTentacle")
            self.update_detailed_status(f"Fatal Error: {e}")
            self._status = 3

if __name__ == "__main__":
    # Test block
    tentacle = QuotesTentacle()
    
    asyncio.run(tentacle.run())
