FROM python:3.9

# Change into the source directory
WORKDIR /bot

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "python", "./main.py" ]