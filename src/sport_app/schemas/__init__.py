from .classes import *
from .schedules import *
from ..database import as_dict


def class_to_schema(self) -> Class:
    nested_models = {
        "category": Category.construct(name=self.category),
        "placement": Category.construct(name=self.placement),
        "instructor": InstructorPublic.from_orm(self.instructor_),
    }
    schema = as_dict(self)
    schema.update(nested_models)
    return Class(**schema)


def record_to_schema(self) -> SchemaRecord:
    nested_models = {
        "Class": self.class_.to_schema()
    }
    schema = as_dict(self)
    schema.update(nested_models)
    return SchemaRecord(**schema)