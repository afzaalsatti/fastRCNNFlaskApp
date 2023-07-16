# FROM python:3.8-bullseye
FROM python:3.10.11
WORKDIR /
ADD . /project
RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install --upgrade Pillow
RUN apt-get update && apt-get install -y \
    libjpeg-dev \
    libtiff-dev \
    libopenjp2-7-dev \
    zlib1g-dev
RUN apt-get update && apt-get install -y libgl1-mesa-glx
RUN apt-get update && apt-get install -y ffmpeg
RUN pip install -U scikit-image
RUN pip install -U cython 
RUN pip install git+https://github.com/facebookresearch/fvcore.git
RUN pip install "git+https://github.com/philferriere/cocoapi.git#egg=pycocotools&subdirectory=PythonAPI"
COPY detectron2 /home
ENTRYPOINT FLASK_APP=/home/app.py flask run --host=0.0.0.0