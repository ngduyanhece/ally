# Using a slim version for a smaller base image
FROM python:3.11.6-slim-bullseye

# Install GEOS library, Rust, and other dependencies, then clean up
RUN apt-get clean && apt-get update && apt-get install -y \
    libgeos-dev \
    libcurl4-openssl-dev \
    libssl-dev \
    binutils \
    pandoc \
    curl \
    git \
    poppler-utils \
    tesseract-ocr \
    build-essential && \
    rm -rf /var/lib/apt/lists/* && apt-get clean

# Add Rust binaries to the PATH
ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /code

# Copy just the requirements first
COPY ./requirements.txt .

# Upgrade pip
RUN pip install --upgrade pip

# Increase timeout to wait for the new installation
RUN pip install --no-cache-dir -r requirements.txt --timeout 200

# Copy the rest of the application
COPY . .
RUN ./setup.sh
EXPOSE 5050
CMD ["uvicorn", "ally.main:app", "--host", "0.0.0.0", "--port", "5050", "--workers", "6"]
