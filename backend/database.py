from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)


class Points(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    id_user: Mapped[int] = mapped_column()
    id_problem: Mapped[int] = mapped_column()
    points: Mapped[int] = mapped_column()
    __table_args__ = (UniqueConstraint("id_user", "id_problem", name="unique_user_problem"),)


def get_all_points():
    return db.session.execute(
        db.select(Points.id_user, func.sum(Points.points))
        .group_by(Points.id_user)
    ).all()


def insert_points(id_user: int, id_problem: int, points: int):
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
