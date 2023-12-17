"""This module defines the HttpClient abstract base class."""


import abc

from ..entities import artefact


class WebhookClient(abc.ABC):
    """Abstract base class for making HTTP requests.

    This class is used to abstract away how HTTP requests are made.
    """

    @abc.abstractmethod
    def post_json(self, webhook_url: str, manifest: artefact.Manifest) -> None:
        """Make a POST request with JSON content type."""
        raise NotImplementedError
