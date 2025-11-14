# Use official Python image for backend
FROM python:3.10-slim AS backend

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential libpoppler-cpp-dev poppler-utils && rm -rf /var/lib/apt/lists/*

# Copy backend files
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
COPY .env.example ./
COPY .env ./
COPY storage ./storage

# Expose backend port
EXPOSE 8000

# Use official Node image for frontend
FROM node:18 AS frontend
WORKDIR /frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install
COPY frontend ./

# Build frontend
RUN npm run build

# Final image
FROM python:3.10-slim
WORKDIR /app

# Copy backend from previous stage
COPY --from=backend /app /app

# Copy built frontend
COPY --from=frontend /frontend/dist /app/frontend/dist

# Expose backend port
EXPOSE 8000

# Start backend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
