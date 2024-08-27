"""Pagination class for forum api."""

from typing import Any

from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request


class ForumPagination(PageNumberPagination):
    """
    Custom pagination class for thread subscriptions.

    This class allows for custom pagination settings.
    """

    page_size_query_param = "per_page"
    max_page_size = 20

    def get_page_size(self, request: Request) -> int:
        """
        Get the page size from the request's GET parameters.

        If the `per_page` parameter is not provided, use the default page size from settings.
        """
        page_size = request.GET.get("per_page")
        if page_size is None:
            return self.max_page_size
        return min(int(page_size), self.max_page_size)

    def paginate_queryset(
        self, queryset: Any, request: Request, view: Any = None
    ) -> Any:
        """
        Paginate the queryset.

        If the page is invalid, return a custom error response instead of raising a 404 error.
        """
        try:
            return super().paginate_queryset(queryset, request, view)
        except NotFound:
            return []
