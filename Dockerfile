FROM python:3.12

ARG GITHUB_SHA
ENV GITHUB_SHA=$GITHUB_SHA

WORKDIR /app/image_viewer
# Copy the project files into the container
COPY pyproject.toml  ./

RUN pip install .

# write git commit hash to a file
RUN echo $GITHUB_SHA > git_commit_hash.txt

# Copy the rest of the project files into the container
COPY . .

# Expose the port your app listens on
EXPOSE 8000

CMD ["uvicorn", "image_viewer.app:app", "--reload"]
