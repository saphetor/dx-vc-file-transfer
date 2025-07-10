FROM python:3.13.5-slim

WORKDIR /app

# Copy the project files
COPY . /app/

# Install the package and its dependencies
RUN pip install --no-cache-dir -e .

# Set environment variables (these will need to be provided at runtime)
ENV DX_API_TOKEN=""
ENV VCLIN_API_TOKEN=""

# Set the entrypoint to the CLI tool
ENTRYPOINT ["dx_to_vclin_transfer"]

# Default command (can be overridden)
CMD ["--help"]
