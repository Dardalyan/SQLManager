# 🗄️ SQLManager
This is a lightweight, modular, and practical SQLAlchemy-based package designed to support multiple database workflows under a single manager layer.

Instead of forcing only one style, `SQLManager` is built to handle real-world mixed scenarios such as:

- direct raw SQL execution
- database-first runtime reflection
- explicit database-first model classes with IDE support
- code-first schema management with Alembic migrations
- clean separation between model definitions and repository/persistence logic

Rather than acting like a heavy framework, this package follows a more engineering-oriented approach.
It stays close to `SQLAlchemy`, but organizes the common connection, ORM, metadata, and migration concerns into a reusable structure.

The result is a package that is:

- Lightweight
- Modular
- Practical
- Easily extensible

At its core:

- `SQLAlchemy` is used for engine, session, ORM, reflection, and metadata handling
- `Alembic` is used for schema migration support

---

## 📚 Table of Contents

- [📂 Project Structure](#project-structure)
- [🛠️ Setup](#setup)
- [🧠 What This Package Solves](#what-this-package-solves)
- [🏗️ Core Idea](#core-idea)
- [🧭 Choosing the Right Approach](#choosing-the-right-approach)
- [🧩 Supported Database Engines](#supported-database-engines)
- [🚀 Quick Start](#quick-start)
- [📦 Module: `manager`](#module-manager)
- [📦 Module: `service`](#module-service)
- [📦 Module: `model`](#module-model)
- [📦 Module: `repository`](#module-repository)
- [🧪 Usage Scenarios](#usage-scenarios)
- [🧩 End-to-End Examples](#end-to-end-examples)
- [⚠️ Notes](#notes)

---

## 📂 Project Structure

```text
.
|-- README.md
|-- requirements.txt
|-- manager/
|   |-- __init__.py
|   |-- BaseManager.py        # Core SQL connection and raw query execution
|   `-- SQLManager.py         # Higher-level manager with Session, Meta, HintBase and StaticBase
|-- model/
|   |-- __init__.py
|   `-- BaseModel.py          # BaseModel, StaticBaseModel and HintBaseModel
|-- repository/
|   |-- __init__.py
|   `-- BaseRepository.py     # Generic repository with query and persistence helpers
|-- service/
|   |-- __init__.py
|   |-- ORMRegistrator.py     # External ORM class registry
|   `-- Migration.py          # Alembic-based migration helper
`-- file_manager/
    |-- __init__.py
    `-- FileManager.py        # Local helper used by the migration service
```

### 🔹 Folder Summary

- `manager/` contains the connection layer and ORM-aware manager classes
- `model/` contains reusable model base classes
- `repository/` contains reusable generic repository helpers
- `service/` contains the ORM registration and migration helpers
- `file_manager/` contains a local file utility used by the migration service

---

## 🛠️ Setup

Install the dependencies:

```bash
pip install -r requirements.txt
```

Current core dependencies:

```text
SQLAlchemy>=2.0
alembic>=1.13
```

Depending on your target database, you may also need a driver package:

- PostgreSQL: `psycopg` or `psycopg2-binary`
- MSSQL: `pyodbc`
- MySQL: `pymysql` or `mysqlclient`
- MariaDB: `mariadb`

### 🔹 Example driver installation

```bash
pip install pyodbc
```

---

## 🧠 What This Package Solves

Many projects do not stay in one single database style forever.

Sometimes:

- the database already exists and you only want to reflect it
- the database already exists but you still want explicit model classes for IDE support
- you want model changes to become schema migrations
- you only want a clean raw SQL manager without ORM models
- you want model definitions separated from persistence/repository operations

`SQLManager` was written to support all of those cases under one package.

Without this kind of structure, projects often end up with:

- scattered connection setup
- repeated session boilerplate
- mixed raw SQL and ORM usage without a clear boundary
- migration logic disconnected from model logic

This package centralizes those responsibilities while still staying close to SQLAlchemy itself.

---

## 🏗️ Core Idea

The package is based on a simple idea:

1. If you only want raw SQL, use `SQLBaseManager`.
2. If you want runtime access to existing tables, use `SQLManager` and `db.Meta`.
3. If you want explicit Python classes for an existing schema, use `HintBase` or `HintBaseModel`.
4. If you want your Python model changes to be reflected in the database through Alembic, use `StaticBase` or `StaticBaseModel`.

This difference is the most important concept in the package.

---

## 🧭 Choosing the Right Approach

### 🔹 1. Runtime database-first access: `db.Meta`

If your database already exists and you do not want to define Python model classes manually, `SQLManager` can reflect tables dynamically at runtime.

After `connect()`, all resolved classes become accessible through `db.Meta`.

```python
users = db.Meta.users
rows = db.Session.query(users).all()
```

Use this approach when:

- the database already exists
- runtime reflection is enough
- you do not need explicit Python classes
- `db.Meta.TableName` access is acceptable

### 🔹 2. Explicit database-first models: `HintBase` and `HintBaseModel`

If the database already exists but you still want explicit Python classes so the IDE can show model properties and give autocomplete, then your models should inherit from `HintBase` or `HintBaseModel`.

This is for database-first projects where:

- the schema already exists in the database
- you want to write `User` instead of `db.Meta.users`
- you want editor support and readable model code
- you do not want these models to drive migrations

#### Important

- `HintBase` is for explicit database-first model classes
- `HintBase` models are prepared against the existing database schema
- `HintBase` models are registered through `ORMRegistrator`
- `HintBase` is not the migration source of the package

### 🔹 3. Code-first migration-aware models: `StaticBase` and `StaticBaseModel`

If model changes should be reflected in the database schema through migration generation, then your models must inherit from `StaticBase` or `StaticBaseModel`.

This is for code-first projects where:

- Python classes are the source of truth
- schema changes should be versioned
- Alembic should compare models against the database
- new tables and column changes should be driven from code

#### Important

- migration support in this package is intentionally built around `StaticBase`
- the migration service rewrites Alembic `env.py`
- during that rewrite it sets `target_metadata = StaticBase.metadata`
- for that reason, migration generation follows `StaticBase`, not `HintBase`

### 🔹 Decision Summary

| Need | Recommended choice |
|------|--------------------|
| Only raw SQL and connection handling | `SQLBaseManager` |
| Existing database, no explicit classes needed | `SQLManager` + `db.Meta` |
| Existing database, explicit model classes needed | `HintBase` or `HintBaseModel` |
| Code-first schema design with migration support | `StaticBase` or `StaticBaseModel` |

---

## 🧩 Supported Database Engines

The package currently supports these engine types through the `SQLEngine` enum:

- `POSTGRES`
- `MSSQL`
- `MYSQL`
- `MARIADB`

### 🔹 MSSQL note

For `MSSQL`, the connection string builder currently appends:

- `driver=ODBC+Driver+18+for+SQL+Server`
- `TrustServerCertificate=yes`
- `Encrypt=yes`

---

## 🚀 Quick Start

Basic flow with `SQLManager`:

1. create the manager
2. call `set_model_import(...)`
3. configure connection with `setup(...)`
4. use `set_orm(...)` for explicit `HintBase` or `HintBaseModel` classes
5. call `connect()`
6. use raw SQL, `Meta`, or explicit model classes depending on your approach

### 🔹 Minimal raw SQL example

```python
from SQLManager.manager import SQLBaseManager, SQLEngine

db = SQLBaseManager()
db.setup(
    sql_engine=SQLEngine.POSTGRES,
    ip="127.0.0.1",
    port=5432,
    db_name="sample_db",
    user_name="postgres",
    password="secret"
)

db.connect()
db.set_query("SELECT * FROM users WHERE id = %s", 1)
rows = db.execute()

for row in rows:
    print(row)

db.disconnect()
```

### 🔹 Minimal `SQLManager` example

```python
from SQLManager.manager import SQLManager, SQLEngine

db = SQLManager()
db.set_model_import("models")
db.setup(
    sql_engine=SQLEngine.POSTGRES,
    ip="127.0.0.1",
    port=5432,
    db_name="sample_db",
    user_name="postgres",
    password="secret"
)
db.connect()

print(db.Meta)
```

---

## 📦 Module: `manager`

### 🔹 `SQLBaseManager`

`SQLBaseManager` is the low-level SQL layer of the package.

It is responsible for:

- building the connection string
- creating and disposing the SQLAlchemy engine
- opening raw connections
- preparing raw SQL queries
- executing parameterized SQL

It is the right choice when you do not need `Meta`, sessions, ORM registration, or migrations.

#### Main methods

- `setup(...)`
- `connect()`
- `get_connection()`
- `disconnect()`
- `set_query(...)`
- `execute()`

### 🔹 `SQLManager`

`SQLManager` extends `SQLBaseManager` and adds:

- SQLAlchemy `Session` support
- runtime automap reflection
- the `Meta` container
- integration with registered explicit ORM classes
- direct preparation flow for `HintBase`-based models

This is the main manager class of the package.

#### Internal flow during `connect()`

When `connect()` runs:

1. the base engine is created
2. a `Meta` object is initialized
3. registered `HintBase` classes are prepared if present
4. automap reflection runs against the current database
5. reflected classes are attached to `Meta`
6. a session factory is created

#### Important requirement

Before calling `connect()`, you must call:

```python
db.set_model_import("models")
```

This is required in the current manager flow.

### 🔹 `Meta`

`Meta` is a lightweight object used to expose runtime-resolved ORM classes.

You can access items like:

```python
db.Meta.users
db.Meta["users"]
```

This is the most direct way to work in database-first mode without defining explicit model classes.

### 🔹 `HintBase`

`HintBase` is for explicit model classes in database-first workflows.

Use it when:

- the schema already exists
- you want explicit Python classes
- you want IDE autocomplete and visible properties
- you do not want migrations to be generated from these models

### 🔹 `StaticBase`

`StaticBase` is for code-first schema-driven development.

Use it when:

- your Python model classes should define the schema
- migration generation should follow model changes
- database changes should be driven from code

The migration service is intentionally built around `StaticBase.metadata`.

---

## 📦 Module: `service`

### 🔹 `ORMRegistrator`

`ORMRegistrator` is a small registry used to register explicit model classes outside the manager.

It exists because `SQLManager` should not need to know your application models in advance.
You define your models in your own modules, then register them and inject them into the manager.

#### Main methods

- `register(cls)`
- `get_model(cls | str)`
- `load()`

### 🔹 `Migration`

`Migration` is the code-first migration helper built on top of Alembic.

It is mainly designed for models based on `StaticBase`.

#### What it does

- initializes a `migrations/` folder when needed
- configures Alembic
- rewrites Alembic `env.py`
- injects the model import into Alembic
- sets migration metadata to `StaticBase.metadata`
- adds `include_object(...)` filtering
- creates revisions
- upgrades the database
- downgrades revisions
- rebuilds migration history when needed
- stamps head when needed

#### Common migration methods

```python
migration.make_migration("add_products_table", autogenerate=False)
migration.update_database()
migration.downgrade_migration("-1")
migration.rebuild_migrations()
migration.stamp_head()
```

---

## 📦 Module: `model`

### 🔹 `BaseModel`

`BaseModel` is an abstract marker base.

It does not provide built-in CRUD/query/session methods.
Persistence operations are expected to be handled by repository classes (for example classes under `repository/`).

### 🔹 `HintBaseModel`

`HintBaseModel` combines:

- `BaseModel`
- `HintBase`

Use this when:

- the database already exists
- you want explicit model classes
- you want IDE support
- you do not want these models to drive migrations

### 🔹 `StaticBaseModel`

`StaticBaseModel` combines:

- `BaseModel`
- `StaticBase`

Use this when:

- your model should define the schema
- model changes should be migration-aware

---

## 📦 Module: `repository`

### 🔹 `BaseRepository`

`BaseRepository` is a generic repository helper for session-based query and persistence operations.

It is designed to work with:

- `SQLManager` session
- model classes derived from `BaseModel` (including `HintBaseModel` and `StaticBaseModel`)

#### Main methods

- `all()`
- `first()`
- `get_by_id(id_value)`
- `filter_by(**kwargs)`
- `add(obj)`
- `add_range(objects)`
- `update(obj)`
- `update_range(objects)`
- `delete(obj)`
- `delete_range(objects)`
- `commit()`
- `rollback()`
- `flush()`

#### Example

```python
from SQLManager.manager import SQLManager, SQLEngine
from SQLManager.repository.BaseRepository import BaseRepository
from models import User

db = SQLManager()
db.set_model_import("models")
db.setup(
    sql_engine=SQLEngine.POSTGRES,
    ip="127.0.0.1",
    port=5432,
    db_name="sample_db",
    user_name="postgres",
    password="secret"
)
db.connect()

user_repo = BaseRepository(db=db, model=User)

all_users = user_repo.all()
first_user = user_repo.first()
active_users = user_repo.filter_by(is_active=True)

new_user = user_repo.add(User(name="Alice"))
user_repo.commit()
```

---

## 🧪 Usage Scenarios

### 🔹 1. Only raw SQL

Use `SQLBaseManager` when you only need:

- connection handling
- raw SQL execution
- parameterized queries

### 🔹 2. Existing database with dynamic class access

Use `SQLManager` + `db.Meta` when:

- the database already exists
- runtime reflection is enough
- you do not want to define models manually

### 🔹 3. Existing database with explicit classes

Use `HintBase` or `HintBaseModel` when:

- the database already exists
- you want explicit model classes
- you want IDE-visible fields
- you do not want these models to drive migrations

### 🔹 4. Code-first schema tracking

Use `StaticBase` or `StaticBaseModel` when:

- your model classes define the schema
- you want migration tracking

### 🔹 5. Repository-based persistence flow

Use `BaseRepository` when:

- you want model logic and persistence logic to stay separate
- you need generic CRUD/query helpers bound to a `SQLManager` session
- you prefer repository pattern over model-bound persistence helpers

---

## 🧩 End-to-End Examples

### 🔹 Example 1: Runtime reflection with `Meta`

```python
from SQLManager.manager import SQLManager, SQLEngine

db = SQLManager()
db.set_model_import("models")
db.setup(
    sql_engine=SQLEngine.POSTGRES,
    ip="127.0.0.1",
    port=5432,
    db_name="sample_db",
    user_name="postgres",
    password="secret"
)
db.connect()

UserTable = db.Meta.users
users = db.Session.query(UserTable).all()
```

### 🔹 Example 2: Database-first explicit model with `HintBase`

```python
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from SQLManager.manager import SQLManager, SQLEngine, HintBase 
from SQLManager.service import ORMRegistrator


class User(HintBase):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))


db = SQLManager()
db.set_model_import("models")
db.setup(
    sql_engine=SQLEngine.POSTGRES,
    ip="127.0.0.1",
    port=5432,
    db_name="sample_db",
    user_name="postgres",
    password="secret"
)

registry = ORMRegistrator()
registry.register(User)
db.set_orm(registry)

db.connect()

users = db.Session.query(User).all()
```

### 🔹 Example 3: Code-first model with `StaticBase`

```python
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from SQLManager.manager import SQLManager, SQLEngine, StaticBase
from SQLManager.service.Migration import Migration


class Product(StaticBase):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(150))


db = SQLManager()
db.set_model_import("models")
db.setup(
    sql_engine=SQLEngine.POSTGRES,
    ip="127.0.0.1",
    port=5432,
    db_name="sample_db",
    user_name="postgres",
    password="secret"
)

db.connect()

migration = Migration(manager=db, model_import="models")
migration.make_migration("initial", autogenerate=False)
migration.update_database()
```

### 🔹 Example 4: Repository usage with explicit model class

```python
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from SQLManager.manager import SQLManager, SQLEngine
from SQLManager.model.BaseModel import HintBaseModel
from SQLManager.service import ORMRegistrator
from SQLManager.repository.BaseRepository import BaseRepository


class User(HintBaseModel):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100))


db = SQLManager()
db.set_model_import("models")
db.setup(
    sql_engine=SQLEngine.POSTGRES,
    ip="127.0.0.1",
    port=5432,
    db_name="sample_db",
    user_name="postgres",
    password="secret"
)

registry = ORMRegistrator()
registry.register(User)
db.set_orm(registry)
db.connect()

user_repo = BaseRepository(db=db, model=User)
users = user_repo.all()

user_repo.add(User(name="Alice"))
user_repo.commit()
```

---

## ⚠️ Notes

- `SQLManager.connect()` expects `set_model_import(...)` to be called first.
- `ORMRegistrator` exists so explicit ORM classes can be kept outside the manager and injected when needed.
- `HintBase` and `HintBaseModel` are for database-first explicit models, not migration metadata.
- `StaticBase` and `StaticBaseModel` are the migration-aware bases of the package.
- The migration service rewrites Alembic `env.py` and sets `target_metadata = StaticBase.metadata`.
- `BaseModel` is an abstract marker, not a built-in CRUD layer in the current version.
- `BaseRepository` is the current reusable query/persistence helper layer.
- `file_manager/` is included as a local helper package for migration/file operations.
- The package does not try to replace SQLAlchemy; it organizes it into a reusable and practical module.

