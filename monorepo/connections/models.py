"""
SQLModel table definitions for the Connections puzzle database.
"""

from datetime import date

from sqlmodel import Field, SQLModel


class Puzzle(SQLModel, table=True):
    """
    One row per puzzle date.
    """

    puzzle_date: date = Field(primary_key=True)


class Category(SQLModel, table=True):
    """
    One row per category within a puzzle.
    """

    id: int | None = Field(default=None, primary_key=True)
    puzzle_date: date = Field(foreign_key="puzzle.puzzle_date")
    title: str


class Card(SQLModel, table=True):
    """
    One row per word card within a category.
    """

    id: int | None = Field(default=None, primary_key=True)
    category_id: int = Field(foreign_key="category.id")
    content: str
