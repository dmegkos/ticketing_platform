# Use an official Python runtime as a parent image
FROM python:3.9-alpine

# Set the working directory in the container
WORKDIR /app

# Add the current directory contents into the container at /app
COPY . /app

# Update and install dependencies
RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 5000 to the world
EXPOSE 5000

# Run app.py when the container launches
CMD ["python", "app.py"]