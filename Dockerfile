FROM python:3.9.1
ADD . /flask-app
WORKDIR /flask-app
RUN pip install -r requirements.txt

ENV AM_I_IN_A_DOCKER_CONTAINER=True

# ENTRYPOINT [ "python" ]
# CMD [ "app.py" ]