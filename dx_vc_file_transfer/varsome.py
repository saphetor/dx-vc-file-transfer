import contextlib
import dataclasses
from typing import TYPE_CHECKING, Dict, Optional

from dx_vc_file_transfer.http_request import http_session

if TYPE_CHECKING:
    import requests


@dataclasses.dataclass(kw_only=True)
class VarSomeClinicalClient:
    """
    Handles interactions with the VarSome Clinical API.
    Provides methods to retrieve external files.

    :ivar clinical_api_token: The authentication token for accessing the
        clinical API.
    :type clinical_api_token: str
    :ivar clinical_base_url: The base URL for the clinical API. Defaults to
        "https://ch.clinical.varsome.com".
    :type clinical_base_url: Optional[str]
    """

    clinical_api_token: str
    clinical_base_url: Optional[str] = "https://ch.clinical.varsome.com"

    @contextlib.contextmanager
    def client(self):
        """
        Context manager to create and manage the HTTP client session.
        """
        client = http_session(self.clinical_api_token)
        try:
            yield client
        finally:
            client.close()

    def _retrieve_external_file(
        self, file_url: str, file_name: str, client: "requests.Session"
    ) -> Dict:
        """
        Retrieve an external file from the clinical API.

        :param file_url: The URL of the file to retrieve.
        :type file_url: str
        :param file_name: The name of the file to save.
        :type file_name: str
        :param client: The HTTP client session to use for the request.
        :type client: requests.Session
        :return: A dictionary containing the file metadata.
        """
        url = f"{self.clinical_base_url}/api/v1/sample-files/"
        params = {"file_url": file_url, "sample_file_name": file_name}
        response = client.post(url, json=params)
        response.raise_for_status()
        return response.json()

    def retrieve_external_files(self, files: Dict[str, str]) -> Dict[str, Dict]:
        """
        Retrieve multiple external files from the clinical API.

        :param files: A dictionary where keys are file URLs and values are file names.
        :type files: Dict[str, str]
        :return: A dictionary containing metadata for each retrieved file.
        """
        with self.client() as client:
            return {
                file_url: self._retrieve_external_file(file_url, file_name, client)
                for file_url, file_name in files.items()
            }
