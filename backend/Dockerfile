FROM python:3.13.3-alpine

# Set the maintainer label
LABEL author="LokaSync team"
LABEL description="LokaSync backend service"
LABEL api_version="1"

# Set environment variables
ENV APP_DIR="/home/lokasync/backend"
ENV APP_PORT="8000"
ENV LOCAL_USER="lokasync-backend"
ENV LOCAL_GROUP="lokasync-group"

# Create a non-root user and group
RUN addgroup -S $LOCAL_GROUP && \
  adduser -S $LOCAL_USER -G $LOCAL_GROUP

# Create the application directory
RUN mkdir -p $APP_DIR && \
  chown $LOCAL_USER:$LOCAL_GROUP $APP_DIR && \
  chmod 755 $APP_DIR

# Set the working directory
WORKDIR $APP_DIR

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy the application code
COPY . .

# Change working directory to the src folder
WORKDIR $APP_DIR/src

# Change user to the non-root user
USER $LOCAL_USER

# Expose the application port
EXPOSE $APP_PORT

# Start the application using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]