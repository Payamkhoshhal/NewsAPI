FROM python:3.9

WORKDIR /code

COPY requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./app /code/app

ENV APIKEY='***********'
ENV DB_NAME='*****'
ENV DB_USER='*****'
ENV PASSWORD='******'
ENV AWS_ACCESS_KEY_ID="************"
ENV AWS_SECRET_ACCESS_KEY="**********"
ENV SEARCH_KEY='serchkeyword'

CMD ["python","/code/app/main.py"]
