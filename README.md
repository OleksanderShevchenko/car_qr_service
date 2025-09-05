**Car QR Service**

It is my first learning project with FastAPI to make some valuable service, learn FastAPi and get fun.

**Для розробників**

**2. Як сконфігурувати Alembic:**
Alembic потрібно знати дві речі: 
    1) до якої бази даних підключатись; 
    2) де шукати наші моделі даних (`User`, `Car`).
Одразу після клонування цього проєкт і створення віртуального середовища
в терміналі вводимо команду ініціалізації Alembic:

    `poetry run alembic init -t async alembic`

* `-t async` — це шаблон для асинхронних проєктів, саме те, що нам потрібно.
* `alembic` — назва директорія, куди будуть складатись файли конфігурації та самі міграції.

Після виконання в вас має з'явиться файл `alembic.ini` та директорія `alembic`.

* **Крок 2.1: Вказуємо шлях до БД.**
    Відкрий файл `alembic.ini`. Знайди рядок `sqlalchemy.url = ...` і заміни його на URL з нашого файлу конфігурації:
    ```ini
    sqlalchemy.url = sqlite+aiosqlite:///./car_qr.db
    ```
    Ця url має збігатися з тим що у класі Settings з config.py


* **Крок 2.2: Вказуємо, де наші моделі.**
    Це найважливіший крок. Відкрий файл `alembic/env.py`.
    * Знайди рядок `target_metadata = None` (приблизно рядок 25).
    * Нам потрібно імпортувати базовий клас `Base` з наших моделей і всі самі моделі, щоб Alembic міг їх "побачити".
    * Заміни блок коду від `from logging.config import fileConfig` до `target_metadata = None` на цей код:

    ```python
    # alembic/env.py - ПОЧАТОК ЗМІН

    import sys
    from pathlib import Path
    from sqlalchemy import pool
    from sqlalchemy.engine import Connection

    # Додаємо корінь проєкту (де лежить папка src) до шляхів пошуку модулів
    # Це потрібно, щоб Alembic міг знайти наші модулі, такі як src.car_qr_service
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

    from logging.config import fileConfig
    from sqlalchemy.ext.asyncio import create_async_engine, async_engine_from_config
    from alembic import context

    # Імпортуємо наш базовий клас для моделей та самі моделі
    from src.car_qr_service.database.database import Base
    from src.car_qr_service.database.models import User, Car # noqa
    # Імпортуємо наші налаштування, щоб взяти DB_URL
    from src.car_qr_service.config import settings

    # Це об'єкт Alembic Config, який надає доступ до
    # значень у файлі .ini.
    config = context.config

    # Встановлюємо sqlalchemy.url з наших налаштувань
    # Це гарантує, що Alembic і додаток дивляться на одну і ту ж БД
    config.set_main_option('sqlalchemy.url', settings.DB_URL)

    # Інтерпретуємо конфігураційний файл для логування Python.
    if config.config_file_name is not None:
        fileConfig(config.config_file_name)

    # target_metadata — це місце, де Alembic шукає моделі для автогенерації.
    # Ми вказуємо йому на Base.metadata з нашого проєкту.
    target_metadata = Base.metadata

    # alembic/env.py - КІНЕЦЬ ЗМІН
        **Примітка:** `# noqa` біля імпорту моделей каже лінтеру ігнорувати той факт, що ми нібито не використовуємо ці імпорти прямо в цьому файлі. Насправді вони потрібні, щоб SQLAlchemy зареєстрував моделі.

**3. Створення першої міграції:**
Тепер, коли Alembic налаштований, даймо йому команду порівняти наші моделі з порожньою базою даних і створити скрипт для приведення її у відповідність.
```bash
poetry run alembic revision --autogenerate -m "Create user and car tables"
* `--autogenerate` — команда для автоматичного створення міграції.
* `-m "..."` — коментар, який описує суть змін.

Якщо все правильно, у папці `alembic/versions` з'явиться новий Python-файл з дивною назвою (наприклад, `8d7c..._create_user_and_car_tables.py`). Це і є наша міграція.

**4. Застосування міграції:**
Останній крок — виконати цей скрипт.
```bash
poetry run alembic upgrade head
Команда `upgrade head` застосовує всі міграції до останньої версії.

Після цього в корені твого проєкту з'явиться файл `car_qr.db` (або те що ви вказали як назву). Це і є наша база даних SQLite, і всередині неї вже є таблиці `users` та `cars` з усіма полями, які ми визначили!

Спробуй виконати ці кроки. Це може здатися складним, але це одноразове налаштування, яке потім робить роботу з базою даних неймовірно зручною.