import typer
from datetime import date

from connections.fetch import get_categories


def run(puzzle_date: str | None = None) -> None:
    parsed = date.fromisoformat(puzzle_date) if puzzle_date else date.today()
    categories = get_categories(parsed)
    for category, words in categories.items():
        print(f"[{category}]: {', '.join(words)}")


if __name__ == "__main__":
    typer.run(run)
