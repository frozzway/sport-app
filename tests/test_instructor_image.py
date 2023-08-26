from pathlib import Path
from pytest_mock import MockerFixture

from fastapi.testclient import TestClient

from src.sport_app import services
from src.sport_app.app import app
from src.sport_app.settings import settings
from src.sport_app.services.programs.instructor import InstructorService

client = TestClient(app)

def test_upload_instructor_image_writes_new_image_file(instructor, tmp_path, monkeypatch, mocker: MockerFixture):
    files = {'image': open('files/img.jpg', 'rb')}
    monkeypatch.chdir(tmp_path)
    token_name = 'img-name'
    patched = mocker.patch.object(services.programs.instructor, 'token_urlsafe')
    patched.return_value = token_name

    response = client.put(f'/api/programs/instructor/{instructor.id}/image', files=files)

    assert response.status_code == 200
    assert Path.exists(tmp_path / settings.images_path / 'instructors' / f'{token_name}.jpg')


def test_upload_instructor_image_removes_old_image_file(instructor_with_image, tmp_path, monkeypatch):
    files = {'image': open('files/img.jpg', 'rb')}
    monkeypatch.chdir(tmp_path)
    filename = f'{instructor_with_image.photo_token}.jpg'
    file_to_remove = Path(tmp_path / settings.images_path / 'instructors' / filename)

    response = client.put(f'/api/programs/instructor/{instructor_with_image.id}/image', files=files)

    assert response.status_code == 200
    assert not Path.exists(file_to_remove)


def test_upload_instructor_image_fails_on_non_image_file(instructor, tmp_path, monkeypatch):
    files = {'image': open('files/not-img', 'rb')}
    monkeypatch.chdir(tmp_path)

    response = client.put(f'/api/programs/instructor/{instructor.id}/image', files=files)

    assert response.status_code == 400
    assert response.json()['detail'] == 'Invalid image type'
