FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy project files
COPY . .

# Add this for hot reload to work
ENV CHOKIDAR_USEPOLLING=true

# Expose Vite port
EXPOSE 5173

# Start development server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]