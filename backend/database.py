"""This file provides the APL MOOC backend database models and functions.

Each database function performs one task, such as reading
certain data or adding points to the database. These
functions do not validate their input; ensure that all
IDs and points are valid in the functions calling the database functions.
"""

import os
import json
from flask import Blueprint
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint, event
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.engine import Connection
from sqlalchemy.schema import Table

bp = Blueprint("database", __name__, cli_group=None)


class Base(DeclarativeBase):  # pylint: disable=too-few-public-methods
    """
    The base database model for SQLAlchemy.
    """

db = SQLAlchemy(model_class=Base)


class Points(db.Model):  # pylint: disable=too-few-public-methods
    """
    The model for the Points database table.
    """

    id: Mapped[int] = mapped_column(primary_key=True)
    id_user: Mapped[str] = mapped_column()
    id_problem: Mapped[str] = mapped_column()
    points: Mapped[int] = mapped_column()
    __table_args__ = (UniqueConstraint("id_user", "id_problem", name="unique_user_problem"),)


class Problems(db.Model):  # pylint: disable=too-few-public-methods
    """
    The model for the Problems database table.
    """

    id: Mapped[int] = mapped_column(primary_key=True)
    id_problem: Mapped[str] = mapped_column(unique=True)
    config: Mapped[str] = mapped_column()


@event.listens_for(Problems.__table__, "after_create")
def init_problems(target: Table, connection: Connection, **kwargs):
    """
    Reads the available problems and stores them in the Problems table.

    Args:
        target (Table): The table variable automatically provided by Flask
        connection (Connection): The connection variable automatically provided by Flask
        **kwargs: Any other arguments. Ignored.
    """

    del kwargs

    connection.execute(target.delete())

    problem_files = [
        os.path.join("problems", file) for file in os.listdir("problems")
        if os.path.isfile(os.path.join("problems", file))
        and os.path.splitext(file)[-1].lower() == ".json"
    ]

    for filename in problem_files:
        with open(filename, "r", encoding="utf-8") as f:
            problem_config = json.load(f)

        id_problem = problem_config.get("id")
        if id_problem is None:  # pragma: no cover
            continue

        connection.execute(target.insert(), {
            "id_problem": id_problem,
            "config": json.dumps(problem_config),
        })

    connection.commit()


@bp.cli.command("init_db")
def init_db():
    """
    Initialise the database.
    
    To run this command, run `flask init_db` in the console.
    """

    db.create_all()


def get_problem_config(id_problem: str) -> dict | None:
    """
    Returns the problem configuration for a certain problem from the Problems table.

    Args:
        id_problem (str): The problem ID
    
    Returns:
        dict:
            The parsed JSON data from the configuration file,
            or None if the problem ID is not found
    """

    result = db.session.execute(
        db.select(Problems.config)
        .where(Problems.id_problem==id_problem)
    ).scalar()

    if result is None:
        return None

    return json.loads(result)


def get_all_points() -> list:
    """
    Gets all the point totals per user from the database.

    Returns:
        list: A list of dictionaries containing the user IDs and total points
    """

    results =  db.session.execute(
        db.select(Points.id_user, func.sum(Points.points))
        .group_by(Points.id_user)
    ).all()

    return [{
        "id_user": row[0],
        "points": row[1],
    } for row in results]


def insert_points(id_user: str, id_problem: str, points: int):
    """
    Award a user a certain number of points for a specific problem.
    If the number of points to award is less than what the user already has, nothing happens.

    Args:
        id_user (str): The user ID
        id_problem (str): The problem ID
        points (int): The number of points to award
    """

    current = db.session.execute(
        db.select(Points)
        .where(Points.id_user==id_user)
        .where(Points.id_problem==id_problem)
    ).scalar()

    if current is None:
        db.session.add(Points(
            id_user = id_user,
            id_problem = id_problem,
            points = points,
        ))
        db.session.commit()
        return

    if current.points >= points:
        return

    current.points = points
    db.session.commit()
