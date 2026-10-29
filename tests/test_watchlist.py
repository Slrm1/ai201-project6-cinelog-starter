"""Tests for CineLog's watchlist service."""

from datetime import datetime, timedelta, timezone

import pytest

from app import create_app, db
from models import Film, User, WatchlistEntry
from services.collection_service import FilmNotFoundError
from services.watchlist_service import (
    AlreadyInWatchlistError,
    NotInWatchlistError,
    add_to_watchlist,
    get_watchlist,
    remove_from_watchlist,
)


@pytest.fixture
def app():
    app = create_app(config={
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def sample_user(app):
    with app.app_context():
        user = User(username="watcher", email="watcher@example.com")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture
def sample_film(app):
    with app.app_context():
        film = Film(title="Moonlight", year=2016, genre="Drama")
        db.session.add(film)
        db.session.commit()
        return film.id


def test_add_to_watchlist_nonexistent_film_raises(app, sample_user):
    with app.app_context():
        fake_film_id = "00000000-0000-0000-0000-000000000000"
        with pytest.raises(FilmNotFoundError):
            add_to_watchlist(sample_user, fake_film_id)


def test_add_to_watchlist_duplicate_raises(app, sample_user, sample_film):
    with app.app_context():
        add_to_watchlist(sample_user, sample_film)
        with pytest.raises(AlreadyInWatchlistError):
            add_to_watchlist(sample_user, sample_film)
        assert WatchlistEntry.query.filter_by(
            user_id=sample_user, film_id=sample_film
        ).count() == 1


def test_remove_from_watchlist(app, sample_user, sample_film):
    with app.app_context():
        add_to_watchlist(sample_user, sample_film)
        assert remove_from_watchlist(sample_user, sample_film) is True
        assert WatchlistEntry.query.filter_by(
            user_id=sample_user, film_id=sample_film
        ).first() is None
        with pytest.raises(NotInWatchlistError):
            remove_from_watchlist(sample_user, sample_film)


def test_visibility_toggle(app, sample_user, sample_film):
    with app.app_context():
        entry = add_to_watchlist(sample_user, sample_film, public=False)
        assert entry.public is False


def test_get_watchlist_returns_newest_first(app, sample_user):
    with app.app_context():
        older_film = Film(title="Alien")
        newer_film = Film(title="Blade Runner")
        db.session.add_all([older_film, newer_film])
        db.session.commit()
        db.session.add_all([
            WatchlistEntry(
                user_id=sample_user,
                film_id=older_film.id,
                date_added=datetime.now(timezone.utc) - timedelta(days=1),
            ),
            WatchlistEntry(
                user_id=sample_user,
                film_id=newer_film.id,
                date_added=datetime.now(timezone.utc),
            ),
        ])
        db.session.commit()
        assert [film["title"] for film in get_watchlist(sample_user)] == [
            "Blade Runner",
            "Alien",
        ]
