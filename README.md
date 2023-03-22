# garbage-identifier

## Build & How to run

```bash
docker build -t custom-vision . && docker run -it -v "/workspaces/garbage-identifier/:/vs/" -p 8080:8080 -e PORT=8080 custom-vision bash

cd /vs

// to run classification
gunicorn --bind :8080 --chdir src/ app:server --reload

// to run object detection
gunicorn --bind :8080 --chdir src/ app_obj:server --reload


```