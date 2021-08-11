from database import (
    ImageModel,
    TaskModel,
    DatasetModel
)

from celery import shared_task
from ..socket import create_socket
# from ..videos import video_to_images
from .thumbnails import thumbnail_generate_single_image

import os, cv2


@shared_task
def scan_dataset(task_id, dataset_id):
    task = TaskModel.objects.get(id=task_id)
    dataset = DatasetModel.objects.get(id=dataset_id)

    task.update(status="PROGRESS")
    socket = create_socket()

    toplevel = list(os.listdir(dataset.directory))
    task.info(f"Scanning {dataset.directory}")

    count = 0
    for root, dirs, files in os.walk(dataset.directory):
        try:
            youarehere = toplevel.index(root.split('/')[-1])
            progress = int((youarehere / len(toplevel)) * 100)
            task.set_progress(progress, socket=socket)
        except:
            pass

        if root.split('/')[-1].startswith('.'):
            continue
        
        for file in files:
            path = os.path.join(root, file)

            if path.lower().endswith(ImageModel.PATTERN):
                db_image = ImageModel.objects(path=path).first()
                if db_image is not None:
                    continue

                try:
                    image = ImageModel.create_from_path(path, dataset.id).save()
                    # thumbnail_generate_single_image.delay(image.id)
                    count += 1
                    task.info(f"New file found: {path}")
                except:
                    task.warning(f"Could not read {path}")
            # elif path.lower().endswith(ImageModel.VIDEO_PATTERN):
            #     try:
            #         video_to_images(path)
            #         count += 1
            #         task.info(f"New file found: {path}")
            #     except:
            #         task.warning(f"Could not read {path}")

    task.info(f"Created {count} new image(s)")
    task.set_progress(100, socket=socket)


__all__ = ["scan_dataset"]