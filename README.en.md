# **Car QR Service**

This is my first learning project with FastAPI, aiming to create a useful service, 
learn FastAPI, and have fun in the process.

## **_For Developers_**

This guide will help you set up the project locally for development.

### **1. Initial Setup**

Prerequisites:

Python 3.10+ installed

Package manager Poetry installed

Steps:

Clone the repository:

`git clone <URL of your repository>`
`cd car_qr_service`

Install dependencies:
This command will create a virtual environment and install all the necessary libraries from the pyproject.toml file.

poetry install

Configure environment variables:
Create a .env file in the project's root directory. The easiest way is to copy the example file:

`cp .env.example .env`

Then, generate a secret key for JWT tokens:

`poetry run python -c "import secrets; print(secrets.token_hex(32))"`

Open the .env file and paste the generated key into the JWT_SECRET_KEY variable.

### **_2. Database Setup (Alembic)_**

Alembic is our tool for managing database schema versions.

Initialize Alembic (run only once):
If the project does not have an alembic folder yet, run this command:

`poetry run alembic init -t async alembic`

_**-t async**_ — template for asynchronous projects.

Configure alembic.ini:
Make sure that in the alembic.ini file, the sqlalchemy.url line corresponds to your database path 
(it is usually taken from the settings, so this step can be skipped if env.py is configured correctly).

Configure alembic/env.py:
Alembic needs to know about our SQLAlchemy models. 
Make sure the alembic/env.py file is configured to automatically read metadata from our project's Base. 
The detailed code for this step is usually already in the repository.

Apply migrations:
To create all tables in the database, run:

`poetry run alembic upgrade head`

This command will apply all existing migrations.

### **_3. Running the Application_**

To run the web server, execute the command:

`poetry run uvicorn src.car_qr_service.main:app --reload --port 8001`

**_--reload_** - will automatically restart the server on code changes.

**_--port 8001_** - specifies the port to run on.

After launch, the API will be available at http://127.0.0.1:8001, and the interactive documentation at http://127.0.0.1:8001/docs.

### **_4. Running Tests_**

To run all automated tests, execute the command:

`poetry run pytest`