import logging
from collections import OrderedDict
from typing import Dict, List, Optional

import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class IndianFestivalsScraper:
    """Scraper for Indian festivals from panchang.astrosage.com"""

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
        """Initialize scraper with year."""
        self.year = year
        self.timeout = timeout
        self.base_url = "https://panchang.astrosage.com/calendars/indiancalendar"
        self._soup = None
        self._tables = None

    def _fetch_data(self) -> None:
        """Fetch and parse HTML data."""
        if self._soup is not None:
            return

        try:
            url = f"{self.base_url}?language=en&date={self.year}"
            logger.info(f"Fetching data from {url}")

            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()

            self._soup = BeautifulSoup(response.text, 'html.parser')
            self._tables = self._soup.find_all('table')

            logger.info(f"Successfully fetched data for year {self.year}. Found {len(self._tables)} tables")
        except requests.RequestException as e:
            logger.error(f"Error fetching data: {str(e)}")
            raise

    def get_festivals(self, month: Optional[int] = None) -> Dict[str, List[Dict]]:
        """Get all festivals for the year, optionally filtered by month."""
        self._fetch_data()

        festivals = OrderedDict()
        target_month_name = self.MONTHS.get(month) if month else None

        logger.info(f"Processing festivals. Target month: {target_month_name}")

        for table in self._tables:
            try:
                # Get month name from table header
                thead = table.find('thead')
                if not thead:
                    continue

                month_header = thead.find('th')
                if not month_header:
                    continue

                header_text = month_header.text.strip()
                month_name = header_text.split()[0] if header_text else None

                if not month_name:
                    continue

                logger.debug(f"Processing table for month: {month_name}")

                # Skip if filtering by month and this isn't the target month
                if target_month_name and month_name != target_month_name:
                    continue

                # Extract festivals from table body
                tbody = table.find('tbody')
                if not tbody:
                    continue

                rows = tbody.find_all('tr')
                month_festivals = []

                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) >= 2:
                        try:
                            date_cell = cells[0].text.strip()
                            name_cell = cells[1].text.strip()

                            if not date_cell or not name_cell:
                                continue

                            date_parts = date_cell.split()
                            if len(date_parts) >= 2:
                                festival = {
                                    "date": date_parts[0],
                                    "day": date_parts[1],
                                    "name": name_cell
                                }
                                month_festivals.append(festival)
                                logger.debug(f"Added festival: {festival}")
                        except (IndexError, AttributeError) as e:
                            logger.debug(f"Error parsing row: {e}")
                            continue

                if month_festivals:
                    festivals[month_name] = month_festivals
                    logger.info(f"Found {len(month_festivals)} festivals for {month_name}")

                # If filtering by month and found it, we can break
                if target_month_name and month_name == target_month_name:
                    logger.info(f"Found target month {target_month_name}, breaking loop")
                    break

            except (AttributeError, IndexError) as e:
                logger.warning(f"Error parsing table: {str(e)}")
                continue

        logger.info(f"Total months with festivals: {len(festivals)}")
        return dict(festivals)

    def get_religious_festivals(self, month: Optional[int] = None) -> Dict[str, List[Dict]]:
        """Get religious festivals organized by religion."""
        self._fetch_data()

        religious_festivals = OrderedDict()
        target_month_name = self.MONTHS.get(month) if month else None

        # Initialize all religion categories
        for religion in self.FESTIVAL_COLORS.values():
            religious_festivals[religion] = []

        logger.info(f"Processing religious festivals. Target month: {target_month_name}")

        for table in self._tables:
            try:
                # Get month name
                thead = table.find('thead')
                if not thead:
                    continue

                month_header = thead.find('th')
                if not month_header:
                    continue

                header_text = month_header.text.strip()
                month_name = header_text.split()[0] if header_text else None

                if not month_name:
                    continue

                logger.debug(f"Processing religious festivals for month: {month_name}")

                # Skip if filtering by month
                if target_month_name and month_name != target_month_name:
                    continue

                # Process table rows
                tbody = table.find('tbody')
                if not tbody:
                    continue

                rows = tbody.find_all('tr')

                for row in rows:
                    cells = row.find_all('td')
                    if len(cells) < 2:
                        continue

                    try:
                        date_cell = cells[0].text.strip()

                        if not date_cell:
                            continue

                        date_parts = date_cell.split()
                        if len(date_parts) < 2:
                            continue

                        date_info = {
                            "date": date_parts[0],
                            "day": date_parts[1]
                        }

                        if not target_month_name:
                            date_info["month"] = month_name

                        # Check for styled tags (bold and links)
                        styled_tags = cells[1].find_all(['b', 'a'])

                        for tag in styled_tags:
                            style = tag.get('style', '')
                            if not style or ':' not in style:
                                continue

                            # Extract color from style
                            color_parts = style.split(':')
                            if len(color_parts) < 2:
                                continue

                            color = color_parts[1].strip().rstrip(';')
                            religion = self.FESTIVAL_COLORS.get(color)

                            if religion:
                                festival = date_info.copy()
                                festival["name"] = tag.text.strip()
                                religious_festivals[religion].append(festival)
                                logger.debug(f"Added {religion} festival: {festival}")

                    except (IndexError, AttributeError) as e:
                        logger.debug(f"Error parsing religious festival row: {e}")
                        continue

                # If filtering by month and found it, break
                if target_month_name and month_name == target_month_name:
                    logger.info(f"Found target month {target_month_name} for religious festivals")
                    break

            except (AttributeError, IndexError) as e:
                logger.warning(f"Error parsing religious festivals: {str(e)}")
                continue

        # Log counts
        for religion, fests in religious_festivals.items():
            if fests:
                logger.info(f"Found {len(fests)} {religion}")

        return dict(religious_festivals)
