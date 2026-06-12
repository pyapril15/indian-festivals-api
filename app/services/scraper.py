import logging
from collections import OrderedDict
from typing import Dict, List, Optional

import httpx
from bs4 import BeautifulSoup

logger = logging.getLogger("uvicorn.error")


class IndianFestivalsScraper:
    """Production-grade asynchronous scraper for Indian festivals from panchang.astrosage.com"""

    MONTHS = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }

    FESTIVAL_COLORS = {
        "#a60000": "Hindu Festivals",
        "#4A3475": "Government Holidays",
        "#556A21": "Sikh Festivals",
        "#d42426": "Christian Holidays",
        "#008000": "Islamic Holidays"
    }

    def __init__(self, year: int, timeout: int = 30):
        """Initialize scraper parameters."""
        self.year = year
        self.timeout = timeout
        self.base_url = "https://panchang.astrosage.com/calendars/indiancalendar"
        self._tables: Optional[List] = None

    async def _fetch_data(self) -> None:
        """Asynchronously fetches and parses raw HTML data without blocking the main event thread."""
        if self._tables is not None:
            return

        url = f"{self.base_url}?language=en&date={self.year}"
        logger.info(f"Asynchronously fetching festival metadata from: {url}")

        try:
            # Using httpx.AsyncClient ensures non-blocking network I/O
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.get(url)
                response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')
            self._tables = soup.find_all('table')
            logger.info(f"Successfully processed HTML metrics. Found {len(self._tables)} monthly tables.")

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP status extraction failure for year {self.year}: {e.response.status_code}")
            raise RuntimeError(f"External service responded with error status: {e.response.status_code}")
        except httpx.RequestError as e:
            logger.error(f"Network transport layer failure on connection target: {str(e)}")
            raise RuntimeError("Failed to establish target connection stream with external provider.")

    async def get_festivals(self, month: Optional[int] = None) -> Dict[str, List[Dict]]:
        """Get all festivals for the year, optionally filtered by month."""
        await self._fetch_data()

        if not self._tables:
            return {}

        festivals = OrderedDict()
        target_month_name = self.MONTHS.get(month) if month else None

        for table in self._tables:
            try:
                thead = table.find('thead')
                if not thead:
                    continue

                month_header = thead.find('th')
                if not month_header:
                    continue

                header_text = month_header.text.strip()
                month_name = header_text.split()[0] if header_text else None

                if not month_name or (target_month_name and month_name != target_month_name):
                    continue

                tbody = table.find('tbody')
                if not tbody:
                    continue

                month_festivals = []
                for row in tbody.find_all('tr'):
                    cells = row.find_all('td')
                    if len(cells) < 2:
                        continue

                    date_cell = cells[0].text.strip()
                    name_cell = cells[1].text.strip()

                    if not date_cell or not name_cell:
                        continue

                    date_parts = date_cell.split()
                    if len(date_parts) >= 2:
                        month_festivals.append({
                            "date": date_parts[0],
                            "day": date_parts[1],
                            "name": name_cell
                        })

                if month_festivals:
                    festivals[month_name] = month_festivals

                if target_month_name and month_name == target_month_name:
                    break

            except (AttributeError, IndexError) as e:
                logger.warning(f"Gracefully bypassed malformed data segment row cell: {str(e)}")
                continue

        return dict(festivals)

    async def get_religious_festivals(self, month: Optional[int] = None) -> Dict[str, List[Dict]]:
        """Get religious festivals organized by religion categories."""
        await self._fetch_data()

        if not self._tables:
            return {}

        religious_festivals = OrderedDict()
        target_month_name = self.MONTHS.get(month) if month else None

        for religion in self.FESTIVAL_COLORS.values():
            religious_festivals[religion] = []

        for table in self._tables:
            try:
                thead = table.find('thead')
                if not thead:
                    continue

                month_header = thead.find('th')
                if not month_header:
                    continue

                header_text = month_header.text.strip()
                month_name = header_text.split()[0] if header_text else None

                if not month_name or (target_month_name and month_name != target_month_name):
                    continue

                tbody = table.find('tbody')
                if not tbody:
                    continue

                for row in tbody.find_all('tr'):
                    cells = row.find_all('td')
                    if len(cells) < 2:
                        continue

                    date_cell = cells[0].text.strip()
                    if not date_cell:
                        continue

                    date_parts = date_cell.split()
                    if len(date_parts) < 2:
                        continue

                    date_info = {"date": date_parts[0], "day": date_parts[1]}
                    if not target_month_name:
                        date_info["month"] = month_name

                    # Process targeted styled inline child tags
                    for tag in cells[1].find_all(['b', 'a']):
                        style = tag.get('style', '')
                        if not style or ':' not in style:
                            continue

                        # Precise split logic parsing for handling semicolon endings securely
                        color = style.split(':')[1].strip().split(';')[0].strip()
                        religion_group = self.FESTIVAL_COLORS.get(color)

                        if religion_group:
                            festival = date_info.copy()
                            festival["name"] = tag.text.strip()
                            religious_festivals[religion_group].append(festival)

                if target_month_name and month_name == target_month_name:
                    break

            except (AttributeError, IndexError) as e:
                logger.warning(f"Bypassed parsing exception trace for collection group element: {str(e)}")
                continue

        return dict(religious_festivals)
