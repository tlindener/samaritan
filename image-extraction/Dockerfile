FROM continuumio/miniconda3:latest

# Install extra packages if required
RUN apt-get update && apt-get install libgl1-mesa-swx11 -y \
    && rm -rf /var/lib/apt/lists/*

# Add the user that will run the app (no need to run as root)
RUN groupadd -r samaritan && useradd -r -g samaritan samaritan

WORKDIR /app
RUN conda update pip
RUN conda install numpy scipy
# Install myapp requirements
COPY environment.yml /app/environment.yml
RUN conda config --add channels conda-forge \
    && conda env create -n samaritan-frame-extractor -f environment.yml \
    && rm -rf /opt/conda/pkgs/*

# Install myapp
COPY . /app/
RUN chown -R samaritan:samaritan /app/*

# activate the myapp environment
ENV PATH /opt/conda/envs/samaritan-frame-extractor/bin:$PATH

CMD ["python","-u","producer.py"]
