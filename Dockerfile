FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

RUN apt update

WORKDIR /workdir

COPY src/ ./src/
COPY requirements.txt  ./
COPY run.sh ./
RUN chmod +x run.sh

RUN pip install -r requirements.txt

ENTRYPOINT ["bash", "./run.sh"]

CMD []
