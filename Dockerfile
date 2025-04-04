# Use official Python runtime as a parent image (Python 3.10-slim)
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Run the chatbot when the container launches
CMD ["python", "chatbot.py"]
