#!/usr/bin/env python3
import argparse

from requests import ConnectTimeout, HTTPError, ReadTimeout

from dx_vc_file_transfer.cli.config import Config
from dx_vc_file_transfer.cli.logger import logger
from dx_vc_file_transfer.dnanexus import DNANexusClient
from dx_vc_file_transfer.varsome import VarSomeClinicalClient


def _transfer_files(
    dx_project_id: str,
    folder: str,
    vclin_base_url: str,
    dx_base_url: str,
    accepted_file_extensions: list,
    download_expiration: int,
):
    """
    Transfer files from a DNAnexus project to VarSome Clinical.

    :param dx_project_id: The ID of the DNAnexus project.
    :type str
    :param folder: The folder path within the project.
    :type str
    :param vclin_base_url: VarSome Clinical base URL.
    :type str
    :param dx_base_url: DNAnexus base URL.
    :type str
    :param accepted_file_extensions: List of accepted file extensions.
    :type list
    :param download_expiration: Download expiration time in seconds.
    :type int
    """

    config = Config.from_env()
    dx_client = DNANexusClient(
        dx_api_token=config.dx_api_token,
        dx_base_url=dx_base_url,
        download_expiration=download_expiration,
        accepted_file_extensions=accepted_file_extensions,
    )
    vclin_client = VarSomeClinicalClient(
        clinical_api_token=config.vclin_api_token,
        clinical_base_url=vclin_base_url,
    )
    logger.info(
        "Initiating transfer of files in project %s folder %s", dx_project_id, folder
    )
    try:
        if file_urls_names := dx_client.files_download_urls_in_project_folder(
            dx_project_id, folder
        ):
            logger.info(
                "Retrieved %d files to transfer to VarSome Clinical",
                len(file_urls_names),
            )
            vclin_client.retrieve_external_files(file_urls_names)
            logger.info("Process to initiate file transfer completed")
            return
        logger.warning(
            "No files in project %s folder %s found to be transferred",
            dx_project_id,
            folder,
        )
    except HTTPError as e:
        logger.error("Failed to transfer files %s", e)
    except ConnectTimeout as e:
        logger.error("Timeout error while trying to transfer files %s", e)
    except ReadTimeout as e:
        logger.error("Read timeout error while trying to transfer files %s", e)


def main():
    parser = argparse.ArgumentParser(
        description="DNAnexus files transfer to VarSome Clinical"
    )
    parser.add_argument("--dx-project-id", required=True, help="DNAnexus project ID")
    parser.add_argument(
        "--folder", required=True, help="Folder path within the project"
    )
    parser.add_argument(
        "--vclin-base-url",
        default="https://ch.clinical.varsome.com",
        help="VarSome Clinical base URL (default: %(default)s)",
    )
    parser.add_argument(
        "--dx-base-url",
        default="https://api.dnanexus.com",
        help="DNAnexus base URL (default: %(default)s)",
    )
    parser.add_argument(
        "--accepted-file-extensions",
        default=".vcf,.vcf.gz,.fastq.gz",
        help="Comma-separated list of accepted file extensions (default: %(default)s)",
    )
    parser.add_argument(
        "--download-expiration",
        type=int,
        default=86400,
        help="Download expiration time in seconds (default: %(default)s)",
    )
    args = parser.parse_args()

    accepted_extensions = [
        ext.strip() for ext in args.accepted_file_extensions.split(",")
    ]

    _transfer_files(
        args.dx_project_id,
        args.folder,
        args.vclin_base_url,
        args.dx_base_url,
        accepted_extensions,
        args.download_expiration,
    )
