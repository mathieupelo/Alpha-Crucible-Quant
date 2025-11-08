FROM apache/airflow:2.8.0

USER root

# Install system dependencies for git and docker client
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI (not docker.io, just the CLI to interact with host Docker)
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian bullseye stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update && apt-get install -y docker-ce-cli \
    && rm -rf /var/lib/apt/lists/*

USER airflow

# Install additional Python packages for backtest execution
RUN pip install --no-cache-dir \
    psycopg2-binary \
    docker \
    mysql-connector-python \
    pandas \
    numpy \
    python-dotenv \
    yfinance \
    cvxopt \
    fastapi \
    pydantic

