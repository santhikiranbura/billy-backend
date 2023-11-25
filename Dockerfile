FROM python:3.9.17

RUN mkdir -p /app/src
WORKDIR /app/src
RUN python3 -m venv .venv
RUN pip3 install Flask spacy python-dateutil waitress flask-cors numerizer nltk
RUN python -m spacy download en_core_web_md

ADD billy.py .venv
ADD run.py .venv

EXPOSE 8082
ENTRYPOINT ["python3","/app/src/.venv/run.py"]