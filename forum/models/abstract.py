"""
Database models for forum.
"""
from pymongo import MongoClient
import datetime

client = MongoClient(host='mongodb', port=27017)
db = client['cs_comments_service']

class MongoModel:
    collection_name = None
    default_filter = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def get_collection(cls):
        return db[cls.collection_name]

    def save(self):
        if not hasattr(self, '_id'):
            result = self.get_collection().insert_one(self.__dict__)
            self._id = result.inserted_id
        else:
            self.get_collection().update_one({'_id': self._id}, {'$set': self.__dict__})

    @classmethod
    def find(cls, **kwargs):
        return [cls(**doc) for doc in cls.get_collection().find(kwargs)]

    @classmethod
    def find_one(cls, **kwargs):
        doc = cls.get_collection().find_one(kwargs)
        return cls(**doc) if doc else None
    
    @classmethod
    def count_documents(cls, **kwargs):
        return cls.get_collection().count_documents(kwargs)


class User(MongoModel):
    collection_name = 'users'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.read_states = kwargs.get('read_states') or []
        self.notifications =  kwargs.get('notifications') or []

    def get_read_state_by_course_id(self, course_id):
        for read_state in self.read_states:
            if read_state['course_id'] == course_id:
                return read_state
        return {}
    
    def mark_as_read(self, thread):
        self.read_states[str(thread._id)] = datetime.datetime.utcnow()
        self.save()

    def follow(self, thread):
        if not hasattr(self, 'subscribed_thread_ids'):
            self.subscribed_thread_ids = []
        if thread._id not in self.subscribed_thread_ids:
            self.subscribed_thread_ids.append(thread._id)
            self.save()

    def unfollow(self, thread):
        if hasattr(self, 'subscribed_thread_ids') and thread._id in self.subscribed_thread_ids:
            self.subscribed_thread_ids.remove(thread._id)
            self.save()

    def vote(self, voteable, value):
        if not hasattr(self, 'votes'):
            self.votes = {}
        self.votes[str(voteable._id)] = value
        self.save()
        voteable.vote_count = voteable.vote_count + value
        voteable.save()

class Comment(MongoModel):
    collection_name = 'contents'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.vote_count = self.vote_count or 0
        self.children = []
    
    @classmethod
    def find(cls, **kwargs):
        kwargs['_type'] = 'Comment'
        return cls.get_collection().find(kwargs)
    
    @classmethod
    def count_documents(cls, **kwargs):
        kwargs['_type'] = 'Comment'
        return cls.get_collection().count_documents(kwargs)

    @property
    def thread(self):
        return CommentThread.find_one(_id=self.comment_thread_id)

    def get_parent(self):
        if hasattr(self, 'parent_id'):
            return Comment.find_one(_id=self.parent_id)
        return None

    def get_ancestors(self):
        ancestors = []
        current = self
        while current.get_parent():
            current = current.get_parent()
            ancestors.append(current)
        return ancestors

class CommentThread(MongoModel):
    collection_name = 'contents'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # self.vote_count = self.vote_count or 0
        # self.comment_count = self.comment_count or 0
    
    @classmethod
    def find(cls, **kwargs):
        kwargs['_type'] = 'CommentThread'
        return cls.get_collection().find(kwargs)

    @classmethod
    def count_documents(cls, **kwargs):
        kwargs['_type'] = 'CommentThread'
        return cls.get_collection().count_documents(kwargs)

    def comments(self):
        return Comment.find(comment_thread_id=self._id, parent_id=None)

    def root_comments(self):
        return self.comments()

    def all_comments(self):
        return Comment.find(comment_thread_id=self._id)

    def commenters(self):
        commenter_ids = set(comment.author_id for comment in self.all_comments())
        return User.find(_id={'$in': list(commenter_ids)})
    
