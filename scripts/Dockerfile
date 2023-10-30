##This dockerfile creates a jupyterlab image that contains the 'STAC_creation_latest.ipynb' script. 
##The dockerfile uses conda to install software that is required including pdal and gdal. The required software is specified in 'osgeo_environment.yml'

FROM harbor.cyverse.org/vice/jupyter/datascience:4.0.1

USER jovyan

# Clean up conda
RUN conda update conda 
RUN conda config --remove channels conda-forge
RUN conda config --add channels conda-forge
RUN conda config --set channel_priority strict

RUN conda install -c conda-forge mamba 

# Create OSGEO environment using mamba
COPY osgeo_environment.yml /home/jovyan/
RUN ls /home/jovyan/ 
RUN mamba env create -f /home/jovyan/osgeo_environment.yml

# using ~/.bash_profile instead of ~/.bashrc for non-interactive tty (-it) containers
RUN echo ". /opt/conda/etc/profile.d/conda.sh" >> /home/jovyan/.bash_profile && \
    echo "conda activate osgeo" >> /home/jovyan/.bash_profile
RUN . /opt/conda/etc/profile.d/conda.sh && conda deactivate && conda activate osgeo && ipython kernel install --name "osgeo" --user 

# Source BASH profile
RUN source /home/jovyan/.bash_profile

COPY STAC_creation_latest.ipynb /home/jovyan
CMD ["start-notebook.sh", "STAC_creation_latest.ipynb"]

# Build it
#RUN jupyter lab build

# Clean it up
RUN mamba clean --all -f -y

