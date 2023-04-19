from pathlib import Path
from secrets import token_urlsafe
from typing import (
    Optional, Union
)

from fastapi import (
    Depends,
    HTTPException,
    status
)
from fastapi import UploadFile
from sqlalchemy import delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ...database import get_session
from ...settings import settings

from ... import (
    tables,
    models
)


class InstructorService:
    exception = HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail='Номер телефона уже имеется в базе'
    )

    def __init__(
        self,
        session: Session = Depends(get_session)
    ):
        self.session = session

    def _get(
        self,
        instructor_id: int
    ) -> Optional[tables.Instructor]:
        instructor = (
            self.session
            .query(tables.Instructor)
            .filter(tables.Instructor.id == instructor_id)
            .first()
        )
        if not instructor:
            raise HTTPException(status.HTTP_404_NOT_FOUND)
        return instructor

    def get_instructor(
        self,
        instructor_id: int,
        for_public: bool = False
    ) -> Union[models.Instructor, models.InstructorPublic]:
        instructor = self._get(instructor_id)
        if for_public:
            del instructor.phone
            model = models.InstructorPublic.from_orm(instructor)
        else:
            model = models.Instructor.from_orm(instructor)
        if t := instructor.photo_token:
            model.photo_src = f'{settings.images_path}/instructors/{t}.jpg'

        return model

    def get_many(
        self
    ) -> list[models.Instructor]:
        instructors = (
            self.session
            .query(tables.Instructor)
            .all()
        )
        instructors_models = []
        for instructor in instructors:
            model = models.Instructor.from_orm(instructor)
            if t := instructor.photo_token:
                model.photo_src = f'{settings.images_path}/instructors/{t}.jpg'
            instructors_models.append(model)
        return instructors_models

    def create_instructor(
        self,
        instructor_data: models.InstructorCreate
    ) -> tables.Instructor:
        instructor = tables.Instructor(
            **instructor_data.dict()
        )
        try:
            self.session.add(instructor)
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise InstructorService.exception from None
        return instructor

    def upload_image(
        self,
        instructor_id: int,
        image: UploadFile,
    ) -> models.InstructorPublic:
        instructor = self._get(instructor_id)
        if not any([
            image.content_type == 'image/jpeg',
            image.content_type == 'image/png',
        ]):
            raise HTTPException(status.HTTP_400_BAD_REQUEST, detail='Invalid image type')
        upload_dir = Path.cwd() / settings.images_path / 'instructors'
        upload_dir.mkdir(parents=True, exist_ok=True)
        img_token = token_urlsafe(10)
        filename = f'{img_token}.jpg'
        with open(upload_dir / filename, 'wb') as out:
            while content := image.file.read(1024):
                out.write(content)
        if old_img_token := instructor.photo_token:
            (upload_dir / f'{old_img_token}.jpg').unlink(missing_ok=True)
        instructor.photo_token = img_token
        self.session.commit()
        return self.get_instructor(instructor_id, for_public=True)

    def delete_instructor(
        self,
        instructor_id: int
    ):
        instructor = self._get(instructor_id)
        try:
            self.session.execute(delete(tables.Instructor).where(tables.Instructor.id == instructor_id))
            self.session.commit()
        except IntegrityError:
            raise HTTPException(status.HTTP_409_CONFLICT, detail="Инструктор задействован в расписании.")
        return

    def update_instructor(
        self,
        instructor_id: int,
        instructor_data: models.InstructorUpdate
    ) -> tables.Instructor:
        instructor = self._get(instructor_id)
        for field, value in instructor_data:
            setattr(instructor, field, value)
        try:
            self.session.commit()
        except IntegrityError:
            self.session.rollback()
            raise InstructorService.exception from None
        return instructor