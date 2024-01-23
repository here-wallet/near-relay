FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

RUN apt update

WORKDIR /workdir

COPY src/ ./src/
COPY config.yml ./
COPY requirements.txt  ./

RUN pip install -r requirements.txt

CMD ["python", "src/run_web.py"]
