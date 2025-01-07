# Build stage
FROM node:18-alpine AS build

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Final stage
FROM node:18-alpine

# Install needed packages
RUN apk --no-cache add ca-certificates

WORKDIR /app

# Copy from build stage
COPY --from=build /app/package*.json ./
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/*.js ./

# Expose port
EXPOSE 8085

# Start the application
CMD ["node", "index.js"]