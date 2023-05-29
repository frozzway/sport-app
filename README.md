# SportApp - FastAPI & Angular приложение для фитнес центра
Выполнялось в рамках дипломной работы бакалавра ЮУрГУ.<br>
Бэкенд: **FastAPI** &  **SQLAlchemy**<br>
Фронт: **Angular 15**<br>
Деплой на Yandex Cloud через  **Ansible** и **docker-compose**<br>

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

![ezgif-1-37e3cd12b6](https://user-images.githubusercontent.com/59840795/241748033-408dca3a-87da-45ce-93db-00dcaf6680fa.gif)

### Запись клиентов
![bandicam 2023-05-28 23-39-41-840](https://lh3.googleusercontent.com/u/1/drive-viewer/AFGJ81qf4M7C10UaJvmuKtDlEhZnzRTY2R58-DOdaj7_0wx4ZZPqmwhdPkV0yptB_lML_fmzc1MuV8fHHas_A8mOxaE9_ezZ8g=w1920-h937)
