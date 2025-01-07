# Build stage
FROM golang:1.23-alpine AS build
WORKDIR /app

# Copy go mod and sum files
COPY go.mod go.sum ./
RUN go mod tidy

# Copy the source code and all directories
COPY . .

# Build the application
RUN go build -o notification-service .

# Final stage
FROM alpine:latest
RUN apk --no-cache add ca-certificates

WORKDIR /app
# Copy the binary from build stage
COPY --from=build /app/notification-service .
# Copy templates directory
COPY --from=build /app/templates ./templates

EXPOSE 8082
EXPOSE 8083
CMD ["./notification-service"]