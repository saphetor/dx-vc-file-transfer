import contextlib
import dataclasses
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from dx_vc_file_transfer.http_request import http_session

if TYPE_CHECKING:
    import requests


@dataclasses.dataclass(kw_only=True)
class DNANexusClient:
    """
    Client for interacting with DNAnexus API.

    Facilitates operations like listing files in a project folder, retrieving
    file metadata, filtering files by extensions, and obtaining
    preauthenticated download URLs for files.

    :ivar dx_api_token: The API token used to authenticate requests to the DNAnexus API.
    :type dx_api_token: str
    :ivar dx_base_url: The base URL of the DNAnexus API.
    Defaults to "https://api.dnanexus.com".
    :type dx_base_url: Optional[str]
    :ivar download_expiration: The default expiration time (in seconds)
    for download links,
        set to 1 day by default (86400 seconds).
    :type download_expiration: Optional[int]
    :ivar accepted_file_extensions: List of file extensions that are acceptable for
        filtering. Defaults to [".vcf", ".vcf.gz", ".fastq.gz"].
    :type accepted_file_extensions: List[str]
    """

    dx_api_token: str
    dx_base_url: Optional[str] = "https://api.dnanexus.com"
    download_expiration: Optional[int] = 86400  # 1 day in seconds
    accepted_file_extensions: List[str] = dataclasses.field(
        default_factory=lambda: [
            ".vcf",
            ".vcf.gz",
            ".fastq.gz",
        ]
    )

    @contextlib.contextmanager
    def client(self):
        """
        Context manager to create and manage the HTTP client session.
        """
        client = http_session(self.dx_api_token)
        try:
            yield client
        finally:
            client.close()

    def _list_folder_files(
        self, project_id: str, folder: str, client: "requests.Session"
    ) -> Optional[Dict[str, Any]]:
        """
        List files in a specific folder within a DNAnexus project.

        :param project_id: The ID of the DNAnexus project.
        :type project_id: str
        :param folder: The folder path within the project.
        :type folder: str
        :param client: The HTTP client session to use for the request.
        :type client: requests.Session
        :return: A dictionary containing the list of files with keys: id (str)
        and describe (dict).
        """
        if not folder.startswith("/"):
            folder = f"/{folder}"
        url = f"{self.dx_base_url}/{project_id}/listFolder"
        params = {"folder": folder, "only": "objects", "describe": True}
        response = client.post(url, json=params)
        response.raise_for_status()
        files = response.json().get("objects", None)
        return self._filter_files_by_extension(files) if files else None

    def _filter_files_by_extension(self, files: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        Filters a list of files by their extensions and returns a dictionary
        mapping file IDs to file names of the files having accepted extensions.

        :param files: A list of dictionaries representing files,
            where each dictionary should include a key "id" with the identifier
            of the file and a key "describe" with the file's metadata.
        :type files: List[Dict[str, Any]]
        :return: A dictionary where keys are file IDs (str) and the values
            are file names (str) for files that have extensions
            matching the accepted file extensions.
        """
        return {
            file["id"]: file["describe"]["name"]
            for file in files
            if any(
                file["describe"]["name"].endswith(ext)
                for ext in self.accepted_file_extensions
            )
        }

    def _file_download_url(
        self, file_id: str, client: "requests.Session"
    ) -> Optional[str]:
        """
        Get a download URL for a file in DNAnexus.

        :param file_id: The ID of the file to download.
        :type file_id: str
        :param client: The HTTP client session to use for the request.
        :type client: requests.Session
        :return: A string containing the download URL.
        """
        url = f"{self.dx_base_url}/{file_id}/download"
        params = {"duration": self.download_expiration, "preauthenticated": True}
        response = client.post(url, json=params)
        response.raise_for_status()
        return response.json().get("url", None)

    def files_download_urls_in_project_folder(
        self, project_id: str, folder: str
    ) -> Optional[Dict[str, str]]:
        """
        Retrieves files in a specific folder of a DNAnexus project, filters them
        and returns a dictionary mapping file urls to file names.
        :param project_id: The ID of the DNAnexus project.
        :type project_id: str
        :param folder: The folder path within the project.
        :type folder: str
        :return: A dictionary where keys are file urls and values are file names
            of files that have accepted extensions.
        """
        with self.client() as client:
            if files := self._list_folder_files(project_id, folder, client):
                return {
                    self._file_download_url(file_id, client): file_name
                    for file_id, file_name in files.items()
                }
        return None
