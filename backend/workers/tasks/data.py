from database import (
    fix_ids,
    ImageModel,
    CategoryModel,
    AnnotationModel,
    DatasetModel,
    TaskModel,
    ExportModel
)

# import pycocotools.mask as mask
import numpy as np
import time
import json
import os
import subprocess
import zipfile
import shutil

from celery import shared_task
from ..socket import create_socket
# from ..videos import video_to_images
from .thumbnails import thumbnail_generate_single_image
from mongoengine import Q
from werkzeug import secure_filename, FileStorage

import logging
logger = logging.getLogger('gunicorn.error')


@shared_task
def export_annotations(task_id, dataset_id, categories, user):
    task = TaskModel.objects.get(id=task_id)
    dataset = DatasetModel.objects.get(id=dataset_id)

    task.update(status="PROGRESS")
    socket = create_socket()

    task.info("Beginning Export (COCO Format)")

    db_categories = CategoryModel.objects(id__in=categories, deleted=False) \
        .only(*["id", "name", "color", "classified", "subcategory"])
    db_images = ImageModel.objects(deleted=False, dataset_id=dataset.id) \
        .only(*["id", "width", "height", "file_name", "path", "dataset_id"])
    db_annotations = AnnotationModel.objects(
        deleted=False, category_id__in=categories, creator=user)

    total_items = db_categories.count()

    coco = {
        'images': [],
        'categories': [],
        'annotations': []
    }

    total_items += db_images.count()
    progress = 0

    # iterate though all categoires and upsert
    category_names = []
    for category in fix_ids(db_categories):
        task.info(f"Adding category: {category.get('name')}")
        coco.get('categories').append(category)
        category_names.append(category.get('name'))

        progress += 1
        task.set_progress((progress / total_items) * 100, socket=socket)

    total_annotations = db_annotations.count()
    total_images = db_images.count()
    for image in fix_ids(db_images):
        progress += 1
        task.set_progress((progress / total_items) * 100, socket=socket)

        annotations = db_annotations.filter(image_id=image.get('id'))\
            .only(*["id", "image_id", "category_id", "segmentation",
                    "color", "area", "bbox", "isbbox", "label", "subannotations"])
        annotations = fix_ids(annotations)

        if len(annotations) == 0:
            continue

        num_annotations = 0
        for annotation in annotations:
            has_segmentation = len(annotation.get('segmentation', [])) > 0
            has_classfied = annotation.get('label')

            if has_segmentation or has_classfied:
                if 'keypoints' in annotation:
                    del annotation['keypoints']

                num_annotations += 1
                coco.get('annotations').append(annotation)

        task.info(
            f"Exporting {num_annotations} annotations for image {image.get('id')}")
        coco.get('images').append(image)

    task.info(
        f"Done export {total_annotations} annotations and {total_images} images from {dataset.name}")

    timestamp = time.time()
    directory = f"{dataset.directory}/{dataset.name}.exports/"
    export_path = f"{directory}coco-{timestamp}.json"

    if not os.path.exists(directory):
        os.makedirs(directory)

    if len(os.listdir(directory)) > 0:
        shutil.rmtree(directory, ignore_errors=True)
        os.makedirs(directory)

    task.info(f"Writing export to file {export_path}")
    with open(export_path, 'w') as fp:
        json.dump(coco, fp)

    storage = 'datasets/zip_storage/'
    if not os.path.exists(storage):
        os.makedirs(storage)

    zip_path = f'{storage}{dataset.name}-{timestamp}.zip'
    zipf = zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED)
    zipdir(dataset.directory, zipf)
    zipf.close()

    if os.path.exists(export_path):
        os.remove(export_path)

    task.info("Creating export object")
    export = ExportModel(dataset_id=dataset.id, path=zip_path, tags=[
                         "COCO", *category_names])
    export.save()

    task.set_progress(100, socket=socket)


def zipdir(path, ziph):
    # ziph is zipfile handle
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), os.path.join(path, '..')))

