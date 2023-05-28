# SportApp - FastAPI & Angular приложение для фитнес центра
Выполнялось в рамках дипломной работы бакалавра ЮУрГУ.
Бэкенд: **FastAPI** &  **SQLAlchemy**
Фронт: **Angular 15**
Деплой на Yandex Cloud через  **Ansible** и **docker-compose**

[Репозиторий клиента](https://github.com/FrozzWay/sport-app-client)

### Функционал
Приложение динамически формирует расписание занятий (тренировочных программ) на основе редактируемых схем и отображает его на две недели вперед, позволяет вести базу инструкторов, клиентов, записывать их на занятия, отслеживать посещаемость с помощью отчетов.
- Вся функциональная логика разработана на FastAPI, спецификация OpenAPI [доступна здесь](https://okunevad.cloud/docs).
- Сформированное расписание [на этой странице](https://okunevad.cloud/schedule).
- Страница с редактированием доступна после [авторизации](https://okunevad.cloud/login).

#### Спроектированная база данных
<img src= "https://i.imgur.com/QOJuRkR.png"  width="500"/>


## Конечный результат
### Редактирование схемы
![ezgif-1-37e3cd12b6](https://github.com/FrozzWay/sport-app/assets/59840795/c9ed3b58-a23d-462a-acf3-b74363bb9e74)
### Запись клиентов
![bandicam 2023-05-28 23-39-41-840](https://github.com/FrozzWay/sport-app/assets/59840795/ab3e8c05-14f8-4ae9-bfa0-0996fa2ca015)
