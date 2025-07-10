import dataclasses
import os


@dataclasses.dataclass
class Config:
    """
    Configuration for the DNAnexus file transfer authentication tokens.
    """

    dx_api_token: str
    vclin_api_token: str

    @classmethod
    def from_env(cls):
        """
        Initialize the configuration from environment variables.
        Environment variables should include the authentication tokens.
        :return:
        """
        return cls(
            dx_api_token=os.getenv("DX_API_TOKEN"),
            vclin_api_token=os.getenv("VCLIN_API_TOKEN"),
        )
