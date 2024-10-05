FROM python:3.12

WORKDIR /app

RUN git clone  https://github.com/ACED-IDP/image_viewer
WORKDIR /app/image_viewer
RUN git checkout development
COPY pyproject.toml .
RUN pip install --no-cache-dir .

CMD ["uvicorn", "image_viewer.app:app", "--reload"]