@shared_task
def import_annotations(task_id, dataset_id, coco_json):
    task = TaskModel.objects.get(id=task_id)
    dataset = DatasetModel.objects.get(id=dataset_id)

    task.update(status="PROGRESS")
    socket = create_socket()

    task.info("Beginning Import")

    images = ImageModel.objects(dataset_id=dataset.id)
    categories = CategoryModel.objects

    coco_images = coco_json.get('images', [])
    coco_annotations = coco_json.get('annotations', [])
    coco_categories = coco_json.get('categories', [])

    task.info(f"Importing {len(coco_categories)} categories, "
              f"{len(coco_images)} images, and "
              f"{len(coco_annotations)} annotations")

    total_items = sum([
        len(coco_categories),
        len(coco_annotations),
        len(coco_images)
    ])
    progress = 0

    task.info("===== Importing Categories =====")
    # category id mapping  ( file : database )
    categories_id = {}

    # Create any missing categories
    for category in coco_categories:
        category_name = category.get('name')
        category_id = category.get('id')
        category_model = categories.filter(name__iexact=category_name).first()

        if category_model is None:
            task.warning(
                f"{category_name} category not found (creating a new one)")

            new_category = CategoryModel(
                name=category_name,
                keypoint_edges=category.get('skeleton', []),
                keypoint_labels=category.get('keypoints', [])
            )
            new_category.save()

            category_model = new_category
            dataset.categories.append(new_category.id)

        task.info(f"{category_name} category found")
        # map category ids
        categories_id[category_id] = category_model.id

        # update progress
        progress += 1
        task.set_progress((progress / total_items) * 100, socket=socket)

    dataset.update(set__categories=dataset.categories)

    task.info("===== Loading Images =====")
    # image id mapping ( file: database )
    images_id = {}
    categories_by_image = {}

    # Find all images
    for image in coco_images:
        image_id = image.get('id')
        image_filename = image.get('file_name')

        # update progress
        progress += 1
        task.set_progress((progress / total_items) * 100, socket=socket)

        image_model = images.filter(file_name__exact=image_filename).all()

        if len(image_model) == 0:
            task.warning(f"Could not find image {image_filename}")
            continue

        if len(image_model) > 1:
            task.error(
                f"Too many images found with the same file name: {image_filename}")
            continue

        task.info(f"Image {image_filename} found")
        image_model = image_model[0]
        images_id[image_id] = image_model
        categories_by_image[image_id] = list()

    task.info("===== Import Annotations =====")
    for annotation in coco_annotations:
        image_id = annotation.get('image_id')
        category_id = annotation.get('category_id')
        segmentation = annotation.get('segmentation', [])
        keypoints = annotation.get('keypoints', [])
        # is_crowd = annotation.get('iscrowed', False)
        area = annotation.get('area', 0)
        bbox = annotation.get('bbox', [0, 0, 0, 0])
        isbbox = annotation.get('isbbox', False)

        progress += 1
        task.set_progress((progress / total_items) * 100, socket=socket)

        has_segmentation = len(segmentation) > 0
        has_keypoints = len(keypoints) > 0
        if not has_segmentation and not has_keypoints:
            task.warning(
                f"Annotation {annotation.get('id')} has no segmentation or keypoints")
            continue

        try:
            image_model = images_id[image_id]
            category_model_id = categories_id[category_id]
            image_categories = categories_by_image[image_id]
        except KeyError:
            task.warning(
                f"Could not find image associated with annotation {annotation.get('id')}")
            continue

        annotation_model = AnnotationModel.objects(
            image_id=image_model.id,
            category_id=category_model_id,
            segmentation=segmentation,
            keypoints=keypoints
        ).first()

        if annotation_model is None:
            task.info(f"Creating annotation data ({image_id}, {category_id})")

            annotation_model = AnnotationModel(image_id=image_model.id)
            annotation_model.category_id = category_model_id

            annotation_model.color = annotation.get('color')
            annotation_model.metadata = annotation.get('metadata', {})

            if has_segmentation:
                annotation_model.segmentation = segmentation
                annotation_model.area = area
                annotation_model.bbox = bbox

            if has_keypoints:
                annotation_model.keypoints = keypoints

            annotation_model.isbbox = isbbox
            annotation_model.save()

            image_categories.append(category_id)
        else:
            annotation_model.update(deleted=False, isbbox=isbbox)
            task.info(
                f"Annotation already exists (i:{image_id}, c:{category_id})")

    for image_id in images_id:
        image_model = images_id[image_id]
        category_ids = categories_by_image[image_id]
        all_category_ids = list(image_model.category_ids)
        all_category_ids += category_ids

        num_annotations = AnnotationModel.objects(
            Q(image_id=image_id) & Q(deleted=False) &
            (Q(area__gt=0) | Q(keypoints__size__gt=0))
        ).count()

        image_model.update(
            set__annotated=True,
            set__category_ids=list(set(all_category_ids)),
            set__num_annotations=num_annotations
        )

    task.set_progress(100, socket=socket)


@shared_task
def scan_images(scan_id, **kwargs):
    dataset_directory = kwargs['directory']
    dataset_id = kwargs['id']

    task = TaskModel.objects.get(id=scan_id)
    task.update(status="PROGRESS")
    socket = create_socket()

    toplevel = list(os.listdir(dataset_directory))
    task.info(f"Scanning {dataset_directory}")

    count = 0
    for root, dirs, files in os.walk(dataset_directory):
        if root.split('/')[-1].startswith('.'):
            continue

        try:
            youarehere = toplevel.index(root.split('/')[-1])
            progress = int((youarehere / len(toplevel)) * 100)
            task.set_progress(progress, socket=socket)
        except:
            pass

        
        for file in files:
            path = os.path.join(root, file)
            if path.lower().endswith(ImageModel.PATTERN):
                db_image = ImageModel.objects(path=path, deleted=False).first()
                if db_image is not None:
                    continue

                try:
                    ImageModel.create_from_path(path, dataset_id).save()
                    # thumbnail_generate_single_image.delay(image.id)
                    count += 1
                    task.info(f"New file found: {path}")
                except:
                    task.warning(f"Could not read {path}")
            # elif path.lower().endswith(ImageModel.VIDEO_PATTERN):
            #     try:
            #         video_to_images(path, task)
            #         count += 1
            #         task.info(f"New file found: {path}")
            #     except:
            #         task.warning(f"Could not read {path}")

    task.info(f"Created {count} new image(s)")
    task.set_progress(100, socket=socket)


@shared_task
def convert_dicom(path):
    subprocess.call(['./script.sh', path])

__all__ = ["export_annotations", "import_annotations", "scan_images", "convert_dicom"]
