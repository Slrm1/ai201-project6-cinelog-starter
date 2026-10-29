"""Domain exceptions shared by CineLog service modules."""


class FilmNotFoundError(Exception):
    """Raised when a film ID does not exist."""


class AlreadyInCollectionError(Exception):
    """Raised when a film is already in a user's collection."""


class NotInCollectionError(Exception):
    """Raised when a film is not in a user's collection."""


class AlreadyInWatchlistError(Exception):
    """Raised when a film is already on a user's watchlist."""


class NotInWatchlistError(Exception):
    """Raised when a film is not on a user's watchlist."""
