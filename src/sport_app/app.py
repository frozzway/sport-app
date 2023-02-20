from fastapi import FastAPI
from . import (
    api
)

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
]

app = FastAPI(openapi_tags=tags_metadata)

app.include_router(api.router)