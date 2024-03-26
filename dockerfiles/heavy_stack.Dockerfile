FROM python:slim

# install poetry
RUN pip install poetry

WORKDIR /app
COPY pyproject.toml poetry.lock ./

# install dependencies
RUN poetry config virtualenvs.in-project true
RUN poetry install

# replace reactpy with custom version
RUN rm -rf .venv/lib/python3.11/site-packages/reactpy
# note: custom_reactpy cannot be a soft link to /workspaces/reactpy
COPY ./custom_reactpy/reactpy .venv/lib/python3.11/site-packages/reactpy
COPY ./custom_reactpy/dist .venv/lib/python3.11/site-packages/reactpy/_static/app/dist

COPY static static
COPY heavy_stack heavy_stack

ENV SANIC_REQUEST_MAX_SIZE 10000000
ENV SANIC_REQUEST_TIMEOUT 10
ENV SANIC_RESPONSE_TIMEOUT 10
ENV PYTHONPATH .:static/brython

EXPOSE 8000

# ENTRYPOINT ["ls", "-l"]
ENTRYPOINT ["poetry", "run", "sanic" , "heavy_stack.main.app", "--host", "0.0.0.0", "--port", "8000", "--fast"]
