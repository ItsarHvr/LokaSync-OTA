FROM nginx:stable-alpine-slim

# Set the maintainer label
LABEL author="LokaSync team"
LABEL description="LokaSync frontend web server"
LABEL version="1.0.0"

# Set environment variables
ENV NGINX_USER="nginx"
ENV NGINX_PORT="80"

# Remove default nginx website
RUN rm -rf /usr/share/nginx/html/*

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create directories for frontend assets
RUN mkdir -p /usr/share/nginx/html

# Set proper permissions
RUN chown -R $NGINX_USER:$NGINX_USER /usr/share/nginx/html
RUN chmod -R 755 /usr/share/nginx/html

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:$NGINX_PORT/health || exit 1

# Expose port
EXPOSE $NGINX_PORT

# Start nginx
CMD ["nginx", "-g", "daemon off;"]