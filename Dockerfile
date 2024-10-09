FROM python:3.12

WORKDIR /app

ADD "https://api.github.com/repos/ACED-IDP/image_viewer/commits?per_page=1" latest_commit

RUN git clone  https://github.com/ACED-IDP/image_viewer
WORKDIR /app/image_viewer
RUN git checkout development
RUN pip install --no-cache-dir .
RUN git log --oneline
CMD ["uvicorn", "image_viewer.app:app", "--reload"]
