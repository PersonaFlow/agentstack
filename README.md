# Introduction 
Welcome to LLiMeade!

This mono-repo consists of a python backend in the `pyserver` directory running on FastAPI and a React/NextJS frontend in the `client` directory. To run the end-to-end solution locally, you will need to run the docker image, which can be done by running from the docker-compose. 

# Setup Instructions
The application can be setup to run client and pyserver with HMR for dev, or it can run entirely from the docker-compose. 

## Quickstart (Docker)

Follow these instructions if you are only running from Docker and do not need to set up the environment for development.

1. Create .env.production file in root using the .env.production.example template.
2. Run `docker-compose up`


## Dev Setup 

*Review "LLiMeade PyServer Prerequisites" below for instructions on installing Python and Poetry.*

1. Clone the repo
2. From root directory, create a new virtual env with `python  -m venv .venv`
3. Activate the virtual env with `source .venv/bin/activate`
4. Create .env.local file using the .env.local.example template.
5. Open docker-compose.yaml and comment out the `pyserver` block under `services`
6. Open docker on your machine if it is not already running and run `docker-compose up -d`. This will download and start the images for Qdrant, Postgres, and Unstructured-API
7.  Install the dependencies by running `cd pyserver && poetry install --no-root`. 
8.  When that is fiinished, you will need to run the database migration with `alembic upgrade head` while still in the `pyserver` directory.
9.  Run `poetry run python start.py` to start the server.
10. Navigate to `http://localhost:9000/docs` to see the API documentation.
11. Continue with "Testing the APIs" below

   
## LLiMeade PyServer Prerequisites
Before starting the dev setup, make sure you have Python 3.11 or above installed:
- Download and install python from [https://www.python.org/downloads/](https://www.python.org/downloads/)
- (Optional) create an alias for python to point to python3 in your shell configuration file (e.g., .zshrc or .bash_profile), like this (for mac):
```shell
echo 'alias python=python3' >> ~/.zshrc
source ~/.zshrc
```
- Run the `Update Shell Profile.command` and `Install Certificates.command` files, located in the folder where Python was installed.
Now you are ready to set up PyServer...

The pyserver uses Poetry for dependency and env management. To install Poetry, run: 
```shell
curl -sSL https://install.python-poetry.org | python -
```
After installing Poetry, it might tell you to add something to your shell profile script (eg. `echo 'export PATH="$HOME/.poetry/bin:$PATH"' >> ~/.zshrc`). Make sure to do this if it tells you to. 

>Note: be sure to restart your terminal or run: `source ~/.zshrc` to make sure the changes take effect. Run `poetry --version` to check that Poetry is installed correctly.


## Testing the APIs 
To test the APIs, you can use the Swagger UI at `http://localhost:9000/docs`. 
