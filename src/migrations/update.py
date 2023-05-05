from alembic.config import Config
from alembic import command

from sport_app.database import Session
from sport_app.settings import settings
from sport_app.services.schedules.schedule import ScheduleService, SchemaService
from sport_app.services.auth import AuthService
from sport_app.models import SchemaCreate
from sport_app import tables


alembic_cfg = Config('alembic.ini')
command.upgrade(alembic_cfg, "head")

session = Session()

ScheduleService(session).validate_active_schema()

if not SchemaService(session).active_schema:
    SchemaService(session).create_schema(SchemaCreate(name='my_active'))
    print('INFO  [sport_app] Active schema created')

admin = session.query(tables.Staff).where(tables.Staff.role == tables.Roles.admin).scalar()
if not admin:
    admin = tables.Staff(username=settings.adm_username,
                         email=settings.adm_email,
                         password_hash=AuthService().hash_password(settings.adm_password),
                         role=tables.Roles.admin)
    session.add(admin)
    session.commit()
    print('INFO  [sport_app] Admin account created')

session.close()