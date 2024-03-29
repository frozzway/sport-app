from pydantic import BaseSettings


class Settings(BaseSettings):
    server_host: str = '0.0.0.0'
    server_port: int = '8000'

    angular_port: int = '4200'

    db_dialect: str = 'postgresql'
    db_username: str = 'admin'
    db_password: str = '123'
    db_host: str = 'localhost'
    db_port: str = '5432'
    db_database: str = 'sport_app'

    adm_username: str = 'John Doe'
    adm_email: str = 'johndoe@example.com'
    adm_password: str = '123'

    timezone: str = 'Asia/Yekaterinburg'

    jwt_secret: str = ''
    jwt_algorithm: str = 'HS256'
    jwt_expires_s: int = 360000

    images_path = 'images'


settings = Settings(
    _env_file='../.env',
    _env_file_encoding='utf-8',
)