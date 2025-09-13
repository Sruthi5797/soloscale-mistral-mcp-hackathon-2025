FROM node:20-slim

RUN apt-get update && apt-get install -y \
    python3 make g++ libc6 libstdc++6 libpng-dev libjpeg-dev libvips-dev \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY package.json ./
RUN npm ci --silent

COPY server.js poses.ref.json ./

ENV POSEFLOW_BACKEND_PORT=4000
EXPOSE 4000
CMD ["npm", "start"]