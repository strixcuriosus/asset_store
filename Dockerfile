FROM python:3-onbuild

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt
COPY . /app
RUN pip install -r /app/requirements.txt

EXPOSE 5000

ENTRYPOINT [ "python" ]
CMD [ "run.py" ]
