# Use Python 3.10 as the base image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy the project files into the container
COPY . /app

# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the inference script
CMD ["python", "inference.py"]