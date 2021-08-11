from flask_login import current_user
from mongoengine import *
from io import BytesIO
from celery import chain
from config import Config
from flask_socketio import SocketIO
from werkzeug import secure_filename, FileStorage

from .tasks import TaskModel

import time
import cv2
import os
import stat
import subprocess

import logging

logger = logging.getLogger("gunicorn.error")


class DatasetModel(DynamicDocument):
    PATTERN = (
        ".gif",
        ".png",
        ".jpg",
        ".jpeg",
        ".bmp",
        ".tif",
        ".tiff",
        ".GIF",
        ".PNG",
        ".JPG",
        ".JPEG",
        ".BMP",
        ".TIF",
        ".TIFF",
        ".dcm",
    )
    VIDEO_PATTERN = (".mp4", ".flv", ".avi", ".amv")

    id = SequenceField(primary_key=True)
    name = StringField(required=True, unique=True)
    directory = StringField()
    thumbnails = StringField()
    categories = ListField(default=[])

    project_id = IntField(required=True)

    owner = StringField(required=True)
    users = ListField(default=[])

    annotate_url = StringField(default="")

    default_annotation_metadata = DictField(default={})

    deleted = BooleanField(default=False)
    deleted_date = DateTimeField()

    def save(self, *args, **kwargs):
        directory = os.path.join(Config.DATASET_DIRECTORY, self.name)
        os.makedirs(directory, mode=0o777, exist_ok=True)

        self.directory = directory
        self.owner = current_user.username if current_user else "system"

        return super(DatasetModel, self).save(*args, **kwargs)

    def get_users(self):
        from .users import UserModel

        members = self.users
        members.append(self.owner)

        return UserModel.objects(username__in=members).exclude(
            "password", "id", "preferences"
        )

    def import_coco(self, coco_json):
        from workers.tasks import import_annotations

        task = TaskModel(
            name="Import COCO format into {}".format(self.name),
            dataset_id=self.id,
            group="Annotation Import",
        )
        task.save()

        cel_task = import_annotations.delay(task.id, self.id, coco_json)

        return {"celery_id": cel_task.id, "id": task.id, "name": task.name}

    def export_coco(self, categories=None, user=None, style="COCO"):
        from workers.tasks import export_annotations

        if categories is None or len(categories) == 0:
            categories = self.categories

        task = TaskModel(
            name=f"Exporting {self.name} into {style} format",
            dataset_id=self.id,
            group="Annotation Export",
        )
        task.save()

        cel_task = export_annotations.delay(task.id, self.id, categories, user)

        return {"celery_id": cel_task.id, "id": task.id, "name": task.name}

    def scan(self):
        from workers.tasks import scan_dataset, scan_images

        logger.info("------------> scanning")

        task = TaskModel(
            name=f"Scanning {self.name} for new images",
            dataset_id=self.id,
            group="Directory Image Scan",
        )
        task.save()

        cel_task = scan_dataset.delay(task.id, self.id)

        return {"celery_id": cel_task.id, "id": task.id, "name": task.name}

    def crop_image(self, path):
        img = cv2.imread(path)
        img = img[84:475, 217:584]
        cv2.imwrite(path, img)

    def upload_folders(self, images, **kwargs):
        from workers.tasks import scan_images

        scan_id = kwargs["scan_id"]
        upload_id = kwargs["upload_id"]
        crop = kwargs["crop"]

        task = TaskModel.objects.get(id=upload_id)
        task.update(status="PROGRESS")
        socket = SocketIO(message_queue=Config.BROKER_URL)
        task.info("Begin Uploading")

        total_items = len(images)
        task.set_progress(0, socket=socket)
        for progress, image in enumerate(images):
            dirname = os.path.dirname(image.filename)
            folder_path = os.path.join(self.directory, dirname)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            filename = os.path.split(image.filename)[-1]
            path = os.path.join(self.directory, dirname, secure_filename(filename))
            image.save(path)

            if path.lower().endswith(self.PATTERN):
                if filename.endswith(".dcm"):
                    self.convert_dicom(path)
                    path = os.path.join(
                        self.directory,
                        dirname,
                        secure_filename(filename.replace(".dcm", ".jpg")),
                    )

                if crop == "true":
                    self.crop_image(path)
            elif path.lower().endswith(self.VIDEO_PATTERN):
                try:
                    video_to_images(path)
                    count += 1
                    task.info(f"New file found: {path}")
                except:
                    task.warning(f"Could not read {path}")

            task.set_progress(int((progress + 1) / total_items * 100), socket=socket)

        cel_task = scan_images.delay(scan_id, directory=self.directory, id=self.id)

        task.set_progress(100, socket=socket)
        return {"success": True}

    def upload_images(self, images, **kwargs):
        from workers.tasks import scan_images

        scan_id = kwargs["scan_id"]
        upload_id = kwargs["upload_id"]
        crop = kwargs["crop"]

        task = TaskModel.objects.get(id=upload_id)
        task.update(status="PROGRESS")
        socket = SocketIO(message_queue=Config.BROKER_URL)
        task.info("Begin Uploading")

        total_items = len(images)
        task.set_progress(0, socket=socket)
        for progress, image in enumerate(images):
            path = os.path.join(self.directory, secure_filename(image.filename))
            image.save(path)

            if path.lower().endswith(self.PATTERN):
                if image.filename.endswith(".dcm"):
                    self.convert_dicom(path)
                    path = os.path.join(
                        self.directory,
                        secure_filename(image.filename.replace(".dcm", ".jpg")),
                    )

                if crop == "true":
                    self.crop_image(path)
            elif path.lower().endswith(self.VIDEO_PATTERN):
                try:
                    video_to_images(path)
                    count += 1
                    task.info(f"New file found: {path}")
                except:
                    task.warning(f"Could not read {path}")

            task.set_progress(int((progress + 1) / total_items * 100), socket=socket)

        cel_task = scan_images.delay(scan_id, directory=self.directory, id=self.id)

        task.set_progress(100, socket=socket)
        return {"success": True}

    def convert_dicom(self, path):
        subprocess.call(["./script.sh", path])

    def get_task_id(self):
        task = TaskModel(
            name=f"Uploading {self.name} new images",
            dataset_id=self.id,
            group="Image Upload",
        )
        task.save()

        scan_task = TaskModel(
            name=f"Scanning {self.name} for new images",
            dataset_id=self.id,
            group="Directory Image Scan",
        )
        scan_task.save()

        return {"id": task.id, "scan_id": scan_task.id, "name": task.name}

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


def video_to_images(path):
    cam = cv2.VideoCapture(path)
    root, file = os.path.split(path)
    filename = file.split(".")[0]

    try:
        # directory = os.path.join(root, '')
        directory = os.path.join(root, filename)
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print("Error: Creating directory of data")

    currentframe = 0
    while True:
        ret, frame = cam.read()
        if ret:
            name = os.path.join(directory, filename + "_" + str(currentframe) + ".jpg")
            cv2.imwrite(name, frame)
            currentframe += 1
        else:
            break
        # break # make first frame as thumbnail image

    cam.release()
    cv2.destroyAllWindows()


__all__ = ["DatasetModel"]
