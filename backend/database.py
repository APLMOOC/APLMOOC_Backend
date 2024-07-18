from flask import current_app, g
import sqlite3
import click


def init_db(db):
    with open("schema.sql", "r") as f:
        db.cursor().executescript(f.read())
    db.commit()


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(current_app.config["DATABASE"])
        init_db(db)
    return db


def close_connection(exception=None):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


@click.command("init-db")
def init_db_command():
    """Clear the existing data and create new tables."""
    db = get_db()
    init_db(db)
    click.echo("Initialized the database.")


def init_app(app):
    app.teardown_appcontext(close_connection)
    app.cli.add_command(init_db_command)


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def insert_db(query, args=()):
    db = get_db()
    db.execute(query, args)
    db.commit()
