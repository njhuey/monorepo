"""
Fetch all NYT Connections puzzles from the first puzzle date to today
and persist them to a SQLite database.
"""

import logging
import time
from datetime import date, timedelta
from typing import Final
from urllib.error import HTTPError

import typer
from sqlmodel import Session, SQLModel, col, create_engine, select

from monorepo.connections.fetch import fetch_connections
from monorepo.connections.models import Card, Category, Puzzle


_FIRST_PUZZLE_DATE: Final[date] = date(2023, 6, 12)
_BACKOFF_INITIAL_DELAY: Final[float] = 1.0
_BACKOFF_FACTOR: Final[float] = 2.0
_BACKOFF_MAX_RETRIES: Final[float] = 6

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def _latest_date_in_db(session: Session) -> date | None:
    result = session.exec(
        select(Puzzle).order_by(col(Puzzle.puzzle_date).desc())
    ).first()
    return result.puzzle_date if result else None


def _validate_puzzle_data(data: dict, puzzle_date: date) -> bool:
    """
    Validate that puzzle data has the expected structure.

    Parameters
    ----------
    data : dict
        Parsed JSON response from NYT API.
    puzzle_date : date
        Date of the puzzle, used in warning messages.

    Returns
    -------
    bool
        True if the data contains 4 categories each with 4 cards.
    """
    categories = data.get("categories")
    if not isinstance(categories, list) or len(categories) != 4:
        logger.warning(
            "Puzzle %s: expected 4 categories, got %s",
            puzzle_date,
            len(categories) if isinstance(categories, list) else categories,
        )
        return False
    for cat in categories:
        cards = cat.get("cards")
        if not isinstance(cards, list) or len(cards) != 4:
            logger.warning(
                "Puzzle %s: category %r has %s cards, expected 4",
                puzzle_date,
                cat.get("title"),
                len(cards) if isinstance(cards, list) else cards,
            )
            return False
        for card in cards:
            if "content" not in card:
                logger.warning(
                    "Puzzle %s: card missing 'content' field: %s", puzzle_date, card
                )
                return False
    return True


def _fetch_with_backoff(puzzle_date: date) -> dict | None:
    """
    Fetch puzzle data, retrying with exponential backoff on rate limit errors.

    Parameters
    ----------
    puzzle_date : date
        Date of the puzzle to fetch.

    Returns
    -------
    dict | None
        Parsed puzzle data, or None if the fetch failed after all retries
        or encountered a non-rate-limit error.
    """
    delay = _BACKOFF_INITIAL_DELAY
    for attempt in range(_BACKOFF_MAX_RETRIES + 1):
        try:
            return fetch_connections(puzzle_date)
        except HTTPError as e:
            if e.code == 429:
                if attempt < _BACKOFF_MAX_RETRIES:
                    logger.warning(
                        "Rate limited on %s (attempt %d), retrying in %.1fs",
                        puzzle_date,
                        attempt + 1,
                        delay,
                    )
                    time.sleep(delay)
                    delay *= _BACKOFF_FACTOR
                else:
                    logger.error(
                        "Rate limit retries exhausted for %s after %d attempts",
                        puzzle_date,
                        _BACKOFF_MAX_RETRIES + 1,
                    )
                    return None
            else:
                logger.error("HTTP %d error fetching %s: %s", e.code, puzzle_date, e)
                return None
        except Exception as e:
            logger.error("Error fetching %s: %s", puzzle_date, e)
            return None
    return None


def accumulate(db_path: str, append: bool = False) -> None:
    engine = create_engine(f"sqlite:///{db_path}")
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        if append:
            latest = _latest_date_in_db(session)
            start = (latest + timedelta(days=1)) if latest else _FIRST_PUZZLE_DATE
            logger.info("Appending from %s", start)
        else:
            start = _FIRST_PUZZLE_DATE

        current = start
        today = date.today()
        while current <= today:
            if not session.get(Puzzle, current):  # type: ignore[arg-type]
                raw = _fetch_with_backoff(current)
                if raw is None:
                    logger.error("Skipping %s due to fetch failure", current)
                    current += timedelta(days=1)
                    continue
                if not _validate_puzzle_data(raw, current):
                    logger.error(
                        "Skipping %s due to unexpected response structure", current
                    )
                    current += timedelta(days=1)
                    continue
                session.add(Puzzle(puzzle_date=current))
                for cat in raw["categories"]:
                    category = Category(puzzle_date=current, title=cat["title"].lower())
                    session.add(category)
                    session.flush()
                    for card in cat["cards"]:
                        session.add(
                            Card(
                                category_id=category.id,  # type: ignore[arg-type]
                                content=card["content"].lower(),
                            )
                        )
                logger.info("Fetched %s", current)
            current += timedelta(days=1)
        session.commit()


if __name__ == "__main__":
    typer.run(accumulate)
