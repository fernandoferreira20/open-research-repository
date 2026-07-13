"""Tests for research record PDF file endpoints."""

import io
import uuid
from pathlib import Path

from app.models import ResearchFile


def make_record_payload(**overrides):
    """Return a valid record payload with optional overrides."""
    payload = {
        "title": "Sample Research",
        "description": "A good description.",
        "record_type": "paper",
        "status": "draft",
        "license": "CC BY 4.0",
        "doi": "10.1234/example-file",
        "publication_date": "2026-07-10",
    }
    payload.update(overrides)
    return payload


def create_record(client, **overrides) -> dict:
    """Create a record and return the response payload."""
    response = client.post("/api/records", json=make_record_payload(**overrides))
    assert response.status_code == 201
    return response.get_json()


def make_pdf_upload(
    content: bytes = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF",
    filename: str = "paper.pdf",
    content_type: str = "application/pdf",
) -> dict:
    """Create multipart test data for a PDF upload."""
    return {"file": (io.BytesIO(content), filename, content_type)}


def get_research_file(app, record_id: str) -> ResearchFile | None:
    """Load a ResearchFile row for assertions."""
    with app.app_context():
        return ResearchFile.query.filter_by(record_id=uuid.UUID(record_id)).one_or_none()


def test_upload_pdf_success(client, app, upload_folder):
    record = create_record(client, doi="10.1234/upload-success")
    file_content = b"%PDF-1.4\nUploaded test PDF\n%%EOF"

    response = client.post(
        f"/api/records/{record['id']}/file",
        data=make_pdf_upload(content=file_content),
        content_type="multipart/form-data",
    )

    assert response.status_code == 201
    payload = response.get_json()["file"]
    assert payload["record_id"] == record["id"]
    assert payload["original_filename"] == "paper.pdf"
    assert payload["mime_type"] == "application/pdf"
    assert payload["file_size"] == len(file_content)
    assert payload["download_url"] == f"/api/records/{record['id']}/file"

    research_file = get_research_file(app, record["id"])
    assert research_file is not None
    assert Path(research_file.file_path).exists()
    assert Path(research_file.file_path).read_bytes() == file_content
    assert str(upload_folder) in research_file.file_path


def test_upload_pdf_missing_record_returns_404(client):
    response = client.post(
        "/api/records/00000000-0000-0000-0000-000000000000/file",
        data=make_pdf_upload(),
        content_type="multipart/form-data",
    )

    assert response.status_code == 404
    assert response.get_json()["error"]["code"] == "not_found"


