"""
Client utility for testing.
"""

import json
from typing import Any

from django.test import Client


class APIClient(Client):
    """
    Extends the Django test client to include a custom PUT method.

    This client sends JSON data with the correct headers.
    """

    def put_json(self, path: str, data: Any, *args: Any, **kwargs: Any):  # type: ignore
        """
        Send a PUT request with JSON data.

        Args:
            path (str): The URL path to send the request to.
            data (dict): The data to be sent in the request body.
            **kwargs: Additional keyword arguments to be passed to the parent method.

        Returns:
            The response object from the request.
        """
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "HTTP_X_API_KEY": "your_api_key",
        }
        return self.put(path, data=json.dumps(data), headers=headers, **kwargs)
