# SportApp - FastAPI & Angular приложение для фитнес центра
Выполнялось в рамках дипломной работы бакалавра ЮУрГУ.<br>
Бэкенд: **FastAPI** &  **SQLAlchemy**<br>
Фронт: **Angular 15**<br>
Деплой на Yandex Cloud через  **Ansible** и **docker-compose**<br>

[Репозиторий клиента](https://github.com/FrozzWay/sport-app-client)<br>
[Текст дипломной работы](http://omega.sp.susu.ru/publications/bachelorthesis/2023_404_okunevad.pdf)

### Функционал
Приложение динамически формирует расписание занятий (тренировочных программ) на основе редактируемых схем и отображает его на две недели вперед, позволяет вести базу инструкторов, клиентов, записывать их на занятия, отслеживать посещаемость с помощью отчетов.
- Вся функциональная логика разработана на FastAPI, спецификация OpenAPI [доступна здесь](https://okunevad.cloud/docs).
- Сформированное расписание [на этой странице](https://okunevad.cloud/schedule).
- Страница с редактированием доступна после [авторизации](https://okunevad.cloud/login). (John Doe : 123)

#### Спроектированная база данных
<img src= "https://i.imgur.com/QOJuRkR.png"  width="500"/>


## Конечный результат
### Редактирование схемы
<img src="https://user-images.githubusercontent.com/59840795/241748033-408dca3a-87da-45ce-93db-00dcaf6680fa.gif"  width="700"/>

### Запись клиентов
<img src="https://user-images.githubusercontent.com/59840795/250643841-f5e3418f-1f28-4c59-ae82-2590a38557e5.gif"  width="700"/>
