FROM python:3.8

WORKDIR /src

COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "-m", "news_scheduler"]