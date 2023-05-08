from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from . import api
from .settings import settings

# for development purposes
from fastapi.responses import FileResponse
from pathlib import Path
# __END


def use_route_names_as_operation_ids(app: FastAPI) -> None:
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name


tags_metadata = [
    {
        'name': 'categories',
        'description': 'Операции над категориями',
    },
    {
        'name': 'placements',
        'description': 'Операции над помещениями',
    },
    {
        'name': 'instructors',
        'description': 'Операции над инструкторами',
    },
    {
        'name': 'programs',
        'description': 'Операции над программами',
    },
    {
        'name': 'schedule schemas',
        'description': 'Операции над схемами расписания',
    },
    {
        'name': 'records',
        'description': 'Операции над элементами расписания',
    },
    {
        'name': 'schedule',
        'description': 'Получение расписания',
    },
    {
        'name': 'clients',
        'description': 'Операции над клиентами',
    },
    {
        'name': 'auth',
        'description': 'Аутентификация'
    },
    {
        'name': 'reports',
        'description': 'Отчеты'
    }
]

app = FastAPI(openapi_tags=tags_metadata)

app.include_router(api.router)
use_route_names_as_operation_ids(app)


# for development purposes
@app.router.get(
    '/images/instructors/{file}'
)
def send_img(
    file: str
):
    return FileResponse(Path.cwd() / 'images' / 'instructors' / file)
# __END


# development middleware - CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[f'http://localhost:{settings.angular_port}', f'http://192.168.0.150:{settings.angular_port}'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# __END