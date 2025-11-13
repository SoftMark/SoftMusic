FROM python:3.12.8

WORKDIR /code

COPY . /code/

RUN pip install -r src/requirements.txt

CMD ["uvicorn", "src.run:app", "--host", "0.0.0.0", "--port", "8000"]
