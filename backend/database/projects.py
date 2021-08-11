from flask_login import current_user
from mongoengine import *
from io import BytesIO
from celery import chain
from config import Config
from flask_socketio import SocketIO

from .tasks import TaskModel

import time
import cv2
import os
import stat
import subprocess

import logging

logger = logging.getLogger("gunicorn.error")


class ProjectModel(DynamicDocument):
    id = SequenceField(primary_key=True)
    name = StringField(required=True, unique=True)
    thumbnail = StringField(default="")

    datasets = ListField(default=[])
    categories = ListField(default=[])

    deleted = BooleanField(default=False)
    deleted_date = DateTimeField()

    owner = StringField(required=True)
    users = ListField(default=[])

    def save(self, *args, **kwargs):
        self.owner = current_user.username if current_user else "system"

        return super(ProjectModel, self).save(*args, **kwargs)

    def get_users(self):
        from .users import UserModel

        members = self.users
        members.append(self.owner)

        return UserModel.objects(username__in=members).exclude(
            "password", "id", "preferences"
        )

    def is_owner(self, user):
        if user.is_admin:
            return True

        if user.is_vtcc:
            return True

        return user.username.lower() == self.owner.lower()

    def can_download(self, user):
        return self.is_owner(user)

    def can_delete(self, user):
        return self.is_owner(user)

    def can_share(self, user):
        return self.is_owner(user)

    def can_generate(self, user):
        return self.is_owner(user)

    def can_edit(self, user):
        return user.username in self.users or self.is_owner(user)

    def permissions(self, user):
        return {
            "owner": self.is_owner(user),
            "edit": self.can_edit(user),
            "share": self.can_share(user),
            "generate": self.can_generate(user),
            "delete": self.can_delete(user),
            "download": self.can_download(user),
        }