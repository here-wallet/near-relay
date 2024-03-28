FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

RUN apt-get update && apt-get install -y curl build-essential

# Install Rust
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# Add Cargo to PATH
ENV PATH="/root/.cargo/bin:${PATH}"

WORKDIR /workdir

COPY src/ ./src/
COPY requirements.txt  ./
COPY run.sh ./
RUN chmod +x run.sh

RUN pip install -r requirements.txt

#ENTRYPOINT ["bash", "./run.sh"]

CMD ["python3", "src/app.py"]


