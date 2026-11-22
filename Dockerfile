FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ACEest_Fitness.py test_aceest.py ./

ENV APP_VERSION=3.2.4
EXPOSE 5000

CMD ["python", "ACEest_Fitness.py"]
