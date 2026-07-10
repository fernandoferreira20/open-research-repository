FROM python:3.12-slim

# Set the working directory inside the container.
WORKDIR /app

# Copy the backend dependency list and install packages.
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code into the container.
COPY . .

# Expose the Flask development port.
EXPOSE 5000

# Run the Flask application when the container starts.
CMD ["python", "run.py"]
