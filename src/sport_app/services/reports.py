import datetime
from typing import Optional

from fastapi import (
    Depends,
    HTTPException,
    status
)
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from sqlalchemy.sql import and_

from . import (
    SchemaService,
    ProgramService
)
from ..database import get_session
from .. import (
    tables,
    models,
    utils
)


class ReportsService:
    def __init__(
        self,
        session: Session = Depends(get_session),
    ):
        self.session = session

