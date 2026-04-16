# Stage 1: Build frontend
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY thchat-ui/package.json thchat-ui/package-lock.json* ./

# Install dependencies
RUN npm install

# Copy frontend source
COPY thchat-ui/ ./

# Build frontend
RUN npm run build

# Stage 2: Serve with nginx
FROM nginx:alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx config
COPY deploy/nginx.conf /etc/nginx/conf.d/

# Copy built frontend dist to nginx html directory
COPY --from=builder /app/dist /usr/share/nginx/html

# Expose port 80
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
