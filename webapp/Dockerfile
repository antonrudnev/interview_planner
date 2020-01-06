FROM python:3.7-slim

WORKDIR /interview_planner

COPY src/requirements.txt .
RUN pip install -r requirements.txt

COPY src/ .

EXPOSE 5000

CMD flask run --host=0.0.0.0 --port=5000

