FROM python:3.9-slim

WORKDIR /code

COPY ./backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./backend/app ./app/

EXPOSE 8000

CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000","--reload"]
# 이 도커파일은 직접 구동시키는 것이 아니라
# 상위 폴더에 있는 docker-compose에 의해서 구동된다.