"""Subscriptions API Views."""

import logging
import math
from typing import Any

from rest_framework import status
from rest_framework.exceptions import ParseError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from forum.api import retrieve_user
from forum.constants import FORUM_DEFAULT_PAGE, FORUM_DEFAULT_PER_PAGE
from forum.backends.mongodb import CommentThread, Contents, Users
from forum.backends.mongodb.api import (
    find_or_create_user,
    get_user_by_username,
    handle_threads_query,
    mark_as_read,
    replace_username_in_all_content,
    retire_all_content,
    unsubscribe_all,
    update_all_users_in_course,
    user_to_hash,
)
from forum.serializers.thread import ThreadSerializer
from forum.serializers.users import UserSerializer
from forum.utils import get_group_ids_from_params
from forum.utils import ForumV2RequestError

log = logging.getLogger(__name__)


class UserAPIView(APIView):
    """Users API View."""

    permission_classes = (AllowAny,)

    def get(self, request: Request, user_id: str) -> Response:
        """Get user data."""
        params: dict[str, Any] = request.GET.dict()
        try:
            user_data: dict[str, Any] = retrieve_user(user_id, params)
        except ForumV2RequestError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

        return Response(user_data, status=status.HTTP_200_OK)

    def put(self, request: Request, user_id: str) -> Response:
        """Update user data."""
        params = request.data
        user = Users().get(user_id)
        username = params.get("username")
        user_by_username = get_user_by_username(username)
        if user and user_by_username:
            if user["external_id"] != user_by_username["external_id"]:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        elif user_by_username:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            user_id = find_or_create_user(user_id)
        Users().update(
            user_id,
            username=username,
            default_sort_key=params.get("default_sort_key"),
        )

        updated_user = Users().get(user_id)
        if not updated_user:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        hashed_user = user_to_hash(updated_user, params)
        serializer = UserSerializer(hashed_user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserCreateAPIView(APIView):
    """Create users api."""

    permission_classes = (AllowAny,)

    def post(self, request: Request) -> Response:
        """Create user."""
        params = request.data
        for key in params:
            if key not in ["id", "username"]:
                return Response(
                    {"error": f"Invalid parameter: {key}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        user_by_id = Users().get(params["id"])
        user_by_username = get_user_by_username(params["username"])
        if user_by_id or user_by_username:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        Users().insert(
            external_id=params["id"],
            username=params["username"],
        )
        new_user = Users().get(params["id"])
        if not new_user:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        hashed_user = user_to_hash(new_user, params)
        return Response(hashed_user, status=status.HTTP_200_OK)


class UserEditAPIView(APIView):
    """Edit user api."""

    def post(self, request: Request, user_id: str) -> Response:
        """Edit user."""
        error_500_response = Response(
            {"message": "Missing new_username param."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
        try:
            params = request.data
        except ParseError:
            return error_500_response
        new_username = params.get("new_username")
        if not new_username:
            return error_500_response
        user = Users().get(user_id)
        if not user:
            return Response(
                {"message": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        Users().update(user_id, username=new_username)
        replace_username_in_all_content(user_id, new_username)
        return Response(status=status.HTTP_200_OK)


class UserRetireAPIView(APIView):
    """Retire user api."""

    permission_classes = (AllowAny,)

    def post(self, request: Request, user_id: str) -> Response:
        """Retire user."""
        error_500_response = Response(
            {"message": "Missing retired_username param."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
        try:
            params = request.data
        except ParseError:
            return error_500_response
        retired_username = params.get("retired_username")
        if not retired_username:
            return error_500_response
        user = Users().get(user_id)
        if not user:
            return Response(
                {"message": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        Users().update(
            user_id,
            email="",
            username=retired_username,
            read_states=[],
        )
        unsubscribe_all(user_id)
        retire_all_content(user_id, retired_username)
        return Response(status=status.HTTP_200_OK)


class UserReadAPIView(APIView):
    """User read api."""

    permission_classes = (AllowAny,)

    def post(self, request: Request, user_id: str) -> Response:
        """User read."""
        params = request.data
        source = params.get("source_id", "")
        thread = CommentThread().get(source)
        if not thread:
            return Response(
                {"message": "Source not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        user = Users().get(user_id)
        if not user:
            return Response(
                {"message": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        mark_as_read(user, thread)
        user = Users().get(user_id)
        if not user:
            return Response(
                {"message": "User not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        hashed_user = user_to_hash(user, params)
        serializer = UserSerializer(hashed_user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserActiveThreadsAPIView(APIView):
    """User active threads api."""

    permission_classes = (AllowAny,)

    def get(self, request: Request, user_id: str) -> Response:
        """User active threads."""
        params = request.GET.dict()
        course_id = params.get("course_id", None)
        if not course_id:
            return Response(
                {},
                status=status.HTTP_200_OK,
            )
        sort_key = params.get("sort_key", "user_activity")
        raw_query = bool(sort_key == "user_activity")
        count_flagged = bool(params.get("count_flagged", "").lower())
        filter_flagged = bool(params.get("flagged", "").lower())
        active_contents = list(
            Contents().get_list(
                author_id=user_id,
                anonymous=False,
                anonymous_to_peers=False,
                course_id=course_id,
            )
        )

        if filter_flagged:
            active_contents = [
                content
                for content in active_contents
                if content["abuse_flaggers"] and len(content["abuse_flaggers"]) > 0
            ]
        active_contents = sorted(
            active_contents, key=lambda x: x["updated_at"], reverse=True
        )
        active_thread_ids = [
            (
                content["comment_thread_id"]
                if content["_type"] == "Comment"
                else content["_id"]
            )
            for content in active_contents
        ]
        active_thread_ids = list(set(active_thread_ids))

        data = handle_threads_query(
            active_thread_ids,
            user_id,
            course_id,
            group_ids=[],
            author_id="",
            thread_type="",
            filter_flagged=False,
            filter_unread=bool(params.get("unread")) or False,
            filter_unanswered=bool(params.get("unanswered")) or False,
            filter_unresponded=bool(params.get("unanswered")) or False,
            count_flagged=count_flagged,
            sort_key=sort_key,
            page=int(request.GET.get("page", FORUM_DEFAULT_PAGE)),
            per_page=int(request.GET.get("per_page", FORUM_DEFAULT_PER_PAGE)),
            context="course",
            raw_query=raw_query,
        )
        if collections := data.get("collection"):
            thread_serializer = ThreadSerializer(
                collections,
                many=True,
                context={
                    "count_flagged": True,
                    "include_endorsed": True,
                    "include_read_state": True,
                },
            )
            data["collection"] = thread_serializer.data
        else:
            collection = data.get("result", [])
            for thread in collection:
                thread["_id"] = str(thread.pop("_id"))
                thread["type"] = str(thread.get("_type", "")).lower()
            data["collection"] = ThreadSerializer(collection, many=True).data
        return Response(data)


class UserCourseStatsAPIView(APIView):
    """User Course stats API."""

    permission_classes = (AllowAny,)

    def _create_pipeline(
        self, course_id: str, page: int, per_page: int, sort_criterion: dict[str, Any]
    ) -> list[dict[str, Any]]:
        """Get pipeline for course stats api."""
        pipeline: list[dict[str, Any]] = [
            {"$match": {"course_stats.course_id": course_id}},
            {"$project": {"username": 1, "course_stats": 1}},
            {"$unwind": "$course_stats"},
            {"$match": {"course_stats.course_id": course_id}},
            {"$sort": sort_criterion},
            {
                "$facet": {
                    "pagination": [{"$count": "total_count"}],
                    "data": [
                        {"$skip": (page - 1) * per_page},
                        {"$limit": per_page},
                    ],
                }
            },
        ]
        return pipeline

    def _get_sort_criterion(self, sort_by: str) -> dict[str, Any]:
        """Get sort criterion based on sort_by parameter."""
        if sort_by == "flagged":
            return {
                "course_stats.active_flags": -1,
                "course_stats.inactive_flags": -1,
                "username": -1,
            }
        elif sort_by == "recency":
            return {
                "course_stats.last_activity_at": -1,
                "username": -1,
            }
        else:
            return {
                "course_stats.threads": -1,
                "course_stats.responses": -1,
                "course_stats.replies": -1,
                "username": -1,
            }

    def _get_paginated_stats(
        self, course_id: str, page: int, per_page: int, sort_criterion: dict[str, Any]
    ) -> dict[str, Any]:
        """Get paginated stats for a course."""
        pipeline = self._create_pipeline(course_id, page, per_page, sort_criterion)
        return list(Users().aggregate(pipeline))[0]

    def _get_user_data(
        self, user_stats: dict[str, Any], exclude_from_stats: list[str]
    ) -> dict[str, Any]:
        """Get user data from user stats."""
        user_data = {"username": user_stats["username"]}
        for k, v in user_stats["course_stats"].items():
            if k not in exclude_from_stats:
                user_data[k] = v
        return user_data

    def _get_stats_for_usernames(
        self, course_id: str, usernames: list[str]
    ) -> list[dict[str, Any]]:
        """Get stats for specific usernames."""
        users = Users().get_list()
        stats_query = []
        for user in users:
            if user["username"] not in usernames:
                continue
            course_stats = user["course_stats"]
            if course_stats:
                for course_stat in course_stats:
                    if course_stat["course_id"] == course_id:
                        stats_query.append(
                            {"username": user["username"], "course_stats": course_stat}
                        )
                        break
        return sorted(stats_query, key=lambda u: usernames.index(u["username"]))

    def get(self, request: Request, course_id: str) -> Response:
        """Get user course stats."""
        params = request.GET.dict()
        page = int(request.GET.get("page", FORUM_DEFAULT_PAGE))
        per_page = int(request.GET.get("per_page", FORUM_DEFAULT_PER_PAGE))
        with_timestamps = bool(params.get("with_timestamps", False))
        sort_by = params.get("sort_key", "")
        usernames_list = params.get("usernames")
        data = []
        usernames = None
        if usernames_list:
            usernames = usernames_list.split(",")

        sort_criterion = self._get_sort_criterion(sort_by)
        exclude_from_stats = ["_id", "course_id"]
        if not with_timestamps:
            exclude_from_stats.append("last_activity_at")

        if not usernames:
            paginated_stats = self._get_paginated_stats(
                course_id, page, per_page, sort_criterion
            )
            num_pages = 0
            page = 0
            total_count = 0
            if paginated_stats.get("pagination"):
                total_count = paginated_stats["pagination"][0]["total_count"]
                num_pages = max(1, math.ceil(total_count / per_page))
                data = [
                    self._get_user_data(user_stats, exclude_from_stats)
                    for user_stats in paginated_stats["data"]
                ]
        else:
            stats_query = self._get_stats_for_usernames(course_id, usernames)
            total_count = len(stats_query)
            num_pages = 1
            data = [
                {
                    "username": user_stats["username"],
                    **{
                        k: v
                        for k, v in user_stats["course_stats"].items()
                        if k not in exclude_from_stats
                    },
                }
                for user_stats in stats_query
            ]

        response = {
            "user_stats": data,
            "num_pages": num_pages,
            "page": page,
            "count": total_count,
        }
        return Response(response, status=status.HTTP_200_OK)

    def post(self, request: Request, course_id: str) -> Response:
        """Update user stats for a course."""
        updated_users = update_all_users_in_course(course_id)
        return Response({"user_count": len(updated_users)}, status=status.HTTP_200_OK)
