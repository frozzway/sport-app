from pydantic import BaseSettings


class Settings(BaseSettings):
    server_host: str = '127.0.0.1'
    server_port: int = '8000'

    db_dialect: str = 'postgresql'
    db_username: str = 'admin'
    db_password: str = '123'
    db_host: str = 'localhost'
    db_port: str = '5432'
    db_database: str = 'sport_app'

    timezone: str = "Asia/Yekaterinburg"


settings = Settings(
    _env_file='.env',
    _env_file_encoding='utf-8',
)