def test_upload_pdf_rejects_non_multipart_request(client):
    record = create_record(client, doi="10.1234/non-multipart")

    response = client.post(
        f"/api/records/{record['id']}/file",
        data=b"not-multipart",
        content_type="application/json",
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["error"]["code"] == "validation_error"
    assert "content_type" in payload["error"]["details"]


def test_upload_pdf_rejects_missing_file_field(client):
    record = create_record(client, doi="10.1234/missing-field")

    response = client.post(
        f"/api/records/{record['id']}/file",
        data={"other": "value"},
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["error"]["code"] == "validation_error"
    assert "file" in payload["error"]["details"]


def test_upload_pdf_rejects_empty_filename(client):
    record = create_record(client, doi="10.1234/empty-filename")

    response = client.post(
        f"/api/records/{record['id']}/file",
        data=make_pdf_upload(filename=""),
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["error"]["code"] == "validation_error"
    assert "file" in payload["error"]["details"]


def test_upload_pdf_rejects_non_pdf_extension(client):
    record = create_record(client, doi="10.1234/bad-extension")

    response = client.post(
        f"/api/records/{record['id']}/file",
        data=make_pdf_upload(filename="notes.txt"),
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["error"]["code"] == "validation_error"
    assert payload["error"]["details"]["file"] == "Only PDF files are allowed"


def test_upload_pdf_rejects_non_pdf_mimetype(client):
    record = create_record(client, doi="10.1234/bad-mimetype")

    response = client.post(
        f"/api/records/{record['id']}/file",
        data=make_pdf_upload(content_type="text/plain"),
        content_type="multipart/form-data",
    )

    assert response.status_code == 400
    payload = response.get_json()
    assert payload["error"]["code"] == "validation_error"
    assert payload["error"]["details"]["file"] == "File must have MIME type application/pdf"


def test_upload_pdf_rejects_oversized_file(client, app):
    record = create_record(client, doi="10.1234/oversized")
    app.config["MAX_CONTENT_LENGTH"] = 1024
    app.config["MAX_UPLOAD_SIZE_MB"] = 1
    file_content = b"%PDF-1.4\n" + (b"x" * 2048)

    response = client.post(
        f"/api/records/{record['id']}/file",
        data=make_pdf_upload(content=file_content),
        content_type="multipart/form-data",
    )

    assert response.status_code == 413
    assert response.get_json()["error"]["code"] == "payload_too_large"


def test_upload_pdf_conflicts_when_record_already_has_file(client):
    record = create_record(client, doi="10.1234/conflict")
    first_response = client.post(
        f"/api/records/{record['id']}/file",
        data=make_pdf_upload(),
        content_type="multipart/form-data",
    )

    assert first_response.status_code == 201

    second_response = client.post(
        f"/api/records/{record['id']}/file",
        data=make_pdf_upload(filename="replacement.pdf"),
        content_type="multipart/form-data",
    )

    assert second_response.status_code == 409
    assert second_response.get_json()["error"]["code"] == "conflict"


def test_download_pdf_success(client):
    record = create_record(client, doi="10.1234/download-success")
    file_content = b"%PDF-1.4\nDownload me\n%%EOF"
    upload_response = client.post(
        f"/api/records/{record['id']}/file",
        data=make_pdf_upload(content=file_content, filename="download.pdf"),
        content_type="multipart/form-data",
    )
    assert upload_response.status_code == 201

    response = client.get(f"/api/records/{record['id']}/file")

    assert response.status_code == 200
    assert response.data == file_content
    assert response.headers["Content-Type"].startswith("application/pdf")
    assert "download.pdf" in response.headers["Content-Disposition"]


def test_download_pdf_without_metadata_returns_404(client):
    record = create_record(client, doi="10.1234/download-missing")

    response = client.get(f"/api/records/{record['id']}/file")

    assert response.status_code == 404
    assert response.get_json()["error"]["code"] == "not_found"


def test_download_pdf_missing_physical_file_returns_404(client, app):
    record = create_record(client, doi="10.1234/download-missing-disk")
    upload_response = client.post(
        f"/api/records/{record['id']}/file",
        data=make_pdf_upload(),
        content_type="multipart/form-data",
    )
    assert upload_response.status_code == 201

    research_file = get_research_file(app, record["id"])
    assert research_file is not None
    Path(research_file.file_path).unlink()

    response = client.get(f"/api/records/{record['id']}/file")

    assert response.status_code == 404
    payload = response.get_json()
    assert payload["error"]["code"] == "not_found"
    assert "missing on disk" in payload["error"]["message"]


def test_replace_pdf_success(client, app):
    record = create_record(client, doi="10.1234/replace-success")
    initial_upload = client.post(
        f"/api/records/{record['id']}/file",
        data=make_pdf_upload(content=b"%PDF-1.4\nOld\n%%EOF", filename="old.pdf"),
        content_type="multipart/form-data",
    )
    assert initial_upload.status_code == 201

    original_file = get_research_file(app, record["id"])
    assert original_file is not None
    old_path = Path(original_file.file_path)

    new_content = b"%PDF-1.4\nNew\n%%EOF"
    response = client.put(
        f"/api/records/{record['id']}/file",
        data=make_pdf_upload(content=new_content, filename="new.pdf"),
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    payload = response.get_json()["file"]
    assert payload["original_filename"] == "new.pdf"
    assert payload["file_size"] == len(new_content)

    updated_file = get_research_file(app, record["id"])
    assert updated_file is not None
    assert Path(updated_file.file_path).exists()
    assert Path(updated_file.file_path).read_bytes() == new_content
    assert updated_file.file_path != str(old_path)
    assert not old_path.exists()


def test_replace_pdf_requires_existing_file(client):
    record = create_record(client, doi="10.1234/replace-missing")

    response = client.put(
        f"/api/records/{record['id']}/file",
        data=make_pdf_upload(),
        content_type="multipart/form-data",
    )

    assert response.status_code == 404
    assert response.get_json()["error"]["code"] == "not_found"


def test_delete_pdf_success(client, app):
    record = create_record(client, doi="10.1234/delete-file")
    upload_response = client.post(
        f"/api/records/{record['id']}/file",
        data=make_pdf_upload(),
        content_type="multipart/form-data",
    )
    assert upload_response.status_code == 201

    research_file = get_research_file(app, record["id"])
    assert research_file is not None
    file_path = Path(research_file.file_path)

    response = client.delete(f"/api/records/{record['id']}/file")

    assert response.status_code == 204
    assert get_research_file(app, record["id"]) is None
    assert not file_path.exists()


def test_delete_pdf_missing_returns_404(client):
    record = create_record(client, doi="10.1234/delete-missing")

    response = client.delete(f"/api/records/{record['id']}/file")

    assert response.status_code == 404
    assert response.get_json()["error"]["code"] == "not_found"


def test_deleting_record_also_removes_uploaded_pdf(client, app):
    record = create_record(client, doi="10.1234/delete-record-file")
    upload_response = client.post(
        f"/api/records/{record['id']}/file",
        data=make_pdf_upload(),
        content_type="multipart/form-data",
    )
    assert upload_response.status_code == 201

    research_file = get_research_file(app, record["id"])
    assert research_file is not None
    file_path = Path(research_file.file_path)

    delete_response = client.delete(f"/api/records/{record['id']}")

    assert delete_response.status_code == 204
    assert not file_path.exists()
    assert get_research_file(app, record["id"]) is None
