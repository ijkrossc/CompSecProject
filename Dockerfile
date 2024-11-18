# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3-slim

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY . /app

# Expose the port the application runs on
EXPOSE 6201

# During debugging, this entry point will be overridden. For more information, please refer to https://aka.ms/vscode-docker-python-debug
CMD ["python", "alphabank_terminal.py"]
