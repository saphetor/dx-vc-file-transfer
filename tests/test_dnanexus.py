from unittest.mock import MagicMock, call, patch

import pytest

from dx_vc_file_transfer.dnanexus import DNANexusClient


@pytest.fixture
def mock_http_session():
    with patch("dx_vc_file_transfer.dnanexus.http_session") as mock_session:
        mock_session.return_value = MagicMock()
        yield mock_session


def test_client_context_manager(mock_http_session):
    client = DNANexusClient(dx_api_token="test_token", dx_base_url="http://example.com")
    with client.client() as session:
        mock_http_session.assert_called_once_with("test_token")
        session.get("http://example.com")
    session.get.assert_called_once_with("http://example.com")
    session.close.assert_called_once()


@pytest.mark.usefixtures("mock_http_session")
@pytest.mark.parametrize(
    "folder, expected_folder",
    [
        ("test_folder", "/test_folder"),
        ("/test_folder", "/test_folder"),
        ("", "/"),
        ("/", "/"),
    ],
)
def test_list_folder_files(folder, expected_folder):
    client = DNANexusClient(dx_api_token="test_token", dx_base_url="http://example.com")
    project_id = "project-123"
    with client.client() as session:
        session.post.return_value.json.return_value = {"objects": []}
        client._list_folder_files(project_id, folder, session)
    session.post.assert_called_once_with(
        f"http://example.com/{project_id}/listFolder",
        json={"folder": expected_folder, "only": "objects", "describe": True},
    )


@pytest.mark.usefixtures("mock_http_session")
def test_filter_files_by_extension():
    client = DNANexusClient(
        dx_api_token="test_token",
        dx_base_url="http://example.com",
        accepted_file_extensions=[".vcf", ".vcf.gz"],
    )
    files = [
        {"id": "file-123", "describe": {"name": "test.vcf"}},
        {"id": "file-456", "describe": {"name": "test.txt"}},
        {"id": "file-789", "describe": {"name": "test.vcf.gz"}},
    ]
    result = client._filter_files_by_extension(files)
    assert result == {"file-123": "test.vcf", "file-789": "test.vcf.gz"}


@pytest.mark.usefixtures("mock_http_session")
def test_file_download_url():
    client = DNANexusClient(
        dx_api_token="test_token",
        dx_base_url="http://example.com",
        download_expiration=3600,
    )
    file_id = "file-123"
    with client.client() as session:
        session.post.return_value.json.return_value = {
            "url": "http://download.example.com/file-123"
        }
        result = client._file_download_url(file_id, session)
    assert result == "http://download.example.com/file-123"
    session.post.assert_called_once_with(
        f"http://example.com/{file_id}/download",
        json={"duration": 3600, "preauthenticated": True},
    )


@pytest.mark.usefixtures("mock_http_session")
def test_files_download_urls_in_project_folder():
    client = DNANexusClient(dx_api_token="test_token", dx_base_url="http://example.com")
    project_id = "project-123"
    folder = "test_folder"

    with patch.object(client, "_list_folder_files") as mock_list_files:
        with patch.object(client, "_file_download_url") as mock_download_url:
            mock_list_files.return_value = {
                "file-123": "test1.vcf",
                "file-456": "test2.vcf.gz",
            }
            mock_download_url.side_effect = [
                "http://download.example.com/file-123",
                "http://download.example.com/file-456",
            ]

            with client.client() as session:
                result = client.files_download_urls_in_project_folder(
                    project_id, folder
                )
    assert result == {
        "http://download.example.com/file-123": "test1.vcf",
        "http://download.example.com/file-456": "test2.vcf.gz",
    }
    mock_list_files.assert_called_once_with(project_id, folder, session)
    mock_download_url.assert_has_calls(
        [call("file-123", session), call("file-456", session)], any_order=True
    )


def test_files_download_urls_in_project_folder_no_files():
    client = DNANexusClient(dx_api_token="test_token", dx_base_url="http://example.com")
    project_id = "project-123"
    folder = "empty_folder"
    with patch.object(client, "_list_folder_files") as mock_list_files:
        mock_list_files.return_value = None
        with client.client():
            result = client.files_download_urls_in_project_folder(project_id, folder)
    assert result is None
    mock_list_files.assert_called_once()
