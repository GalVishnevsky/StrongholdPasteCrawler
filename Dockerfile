
FROM python:3.5.2


# Set the working directory to /app
WORKDIR /app

# Copy the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip3 install -r requirements.txt

EXPOSE 80

# Define environment variable
ENV NAME stronghold-paste

# Run app.py when the container launches
CMD ["python", "main.py"]

