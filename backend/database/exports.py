from mongoengine import *

import datetime
import time
import os


class ExportModel(DynamicDocument):
    id = SequenceField(primary_key=True)
    dataset_id = IntField(required=True)
    path = StringField(required=True)
    tags = ListField(default=[])
    categories = ListField(default=[])
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    
    def get_file(self):
        return

    def remove_zip_file(self):
        if os.path.exists(self.path):
            os.remove(self.path)


__all__ = ["ExportModel"]