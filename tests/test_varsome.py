from unittest.mock import MagicMock, call, patch

import pytest

from dx_vc_file_transfer.varsome import VarSomeClinicalClient


@pytest.fixture
def mock_http_session():
    with patch("dx_vc_file_transfer.varsome.http_session") as mock_session:
        mock_session.return_value = MagicMock()
        yield mock_session


def test_client_context_manager(mock_http_session):
    client = VarSomeClinicalClient(
        clinical_api_token="test_token", clinical_base_url="http://example.com"
    )
    with client.client() as session:
        mock_http_session.assert_called_once_with("test_token")
        session.get("http://example.com")
    session.get.assert_called_once_with("http://example.com")
    session.close.assert_called_once()


@pytest.mark.usefixtures("mock_http_session")
def test_retrieve_external_file():
    client = VarSomeClinicalClient(
        clinical_api_token="test_token", clinical_base_url="http://example.com"
    )
    file_url = "http://server.somewhere.com/file.txt"
    file_name = "file.txt"
    with client.client() as session:
        client._retrieve_external_file(file_url, file_name, session)
    session.post.assert_called_once_with(
        "http://example.com/api/v1/sample-files/",
        json={"file_url": file_url, "sample_file_name": file_name},
    )


@pytest.mark.usefixtures("mock_http_session")
def test_retrieve_external_files():
    client = VarSomeClinicalClient(
        clinical_api_token="test_token", clinical_base_url="http://example.com"
    )
    files = {
        "http://server.somewhere.com/file1.txt": "file1",
        "http://server.somewhere.com/file2.txt": "file2",
    }
    with client.client() as session:
        client.retrieve_external_files(files)
    session.post.assert_has_calls(
        [
            call(
                "http://example.com/api/v1/sample-files/",
                json={
                    "file_url": "http://server.somewhere.com/file1.txt",
                    "sample_file_name": "file1",
                },
            ),
            call(
                "http://example.com/api/v1/sample-files/",
                json={
                    "file_url": "http://server.somewhere.com/file2.txt",
                    "sample_file_name": "file2",
                },
            ),
        ],
        any_order=True,
    )
