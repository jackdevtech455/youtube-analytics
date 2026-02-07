FROM node:20-alpine

WORKDIR /app

ARG NEXT_PUBLIC_API_BASE
ENV NEXT_PUBLIC_API_BASE=$NEXT_PUBLIC_API_BASE

COPY package.json package-lock.json* ./

RUN npm ci

COPY . .

RUN rm -rf .next && npm run build

EXPOSE 3000
CMD ["node", ".next/standalone/server.js"]
