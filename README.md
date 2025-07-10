# DNAnexus to VarSome Clinical File Transfer

A utility for transferring genomic files from DNAnexus projects to VarSome Clinical.

## Project Scope

This project is a tool to handle a specific use case: transferring genomic files (VCF, BAM, FASTQ) from DNAnexus
projects to
VarSome Clinical.
It provides a command-line interface that:

1. Lists files in a specified DNAnexus project folder
2. Filters files by supported extensions (.vcf, .vcf.gz, .fastq.gz)
3. Generates pre-authenticated download URLs for the files
4. Submits these URLs to VarSome Clinical for retrieval and processing

This tool is designed for bioinformaticians and clinical researchers
who work with both DNAnexus and VarSome Clinical platforms.

## Installation

### Prerequisites

- Python 3.10 or higher
- Git

### Setup

1. Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install the package directly from GitHub:

```bash
pip install git+https://github.com/saphetor/dx-vc-file-transfer.git
```

#### Environment Variables

Set the following environment variables before running the tool:

```bash
# Required
export DX_API_TOKEN="your-dnanexus-api-token"
export VCLIN_API_TOKEN="your-varsome-clinical-api-token"
```

These environment variables are used for authentication with the DNAnexus and VarSome Clinical APIs. All other
configuration options are passed as command-line arguments.

#### Usage

Once installed and configured, you can use the CLI tool as follows:

```bash
dx_to_vclin_transfer --dx-project-id "project-xxxx" --folder "/path/to/folder"
```

#### Arguments

- `--dx-project-id`: The DNAnexus project ID (required)
- `--folder`: The folder path within the project (required)
- `--vclin-base-url`: VarSome Clinical base URL (default: "https://ch.clinical.varsome.com")
- `--dx-base-url`: DNAnexus base URL (default: "https://api.dnanexus.com")
- `--accepted-file-extensions`: Comma-separated list of accepted file extensions (default: ".vcf,.vcf.gz,.fastq.gz")
- `--download-expiration`: Download expiration time in seconds (default: 86400 - affects how long the download URLs
  produced by DNAnexus are valid)

#### Example

```bash
# Set up environment variables
export DX_API_TOKEN="your-dnanexus-api-token"
export VCLIN_API_TOKEN="your-varsome-clinical-api-token"

# Run the transfer with default settings
dx_to_vclin_transfer --dx-project-id "project-xxx" --folder "/samples/batch1"

# Run the transfer with custom settings
dx_to_vclin_transfer \
  --dx-project-id "project-xxxx" \
  --folder "/samples/batch1" \
  --vclin-base-url "https://eu.clinical.varsome.com" \
  --dx-base-url "https://custom.dnanexus.com" \
  --accepted-file-extensions ".vcf,.vcf.gz,.bam" \
  --download-expiration 172800
```

## Docker Installation

### Prerequisites

- Docker installed on your machine
- Git

### Setup

1. Clone the repository:

```bash
git clone https://github.com/saphetor/dx-vc-file-transfer.git
```

2. Build the Docker image:

```bash
cd dx-vc-file-transfer
docker build -t dx-vc-file-transfer .
```

### Usage

Create a `.env` file with the following content:

```env
DX_API_TOKEN="your-dnanexus-api-token"
VCLIN_API_TOKEN="your-varsome-clinical-api-token"
```

Run the Docker container:

```bash
docker run --env-file .env \
           dx-vc-file-transfer --dx-project-id "project-xxxx" --folder "/path/to/folder"
```

The Docker image uses Python 3.13.5 and includes all necessary dependencies.

#### Arguments

- `--dx-project-id`: The DNAnexus project ID (required)
- `--folder`: The folder path within the project (required)
- `--vclin-base-url`: VarSome Clinical base URL (default: "https://ch.clinical.varsome.com")
- `--dx-base-url`: DNAnexus base URL (default: "https://api.dnanexus.com")
- `--accepted-file-extensions`: Comma-separated list of accepted file extensions (default: ".vcf,.vcf.gz,.fastq.gz")
- `--download-expiration`: Download expiration time in seconds (default: 86400)

#### Example

```bash
docker run --env-file .env \
           dx-vc-file-transfer \
           --dx-project-id "project-xxxx" \
           --folder "/samples/batch1" \
           --vclin-base-url "https://eu.clinical.varsome.com" \
           --accepted-file-extensions ".vcf,.vcf.gz,.bam" \
           --download-expiration 172800
```

The tool will:

1. Find all supported files in the specified folder
2. Generate download URLs for these files
3. Submit the URLs to VarSome Clinical for retrieval

After the tool completes, you can check VarSome Clinical for the uploaded files.
