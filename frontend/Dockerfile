# Frontend Dockerfile for Railway deployment
FROM node:18-alpine as build

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build the app
RUN npm run build

# Production stage with nginx
FROM nginx:alpine

# Copy built files
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx configuration template and startup script
COPY nginx.conf.template /etc/nginx/conf.d/default.conf.template
COPY start-nginx.sh /start-nginx.sh
RUN chmod +x /start-nginx.sh

# Expose port (Railway will use $PORT environment variable)
EXPOSE 8080

# Start nginx with environment variable substitution
CMD ["/start-nginx.sh"]
