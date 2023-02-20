from .programs import *
from .schedules import *
from .clients import *
from .auth import *
from ..database import as_dict


def program_to_model(self) -> Program:
    nested_models = {
        "category": Category.construct(name=self.category),
        "placement": Category.construct(name=self.placement),
        "instructor": InstructorPublic.from_orm(self.instructor_obj),
    }
    model = as_dict(self)
    model.update(nested_models)
    return Program(**model)


def record_to_model(self) -> SchemaRecord:
    nested_models = {
        "program": self.program_.to_model()
    }
    model = as_dict(self)
    model.update(nested_models)
    return SchemaRecord(**model)