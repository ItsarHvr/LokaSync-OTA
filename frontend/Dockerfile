########## STAGE 1 ##########
FROM node:22.16.0-alpine AS builder

# Set the maintainer label
LABEL author="LokaSync team"
LABEL description="LokaSync frontend service"
LABEL version="1.0.0"

# Set environment variables
ENV APP_DIR="/home/lokasync/frontend"
ENV APP_PORT="3000"
ENV LOCAL_USER="lokasync-frontend"
ENV LOCAL_GROUP="lokasync-group"
ENV NODE_ENV="production"

# Create a non-root user and group
RUN addgroup -S $LOCAL_GROUP && \
  adduser -S $LOCAL_USER -G $LOCAL_GROUP

# Create the application directory
RUN mkdir -p $APP_DIR && \
  chown $LOCAL_USER:$LOCAL_GROUP $APP_DIR && \
  chmod 755 $APP_DIR

# Set the working directory
WORKDIR $APP_DIR

# Copy the package-lock.json and install dependencies
COPY package*.json ./
RUN npm ci --only=production --silent

# Copy the application code
COPY . .

# Type check and linting
RUN npm run type-check
RUN npm run lint:fix

# Build the application for production
RUN npm run build:prod

# Verify the build output (dist folder)
RUN ls -la $APP_DIR/dist

# Copy the built files to a specific directory
RUN mkdir -p /dist && \
  chown $LOCAL_USER:$LOCAL_GROUP /dist && \
  chmod 755 /dist && \
  cp -r $APP_DIR/dist/* /dist/

########## STAGE 2 ##########
# Final stage - just the built files
FROM scratch AS dist

# Copy the built files from the builder stage
RUN mkdir -p /dist
COPY --from=builder /dist /dist