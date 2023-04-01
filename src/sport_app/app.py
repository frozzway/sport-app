from fastapi import FastAPI
from fastapi.routing import APIRoute
from fastapi.middleware.cors import CORSMiddleware
from . import api
from .settings import settings


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

app.add_middleware(
    CORSMiddleware,
    allow_origins=[f'http://localhost:{settings.angular_port}'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
