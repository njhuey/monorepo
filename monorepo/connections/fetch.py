"""
Fetch the 16 words for today's NYT Connections puzzle.
"""

import json
import ssl
from datetime import date
from typing import Final
from urllib import error, request


_NYT_CONNECTIONS_URL: Final[str] = (
    "https://www.nytimes.com/svc/connections/v2/{date}.json"
)


def fetch_connections(puzzle_date: date | None = None) -> dict:
    """
    Fetch Connections puzzle data from NYT.

    Parameters
    ----------
    puzzle_date : date, optional
        Date to fetch. Defaults to today.

    Returns
    -------
    dict
        Parsed JSON response from NYT API.
    """
    if puzzle_date is None:
        puzzle_date = date.today()

    url = _NYT_CONNECTIONS_URL.format(date=puzzle_date.isoformat())
    req = request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    ctx = ssl.create_default_context()
    try:
        with request.urlopen(req, context=ctx) as response:
            return json.loads(response.read().decode())
    except error.URLError:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with request.urlopen(req, context=ctx) as response:
            return json.loads(response.read().decode())


def get_words(puzzle_date: date | None = None) -> list[str]:
    """
    Return the 16 words for the given date's Connections puzzle.
    """
    data = fetch_connections(puzzle_date)
    words = []
    for category in data["categories"]:
        for card in category["cards"]:
            words.append(card["content"])
    return words


def get_categories(puzzle_date: date | None = None) -> dict[str, list[str]]:
    """
    Return words grouped by category name.
    """
    data = fetch_connections(puzzle_date)
    return {
        category["title"]: [card["content"] for card in category["cards"]]
        for category in data["categories"]
    }
