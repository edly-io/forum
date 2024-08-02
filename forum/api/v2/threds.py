# views.py
from pymongo import MongoClient

from rest_framework import viewsets, status
from rest_framework.response import Response
from django.conf import settings
from .serializers import CommentThreadSerializer
from forum.models.abstract import Comment, CommentThread, User


class CommentThreadViewSet(viewsets.ViewSet):
    def get_sort_criteria(self, sort_key):
        sort_key_mapper = {
            "date": "created_at",
            "activity": "last_activity_at",
            "votes": "votes.point",
            "comments": "comment_count",
        }

        sort_key = sort_key_mapper.get(sort_key, "date")

        if sort_key:
            # only sort order of :desc is supported.  support for :asc would require new indices.
            sort_criteria = [("pinned", -1), (sort_key, -1)]
            if sort_key not in ["created_at", "last_activity_at"]:
                sort_criteria.append(("created_at", -1))
            return sort_criteria
        else:
            return None
    
    def list(self, request):
        page = 1
        per_page = 10
        raw_query = True

        params = request.query_params

        sort_key = 'date'
        filter_unread = True
       

        query = {"context": "course"}

        if course_id := params.get("course_id"):
            query["course_id"] = course_id

        if group_ids := params.get("group_ids"):
            query["group_id"] = {"$in": group_ids}

        if author_id := params.get("author_id"):
            query["author_id"] = author_id
            if author_id != params.get("user_id"):
                query["anonymous"] = False
                query["anonymous_to_peers"] = False

        if thread_type := params.get("thread_type"):
            query["thread_type"] = thread_type

        if params.get("filter_flagged") == "true":
            comment_ids = Comment.find(
                {"course_id": course_id, "abuse_flaggers": {"$ne": [], "$exists": True}}
            ).distinct("comment_thread_id")
            thread_ids = CommentThread.find(
                {"abuse_flaggers": {"$ne": [], "$exists": True}}
            ).distinct("_id")
            combined_ids = list(set(comment_ids + thread_ids))
            query["_id"] = {"$in": combined_ids}

        if params.get("filter_unresponded") == "true":
            query["comment_count"] = 0

        threads = CommentThread.find(**query)

        sort_criteria = self.get_sort_criteria(sort_key)
        
        if sort_criteria:
            threads = threads.sort(sort_criteria)

        thread_count = CommentThread.count_documents()

        if filter_unread:
            request_user = None
            if user_id:=params.get('user_id'):
                request_user = User.find_one(_id=user_id)
            if request_user:
                read_state = request_user.get_read_state_by_course_id(course_id)
                read_dates = read_state.get("last_read_times", {})
                
                # TODO: When calling the threads.batch_size it loads the data and threads got empty.
                skipped = 0
                to_skip = (page - 1) * per_page
                has_more = False
                batch_size = 100  # or some other reasonable value
                filtered_threads = []
                for thread in threads.batch_size(batch_size):
                    thread_key = str(thread["_id"])
                    if thread_key not in read_dates or read_dates[thread_key] < thread["last_activity_at"]:
                        if raw_query:
                            filtered_threads.append(thread)
                        elif skipped >= to_skip:
                            if len(threads) == per_page:
                                has_more = True
                                break
                            filtered_threads.append(thread)
                        else:
                            skipped += 1
                threads = filtered_threads
                num_pages = page + 1 if has_more else page
            else:
                threads = threads.skip((page - 1) * per_page).limit(per_page)
                num_pages = max(1, (thread_count + per_page - 1) // per_page)
        else:
            threads = threads.skip((page - 1) * per_page).limit(per_page)
            num_pages = max(1, (thread_count + per_page - 1) // per_page)

        serializered_threads = CommentThreadSerializer(threads, many=True)
        
        result = {
            "collection": serializered_threads.data,
            "num_pages": num_pages,
            "page": page,
            "thread_count": thread_count
        }
        return Response(result)
