import datetime

from flask_restplus import Namespace, Resource, reqparse
from flask_login import login_required, current_user
from flask import request

from ..util import query_util, coco_util, profile, thumbnails

from config import Config
from database import ImageModel, CategoryModel, AnnotationModel, SessionEvent

import logging, os

logger = logging.getLogger("gunicorn.error")

api = Namespace("annotator", description="Annotator related operations")

image_data = reqparse.RequestParser()
image_data.add_argument("folders", type=list, location="json")


@api.route("/data")
class AnnotatorData(Resource):
    @profile
    @login_required
    def post(self):
        """
        Called when saving data from the annotator client
        """
        data = request.get_json(force=True)
        image = data.get("image")
        dataset = data.get("dataset")
        mode = data.get("mode")
        reviewuser = data.get("reviewuser")
        image_id = image.get("id")

        image_model = ImageModel.objects(id=image_id).first()

        if image_model is None:
            return {"success": False, "message": "Image does not exist"}, 400

        # Check if current user can access dataset
        db_dataset = current_user.datasets.filter(id=image_model.dataset_id).first()
        if dataset is None:
            return {"success": False, "message": "Could not find associated dataset"}

        db_dataset.update(annotate_url=dataset.get("annotate_url", ""))

        categories = CategoryModel.objects.all()
        annotations = AnnotationModel.objects(image_id=image_id)

        annotated = False
        num_annotations = 0
        # Iterate every category passed in the data
        for category in data.get("categories", []):
            category_id = category.get("id")

            # Find corresponding category object in the database
            db_category = categories.filter(id=category_id).first()
            if db_category is None:
                continue

            category_update = {"color": category.get("color")}
            # if current_user.can_edit(db_category):
            #     category_update['keypoint_edges'] = category.get('keypoint_edges', [])
            #     category_update['keypoint_labels'] = category.get('keypoint_labels', [])
            #     category_update['keypoint_colors'] = category.get('keypoint_colors', [])

            db_category.update(**category_update)

            # Iterate every annotation from the data annotations
            for annotation in category.get("annotations", []):
                counted = False
                # Find corresponding annotation object in database
                annotation_id = annotation.get("id")
                db_annotation = annotations.filter(id=annotation_id).first()

                if db_annotation is None:
                    continue

                # Paperjs objects are complex, so they will not always be passed. Therefor we update
                # the annotation twice, checking if the paperjs exists.

                # Update annotation in database
                sessions = []
                total_time = 0
                for session in annotation.get("sessions", []):
                    date = datetime.datetime.fromtimestamp(
                        int(session.get("start")) / 1e3
                    )
                    model = SessionEvent(
                        user=current_user.username,
                        created_at=date,
                        milliseconds=session.get("milliseconds"),
                        tools_used=session.get("tools"),
                    )
                    total_time += session.get("milliseconds")
                    sessions.append(model)

                if annotation.get("label"):
                    counted = True

                db_annotation.update(
                    add_to_set__events=sessions,
                    inc__milliseconds=total_time,
                    set__isbbox=annotation.get("isbbox", False),
                    set__metadata=annotation.get("metadata"),
                    set__color=annotation.get("color"),
                    set__label=annotation.get("label", False),
                    set__subannotations=annotation.get("subannotations", []),
                )

                # Update paperjs if it exists
                paperjs_object = annotation.get("compoundPath", [])
                if len(paperjs_object) == 2:
                    width = db_annotation.width
                    height = db_annotation.height

                    # Generate coco formatted segmentation data
                    segmentation, area, bbox = coco_util.paperjs_to_coco(
                        width, height, paperjs_object
                    )

                    db_annotation.update(
                        set__segmentation=segmentation,
                        set__area=area,
                        set__isbbox=annotation.get("isbbox", False),
                        set__bbox=bbox,
                        set__paper_object=paperjs_object,
                    )

                    if area > 0:
                        counted = True

                if counted:
                    num_annotations += 1

        user_category_ids = image_model.user_category_ids
        user_num_annotations = image_model.user_num_annotations
        user_annotated = image_model.user_annotated

        if mode == "annotate":
            user_category_ids.update(
                {current_user.username: image.get("category_ids", [])}
            )

            user_num_annotations.update({current_user.username: num_annotations})

            user_annotated.update({current_user.username: (num_annotations > 0)})
        elif mode == "review":
            user_category_ids.update({reviewuser: image.get("category_ids", [])})

            user_num_annotations.update({reviewuser: num_annotations})

            user_annotated.update({reviewuser: (num_annotations > 0)})

        image_model.update(
            set__metadata=image.get("metadata", {}),
            # set__annotated=(num_annotations > 0),
            set__user_annotated=user_annotated,
            set__category_ids=image.get("category_ids", []),
            set__user_category_ids=user_category_ids,
            set__num_annotations=num_annotations,
            set__user_num_annotations=user_num_annotations,
        )

        current_user.update(preferences=data.get("user", {}))

        # thumbnails.generate_thumbnail(image_model)

        return {"success": True}


