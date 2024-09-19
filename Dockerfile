# Use the official Python image from the Docker Hub
FROM python:3.10.14-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . .

# Command to run your application (adjust as necessary)
CMD ["python", "app.py"]