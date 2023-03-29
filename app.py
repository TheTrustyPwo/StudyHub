from app import create_app

if __name__ == '__main__':
    gunicorn_app = create_app()
    gunicorn_app.run()
else:
    gunicorn_app = create_app()
