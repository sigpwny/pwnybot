FROM python:3.10

# Change into the source directory
WORKDIR /bot

COPY src .

RUN pip install -r requirements.txt

CMD [ "python", "./main.py" ]
