# XtractValue


## Infra used

- https://connect.posit.cloud/albankerloch (alban.kerloch@gmail.com)
- AWS for Tesseract (alban / alban.kerloch@gmail.com)

## Before launching

Write the Open Router password in the .env file (OPENROUTER_API_KEY)

## To launch the streamlit

- python3 -m venv .venv
- source .venv/bin/activate (ou .venv\Scripts\activate sur Windows)
- pip install -r requirements.txt
- streamlit run src/app.py

## To regenerate the back

- python3 -m venv .venv
- source .venv/bin/activate (ou .venv\Scripts\activate sur Windows)
- pip install -r requirements.txt
- aws sso login --profile AdministratorAccess-004843573718 (log in AWS)
- python src/main.py
