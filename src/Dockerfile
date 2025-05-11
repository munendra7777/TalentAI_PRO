# Use the official Python image as the base image
FROM arm64v8/python:3.12



# Set the working directory in the container
WORKDIR /app

# Copy the requirements file to the container
COPY requirements.txt .

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir streamlit

# Copy the entire app to the container
COPY . .

# Expose the port that Streamlit runs on
EXPOSE 8080

# Set the Streamlit configuration to run on 0.0.0.0
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_PORT=8080
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Command to run the Streamlit app
CMD ["python", "-m", "streamlit", "run", "main.py", "--server.port=8080", "--server.address=0.0.0.0", "--server.headless=true"]
