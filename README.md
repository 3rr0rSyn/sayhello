# SayHello

*Say hello to the world.*

> Example application for *[Python Web Development with Flask](https://helloflask.com/en/book/1)* (《[Flask Web 开发实战](https://helloflask.com/book/1)》).

This fork has been updated to run on modern Python (3.11+) and Flask 3.x, and includes a simple admin backend for managing messages.

## Features

- Post and view messages
- Simple admin backend with CRUD, search and pagination
- Compatible with Python 3.11 / 3.12 / 3.13

## Installation

Clone:
```bash
$ git clone https://github.com/3rr0rSyn/sayhello.git
$ cd sayhello
```

Create & activate virtual env then install dependencies:

```bash
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

Initialize the database and run:

```bash
$ flask initdb
$ flask run
 * Running on http://127.0.0.1:5000/
```

You can also generate fake data with:

```bash
$ flask forge
```

## Admin Backend

Visit `/admin/` and log in with the default password `admin`.  
**Important:** change the admin password in production by setting the `ADMIN_PASSWORD` environment variable.

## Deployment

For deploying with BT Panel (宝塔面板), see the [宝塔部署.md](宝塔部署.md) guide.

## License

This project is licensed under the MIT License (see the
[LICENSE](LICENSE) file for details).
