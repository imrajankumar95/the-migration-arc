# ─────────────────────────────────────────────
# The Migration Arc — Local Dev Commands
# ─────────────────────────────────────────────

IMAGE_NAME := migration-arc-app
TAG        := local

.PHONY: build run stop test lint clean

## Build the Docker image locally
build:
	docker build -t $(IMAGE_NAME):$(TAG) ./app

## Run the app container locally on port 5000
run:
	docker run --rm -p 5000:5000 --name $(IMAGE_NAME) $(IMAGE_NAME):$(TAG)

## Stop the running container
stop:
	docker stop $(IMAGE_NAME) || true

## Run unit tests (requires Python + deps installed)
test:
	pip install pytest pytest-flask --quiet
	pytest tests/ -v

## Lint the app code
lint:
	flake8 app/app.py --max-line-length=100 --ignore=E501

## Remove local Docker image
clean:
	docker rmi $(IMAGE_NAME):$(TAG) || true

## Build + run in one shot
dev: build run
