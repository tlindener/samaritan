FROM continuumio/miniconda3:latest

# Install extra packages if required
RUN apt-get update && apt-get install wget ca-certificates -y \
    && rm -rf /var/lib/apt/lists/*

# Add the user that will run the app (no need to run as root)
RUN groupadd -r samaritan && useradd -r -g samaritan samaritan

WORKDIR /app
#RUN wget http://pjreddie.com/media/files/yolo.weights && \
#    wget https://raw.githubusercontent.com/pjreddie/darknet/master/cfg/yolo.cfg

RUN conda install numpy scipy

# Install myapp requirements
COPY environment.yml /app/environment.yml
RUN conda config --add channels conda-forge \
    && conda env create -n samaritan-person-detector -f environment.yml \
    && rm -rf /opt/conda/pkgs/*

# Install myapp
COPY . /app/
RUN chown -R samaritan:samaritan /app/*

# activate the myapp environment
ENV PATH /opt/conda/envs/samaritan-person-detector/bin:$PATH
#RUN ./yad2k.py yolo.cfg yolo.weights model_data/yolo.h5
CMD ["python","-u","consumer.py"]
