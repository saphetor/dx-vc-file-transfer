from unittest.mock import MagicMock, call, patch

import pytest
from requests import ConnectTimeout, HTTPError, ReadTimeout

from dx_vc_file_transfer.cli.transfer_files import _transfer_files, main


@pytest.fixture
def mock_config():
    with patch("dx_vc_file_transfer.cli.transfer_files.Config") as mock_config_class:
        mock_config_instance = MagicMock()
        mock_config_class.from_env.return_value = mock_config_instance
        mock_config_instance.dx_api_token = "mock_dx_token"
        mock_config_instance.vclin_api_token = "mock_vclin_token"
        yield mock_config_instance


@pytest.fixture
def mock_dx_client():
    with patch(
        "dx_vc_file_transfer.cli.transfer_files.DNANexusClient"
    ) as mock_client_class:
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance
        yield mock_client_instance


@pytest.fixture
def mock_vclin_client():
    with patch(
        "dx_vc_file_transfer.cli.transfer_files.VarSomeClinicalClient"
    ) as mock_client_class:
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance
        yield mock_client_instance


@pytest.fixture
def mock_logger():
    with patch("dx_vc_file_transfer.cli.transfer_files.logger") as mock_logger:
        yield mock_logger


def test_transfer_files_success(
    mock_config, mock_dx_client, mock_vclin_client, mock_logger
):
    dx_project_id = "project-123"
    folder = "test_folder"
    vclin_base_url = "https://mock.varsome.com"
    dx_base_url = "https://mock.dnanexus.com"
    accepted_file_extensions = [".mock1", ".mock2"]
    download_expiration = 1234
    file_urls_names = {
        "http://download.example.com/file1": "file1.vcf",
        "http://download.example.com/file2": "file2.vcf.gz",
    }

    mock_dx_client.files_download_urls_in_project_folder.return_value = file_urls_names

    _transfer_files(
        dx_project_id,
        folder,
        vclin_base_url,
        dx_base_url,
        accepted_file_extensions,
        download_expiration,
    )

    mock_dx_client.files_download_urls_in_project_folder.assert_called_once_with(
        dx_project_id, folder
    )
    mock_vclin_client.retrieve_external_files.assert_called_once_with(file_urls_names)

    mock_logger.info.assert_has_calls(
        [
            call(
                "Initiating transfer of files in project %s folder %s",
                dx_project_id,
                folder,
            ),
            call(
                "Retrieved %d files to transfer to VarSome Clinical",
                len(file_urls_names),
            ),
            call("Process to initiate file transfer completed"),
        ]
    )


def test_transfer_files_no_files(
    mock_config, mock_dx_client, mock_vclin_client, mock_logger
):
    dx_project_id = "project-123"
    folder = "empty_folder"
    vclin_base_url = "https://mock.varsome.com"
    dx_base_url = "https://mock.dnanexus.com"
    accepted_file_extensions = [".mock1", ".mock2"]
    download_expiration = 1234

    mock_dx_client.files_download_urls_in_project_folder.return_value = None

    _transfer_files(
        dx_project_id,
        folder,
        vclin_base_url,
        dx_base_url,
        accepted_file_extensions,
        download_expiration,
    )

    mock_dx_client.files_download_urls_in_project_folder.assert_called_once_with(
        dx_project_id, folder
    )
    mock_vclin_client.retrieve_external_files.assert_not_called()

    mock_logger.info.assert_called_once_with(
        "Initiating transfer of files in project %s folder %s", dx_project_id, folder
    )
    mock_logger.warning.assert_called_once_with(
        "No files in project %s folder %s found to be transferred",
        dx_project_id,
        folder,
    )


def test_transfer_files_http_error(
    mock_config, mock_dx_client, mock_vclin_client, mock_logger
):
    dx_project_id = "project-123"
    folder = "test_folder"
    vclin_base_url = "https://mock.varsome.com"
    dx_base_url = "https://mock.dnanexus.com"
    accepted_file_extensions = [".mock1", ".mock2"]
    download_expiration = 1234

    mock_dx_client.files_download_urls_in_project_folder.side_effect = HTTPError(
        "HTTP Error"
    )

    _transfer_files(
        dx_project_id,
        folder,
        vclin_base_url,
        dx_base_url,
        accepted_file_extensions,
        download_expiration,
    )

    mock_logger.error.assert_called_once_with(
        "Failed to transfer files %s",
        mock_dx_client.files_download_urls_in_project_folder.side_effect,
    )


def test_transfer_files_connect_timeout(
    mock_config, mock_dx_client, mock_vclin_client, mock_logger
):
    dx_project_id = "project-123"
    folder = "test_folder"
    vclin_base_url = "https://mock.varsome.com"
    dx_base_url = "https://mock.dnanexus.com"
    accepted_file_extensions = [".mock1", ".mock2"]
    download_expiration = 1234

    mock_dx_client.files_download_urls_in_project_folder.side_effect = ConnectTimeout(
        "Connection Timeout"
    )

    _transfer_files(
        dx_project_id,
        folder,
        vclin_base_url,
        dx_base_url,
        accepted_file_extensions,
        download_expiration,
    )

    mock_logger.error.assert_called_once_with(
        "Timeout error while trying to transfer files %s",
        mock_dx_client.files_download_urls_in_project_folder.side_effect,
    )


def test_transfer_files_read_timeout(
    mock_config, mock_dx_client, mock_vclin_client, mock_logger
):
    dx_project_id = "project-123"
    folder = "test_folder"
    vclin_base_url = "https://mock.varsome.com"
    dx_base_url = "https://mock.dnanexus.com"
    accepted_file_extensions = [".mock1", ".mock2"]
    download_expiration = 1234

    mock_dx_client.files_download_urls_in_project_folder.side_effect = ReadTimeout(
        "Read Timeout"
    )

    _transfer_files(
        dx_project_id,
        folder,
        vclin_base_url,
        dx_base_url,
        accepted_file_extensions,
        download_expiration,
    )

    mock_logger.error.assert_called_once_with(
        "Read timeout error while trying to transfer files %s",
        mock_dx_client.files_download_urls_in_project_folder.side_effect,
    )


def test_main(mock_config, mock_dx_client, mock_vclin_client):
    with patch("argparse.ArgumentParser.parse_args") as mock_parse_args:
        mock_args = MagicMock()
        mock_args.dx_project_id = "project-123"
        mock_args.folder = "test_folder"
        mock_args.vclin_base_url = "https://mock.varsome.com"
        mock_args.dx_base_url = "https://mock.dnanexus.com"
        mock_args.accepted_file_extensions = ".mock1,.mock2"
        mock_args.download_expiration = 1234
        mock_parse_args.return_value = mock_args

        with patch(
            "dx_vc_file_transfer.cli.transfer_files._transfer_files"
        ) as mock_transfer:
            main()

            mock_transfer.assert_called_once_with(
                "project-123",
                "test_folder",
                "https://mock.varsome.com",
                "https://mock.dnanexus.com",
                [".mock1", ".mock2"],
                1234,
            )


def test_main_argument_parsing():
    with patch("argparse.ArgumentParser.parse_args") as mock_parse_args:
        with patch("dx_vc_file_transfer.cli.transfer_files._transfer_files"):
            main()
            mock_parse_args.assert_called_once()
