FROM node:20-slim

WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm ci || npm i

COPY tsconfig.json ./
COPY src ./src

RUN npm run build

ENV NODE_ENV=production
ENV PORT=7860
EXPOSE 7860

CMD ["npm", "start"]