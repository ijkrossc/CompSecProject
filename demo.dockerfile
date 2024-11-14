#########################################
#/Use an official Python runtime as a base image (Python 3.11, slim version for reduced size)
FROM python:3.11-slim

#Set the working directory inside the container to /alpha_bank
WORKDIR /alpha_bank

#Copy the requirements file to the container. 
#This is done first to leverage Docker's layer caching. 
#If only the requirements change, the Docker cache will be reused for the rest.
COPY requirements.txt .

#Install Python dependencies specified in requirements.txt.
#--no-cache-dir prevents pip from using cache, keeping the image smaller.
RUN pip install --no-cache-dir -r requirements.txt

#Copy the entire project directory (./alpha_bank on the host) to the container's /alpha_bank directory.
#This includes all the project files such as code and configuration files like config.yaml.
COPY ./alpha_bank /alpha_bank

#Set the PYTHONPATH environment variable to include the /alpha_bank directory.
#/This allows the Python interpreter to locate your modules and packages.
ENV PYTHONPATH=/alpha_bank

#Expose port 6201 for communication with the application (e.g., HTTP server or API).
EXPOSE 6201

#The command to run the application when the container starts.
#In this case, it's running the Python server located at ui/server.py.
CMD ["python", "server.py"]
#########################################