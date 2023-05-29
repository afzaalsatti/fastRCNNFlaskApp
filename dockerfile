FROM python:3.8-bullseye
WORKDIR /
ADD . /project
RUN pip install --upgrade pip
RUN apt-get update && apt-get install -y libgl1-mesa-glx
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install -U scikit-image
RUN pip install -U cython 
RUN pip install git+https://github.com/facebookresearch/fvcore.git
RUN pip install "git+https://github.com/philferriere/cocoapi.git#egg=pycocotools&subdirectory=PythonAPI"
COPY detectron2 /home
ENTRYPOINT FLASK_APP=/home/app.py flask run --host=0.0.0.0