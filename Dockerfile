FROM python:3.13-slim

WORKDIR /usr/src/app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -ms /bin/sh www-user

RUN chown -R www-user:www-user /usr/src/app

USER www-user

EXPOSE 5000

CMD ["python", "main.py"]