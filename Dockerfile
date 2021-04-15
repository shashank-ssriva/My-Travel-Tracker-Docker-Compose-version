FROM python:3.7.10-alpine
COPY requirements.txt /src/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r /src/requirements.txt
COPY app.py /src
COPY tables.py /src
COPY static /src/static
COPY templates /src/templates
COPY tests /src/tests
CMD python3 /src/app.py