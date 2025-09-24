# XtractValue


## Infra used

- https://connect.posit.cloud/albankerloch (alban.kerloch@gmail.com)
- AWS for Tesseract (alban / alban.kerloch@gmail.com)

## Before launching

Write the Open Router password in the .env file (OPENROUTER_API_KEY)

## To local launch

- python3 -m venv .venv
- source .venv/bin/activate (ou .venv\Scripts\activate sur Windows)
- pip install -r requirements.txt
- aws sso login --profile AdministratorAccess-004843573718 (log in AWS)
- streamlit run src/app.py

## Docker

### Create image


### Launch container
* Copy ``docker-compose.yml`` where you want
* Go in folder where ``docker-compose.yml`` file was copied
* Execute following command line :
    ```commandline
    docker compose up -d
    ```