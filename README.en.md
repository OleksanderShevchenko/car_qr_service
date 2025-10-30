# **Car QR Service**

This is my first FastAPI tutorial project, the goal of which is to create a useful service,
learn FastAPI and have fun with the process.

## **For developers**

This tutorial will help you set up the project locally for development.

### **1. Initial setup**

Requirements:

Python 3.10+ installed

Poetry package manager installed (latest versions 2.x+ recommended)

Steps:

Clone the repository:

`git clone <URL of your repository>`

`cd car_qr_service`

Install dependencies:

This command will create a virtual environment and install all the required libraries from the pyproject.toml file.

Set up environment variables:

Create a .env file in the root directory of the project (you can simply copy .env.example if it exists, or create it from scratch).
The easiest way to do this is to copy the example file:

`cp .env.example .env`

For SQLite (main branch):
The .env file should only contain the secret key for the JWT. No other database settings are needed, 
as config.py is set to sqlite+aiosqlite:///./car_qr.db by default.

For PostgreSQL (deployment branch):
The .env file should also contain your Postgres connection details (USER, PASSWORD, SERVER, PORT, DB).

Generate the secret key:
Run the command and copy the result to the .env file:

`poetry run python -c "import secrets; print(secrets.token_hex(32))"`

Open the .env file and paste the generated key into the **JWT_SECRET_KEY** variable.

.env should look something like this:

JWT_SECRET_KEY=your_generated_key

JWT_ALGORITHM=HS256

ACCESS_TOKEN_EXPIRE_MINUTES=30

### **2. Database Configuration (Alembic)**

Important: The alembic folder (including the env.py file and the versions/ subfolder with all migration files) 
and the alembic.ini file in this repository are already fully configured and should be in version control (Git).

DO NOT EXECUTE the command

`poetry run alembic init -t async alembic`

This command is intended to create a project from scratch and will overwrite your correct configuration 
with empty templates, which will result in errors (such as NoSuchModuleError).

All you need to do is apply the migrations that already exist
to create the tables in your database.

Applying migrations:
To create all tables in the database (car_qr.db), run:

`poetry run alembic upgrade head`

This command will automatically read the configured alembic/env.py, find the DB_URL in your config.py, and create the database.

### **3. Starting the application**

To start the web server, run the command:

`poetry run uvicorn src.car_qr_service.main:app --reload --port 8001`

_**--reload**_ will automatically restart the server when the code changes.

**_--port 8001_** specifies the port to start.

After starting, the API will be available at http://127.0.0.1:8001,
and the interactive documentation at http://127.0.0.1:8001/docs.

### **4. Running Tests**

To run all automated tests, run the command:

`poetry run pytest`