FROM node:20-slim

WORKDIR /app

# Install deps
COPY package.json package-lock.json* ./
RUN npm ci || npm i

# Build
COPY tsconfig.json ./
COPY src ./src
RUN npm run build

# Hugging Face expects the app to listen on $PORT (defaults to 7860)
ENV NODE_ENV=production
ENV HOST=0.0.0.0
ENV PORT=7860
EXPOSE 7860

# Start the server
CMD ["node", "dist/server.js"]