#!/usr/bin/env python3
""" Insert a document in Python
"""


def insert_school(mongo_collection, **kwargs):
        """ insert_school.
            """
                new_doc = mongo_collection.insert_one(kwargs)
                    return new_doc.inserted_id
