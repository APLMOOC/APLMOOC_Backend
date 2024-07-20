"""This file provides the APL MOOC backend database models and functions.

Each database function performs one task, such as reading
certain data or adding points to the database. These
functions do not validate their input; ensure that all
IDs and points are valid in the functions calling the database functions.
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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
    id_user: Mapped[int] = mapped_column()
    id_problem: Mapped[int] = mapped_column()
    points: Mapped[int] = mapped_column()
    __table_args__ = (UniqueConstraint("id_user", "id_problem", name="unique_user_problem"),)


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


def insert_points(id_user: int, id_problem: int, points: int):
    """
    Award a user a certain number of points for a specific problem.
    If the number of points to award is less than what the user already has, nothing happens.

    Args:
        id_user (int): The user ID
        id_problem (int): The problem ID
        points (int): The number of points to award
    """

    current = db.session.execute(
        db.select(Points)
        .where(Points.id_user==id_user)
        .where(Points.id_problem==id_problem)
    ).scalar()

    if current is None:
        to_add = Points(
            id_user = id_user,
            id_problem = id_problem,
            points = points,
        )
        db.session.add(to_add)
        db.session.commit()
        return

    if current.points >= points:
        return

    current.points = points
    db.session.commit()
