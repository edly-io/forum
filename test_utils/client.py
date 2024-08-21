"""
Client utility for testing.
"""

import json
from typing import Any

from django.test import Client


class APIClient(Client):
    """
    Extends the Django test client to include custom methods for sending requests.

    This client sends JSON data with the correct headers.
    """

    def send_request(
        self, method: str, path: str, data: Any, *args: Any, **kwargs: Any
    ) -> Any:
        """
        Send a request with the specified HTTP method and JSON data.

        Args:
            method (str): The HTTP method (e.g., 'GET', 'POST', 'PUT', 'DELETE').
            path (str): The URL path to send the request to.
            data (Optional[dict]): The data to be sent in the request body (if applicable).
            **kwargs: Additional keyword arguments to be passed to the parent method.

        Returns:
            The response object from the request.
        """
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "HTTP_X_API_KEY": "your_api_key",
        }
        if method.lower() in ["post", "put"]:
            data = json.dumps(data) if data else None

        return self.generic(method, path, data, headers=headers, **kwargs)

    def get_json(self, path: str, *args: Any, **kwargs: Any) -> Any:
        """
        Send a GET request.
        """
        return self.send_request("GET", path, None, *args, **kwargs)

    def post_json(self, path: str, data: Any, *args: Any, **kwargs: Any) -> Any:
        """
        Send a POST request with JSON data.
        """
        return self.send_request("POST", path, data, *args, **kwargs)

    def put_json(self, path: str, data: Any, *args: Any, **kwargs: Any) -> Any:
        """
        Send a PUT request with JSON data.
        """
        return self.send_request("PUT", path, data, *args, **kwargs)

    def delete_json(self, path: str, *args: Any, **kwargs: Any) -> Any:
        """
        Send a DELETE request.
        """
        return self.send_request("DELETE", path, None, *args, **kwargs)
