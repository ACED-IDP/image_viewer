FROM python:3.12
WORKDIR /app

COPY . /app/image_viewer
WORKDIR /app/image_viewer
RUN pip install --no-cache-dir .
CMD ["uvicorn", "image_viewer.app:app", "--reload"]
