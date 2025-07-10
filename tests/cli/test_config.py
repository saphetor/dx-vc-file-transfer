from unittest.mock import patch

from dx_vc_file_transfer.cli.config import Config


def test_config_initialization():
    config = Config(
        dx_api_token="dx_token",
        vclin_api_token="vclin_token",
    )

    assert config.dx_api_token == "dx_token"
    assert config.vclin_api_token == "vclin_token"


@patch.dict(
    "os.environ",
    {
        "DX_API_TOKEN": "env_dx_token",
        "VCLIN_API_TOKEN": "env_vclin_token",
    },
)
def test_config_from_env():
    config = Config.from_env()

    assert config.dx_api_token == "env_dx_token"
    assert config.vclin_api_token == "env_vclin_token"
