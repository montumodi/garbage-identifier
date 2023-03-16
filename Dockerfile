FROM python:3.7-slim

ENV APP_HOME /app

WORKDIR $APP_HOME

RUN pip install -U pip
RUN pip install --no-cache-dir gunicorn dash numpy~=1.17.5 tensorflow~=2.0.2 flask~=2.1.2 pillow~=7.2.0 protobuf~=3.20.0
RUN pip install --no-cache-dir mscviplib==2.200731.16

ENV PYTHONUNBUFFERED True

# Install Python dependencies and Gunicorn
# ADD requirements.txt . 
# RUN pip install --no-cache-dir -r requirements.txt \
#     && pip install --no-cache-dir gunicorn
RUN groupadd -r app && useradd -r -g app app

# Copy the rest of the codebase into the image
COPY --chown=app:app . ./
USER app

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available in Cloud Run.
CMD exec gunicorn --bind :$PORT --log-level info --workers 1 --threads 8 --timeout 0 app:server
