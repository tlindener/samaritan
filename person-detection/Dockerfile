FROM samaritan/base:latest

# Add the user that will run the app (no need to run as root)
RUN groupadd -r samaritan && useradd -r -g samaritan samaritan

WORKDIR /app
RUN wget http://pjreddie.com/media/files/yolo.weights && \
    wget https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolo.cfg

# Install myapp requirements
COPY environment.yml /app/environment.yml
RUN conda env create -n samaritan-person-detection -f environment.yml \
    && rm -rf /opt/conda/pkgs/*

# Install myapp
COPY . /app/
RUN chown -R samaritan:samaritan /app/*

# activate the myapp environment
ENV PATH /opt/conda/envs/samaritan-person-detection/bin:$PATH
RUN python yad2k.py yolo.cfg yolo.weights model_data/yolo.h5
CMD ["python","-u","consumer.py"]
