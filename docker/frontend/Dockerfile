FROM node:18-alpine
WORKDIR /app

COPY frontend/package.json frontend/pnpm-lock.yaml ./
RUN npm install -g pnpm && pnpm install

COPY frontend/ .

RUN pnpm build

EXPOSE 3000
CMD ["pnpm", "start"]
