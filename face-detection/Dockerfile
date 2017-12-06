FROM samaritan/miniconda3:latest

# Install extra packages if required
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Add the user that will run the app (no need to run as root)
RUN groupadd -r samaritan && useradd -r -g samaritan samaritan

WORKDIR /app

# Install myapp requirements
COPY environment.yml /app/environment.yml
RUN conda config --add channels conda-forge \
    && conda env create -n samaritan-face-detector -f environment.yml \
    && rm -rf /opt/conda/pkgs/*

# Install myapp
COPY . /app/
RUN chown -R samaritan:samaritan /app/*

# activate the myapp environment
ENV LD_LIBRARY_PATH /usr/local/cuda/lib64/
ENV LD_LIBRARY_PATH /usr/local/cuda/extras/CUPTI/lib64:$LD_LIBRARY_PATH
ENV PATH /opt/conda/envs/samaritan-face-detector/bin:$PATH

CMD ["python","-u","consumer.py"]
