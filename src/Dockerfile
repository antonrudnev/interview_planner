FROM python:3.7.5-slim

RUN mkdir -p /interview_planner

WORKDIR /interview_planner

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD flask run -h 0.0.0.0

