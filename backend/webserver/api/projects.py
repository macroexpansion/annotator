from flask import request
from flask_restplus import Namespace, Resource, reqparse
from flask_login import login_required, current_user
from werkzeug.datastructures import FileStorage
from mongoengine.errors import NotUniqueError
from mongoengine.queryset.visitor import Q
from threading import Thread

from google_images_download import google_images_download as gid

from ..util.pagination_util import Pagination
from ..util import query_util, coco_util, profile

from database import (
    DatasetModel,
    CategoryModel,
    ProjectModel
)

import datetime
import json
import os

import logging
logger = logging.getLogger('gunicorn.error')

api = Namespace('project', description='Project related operations')


create_project = reqparse.RequestParser()
create_project.add_argument('name', required=True)

page_data = reqparse.RequestParser()
page_data.add_argument('page', default=1, type=int)
page_data.add_argument('limit', default=20, type=int)
page_data.add_argument('folder', default='', help='Folder for data')
page_data.add_argument('order', default='file_name', help='Order to display images')

delete_data = reqparse.RequestParser()
delete_data.add_argument('fully', default=False, type=bool,
                         help="Fully delete dataset (no undo)")


update_project = reqparse.RequestParser()
update_project.add_argument('name', required=True, location='json', type=str, default=None)

share = reqparse.RequestParser()
share.add_argument('users', location='json', type=list, default=[], help="List of users")


@api.route('/')
class Project(Resource):
    @login_required
    def get(self):
        """ Returns all projects """
        return query_util.fix_ids(current_user.projects.filter(deleted=False).all())

    @api.expect(create_project)
    @login_required
    def post(self):
        """ Creates a project """
        args = create_project.parse_args()
        name = args['name']

        try:
            project = ProjectModel(name=name)
            project.save()
        except NotUniqueError:
            return {'message': 'Project already exists. Check the undo tab to fully delete the project.'}, 400

        return query_util.fix_ids(project)


@api.route('/<int:project_id>')
class ProjectId(Resource):
    @login_required
    def get(self, project_id):
        """ Get project by ID """
        project = current_user.projects.filter(id=project_id, deleted=False).first()
        if project is None:
            return {"message": "Invalid project id"}, 400

        # users = project.get_users()
        return query_util.fix_ids(project)

    @login_required
    def delete(self, project_id):
        """ Deletes project by ID (only owners)"""
        project = ProjectModel.objects(id=project_id, deleted=False).first()
        if project is None:
            return {"message": "Invalid project id"}, 400
        
        if not current_user.can_delete(project):
            return {"message": "You do not have permission to delete the project"}, 403

        project.update(set__deleted=True, set__deleted_date=datetime.datetime.now())
        return {"success": True}

    @api.expect(update_project)
    def post(self, project_id):
        """ Updates project by ID """
        project = current_user.projects.filter(id=project_id, deleted=False).first()
        if project is None:
            return {"message": "Invalid project id"}, 400

        args = update_project.parse_args()
        name = args.get('name', None)

        if len(name) == 0 or name is None:
            return {"message": "Update error"}, 400

        if not current_user.can_delete(project):
            return {"message": "You do not have permission to delete the project"}, 403

        project.update(
            name=name
        )

        return {"success": True}


@api.route('/<int:project_id>/share')
class ProjectIdShare(Resource):
    @api.expect(share)
    @login_required
    def post(self, project_id):
        args = share.parse_args()

        project = current_user.projects.filter(id=project_id, deleted=False).first()
        datasets = current_user.datasets.filter(project_id=project_id).all()
        if project is None:
            return {"message": "Invalid project id"}, 400

        if not project.is_owner(current_user):
            return {"message": "You do not have permission to share this project"}, 403

        project.update(users=args.get('users'))
        if datasets is not None:
            datasets.update(__raw__={'$set': { 'users': args.get('users') }})

        return {"success": True}