@api.route("/data/<int:image_id>")
class AnnotatorId(Resource):
    @profile
    @login_required
    @api.expect(image_data)
    def get(self, image_id):
        """ Called when loading from the annotator client """
        order = (
            request.args.get("order")
            if request.args.get("order") in ["file_name", "id"]
            else "id"
        )
        user = request.args.get("user", current_user.username)
        mode = request.args.get("mode", "review")
        args = image_data.parse_args()
        folder = request.args.get("folder")

        image = ImageModel.objects(id=image_id).exclude("events").first()

        if image is None:
            return {"success": False, "message": "Could not load image"}, 400

        dataset = current_user.datasets.filter(id=image.dataset_id).first()
        if dataset is None:
            return {
                "success": False,
                "message": "Could not find associated dataset",
            }, 400

        categories = (
            CategoryModel.objects(deleted=False).in_bulk(dataset.categories).items()
        )

        # Get next and previous image
        images = ImageModel.objects(dataset_id=dataset.id, deleted=False)
        directory = os.path.join(dataset.directory, folder)
        if mode == "annotate":
            if order == "file_name":
                pre = (
                    images.filter(
                        path__startswith=directory,
                        file_name__lt=image.file_name,
                        __raw__={f"user_annotated.{user}": {"$ne": True}},
                    )
                    .order_by("-" + order)
                    .first()
                )
                nex = (
                    images.filter(
                        path__startswith=directory,
                        file_name__gt=image.file_name,
                        __raw__={f"user_annotated.{user}": {"$ne": True}},
                    )
                    .order_by(order)
                    .first()
                )
            else:  # order == 'id'
                pre = (
                    images.filter(
                        path__startswith=directory,
                        id__lt=image.id,
                        __raw__={f"user_annotated.{user}": {"$ne": True}},
                    )
                    .order_by("-_" + order)
                    .first()
                )
                nex = (
                    images.filter(
                        path__startswith=directory,
                        id__gt=image.id,
                        __raw__={f"user_annotated.{user}": {"$ne": True}},
                    )
                    .order_by("_" + order)
                    .first()
                )
        else:  # mode == 'review':
            if order == "file_name":
                pre = (
                    images.filter(
                        path__startswith=directory, file_name__lt=image.file_name
                    )
                    .order_by("-" + order)
                    .first()
                )
                nex = (
                    images.filter(
                        path__startswith=directory, file_name__gt=image.file_name
                    )
                    .order_by(order)
                    .first()
                )
            else:  # order == 'id'
                pre = (
                    images.filter(path__startswith=directory, id__lt=image.id)
                    .order_by("-_" + order)
                    .first()
                )
                nex = (
                    images.filter(path__startswith=directory, id__gt=image.id)
                    .order_by("_" + order)
                    .first()
                )

        preferences = {}
        if not Config.LOGIN_DISABLED:
            preferences = current_user.preferences

        # Generate data about the image to return to client
        data = {
            "image": query_util.fix_ids(image),
            "categories": [],
            "dataset": query_util.fix_ids(dataset),
            "preferences": preferences,
            "permissions": {
                "dataset": dataset.permissions(current_user),
                "image": image.permissions(current_user),
            },
        }

        data["image"]["previous"] = pre.id if pre else None
        data["image"]["next"] = nex.id if nex else None

        for category in categories:
            category = query_util.fix_ids(category[1])

            category_id = category.get("id")
            annotations = (
                AnnotationModel.objects(
                    image_id=image_id,
                    category_id=category_id,
                    creator=user,
                    deleted=False,
                )
                .exclude("events")
                .all()
            )

            category["show"] = True
            category["visualize"] = False
            category["annotations"] = (
                [] if annotations is None else query_util.fix_ids(annotations)
            )
            data.get("categories").append(category)

        return data