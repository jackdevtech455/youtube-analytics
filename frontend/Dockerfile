# ---- deps ----
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

# ---- build ----
FROM node:20-alpine AS builder
WORKDIR /app
ENV NODE_ENV=production
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN rm -rf .next && npm run build

# ---- run ----
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production

# Standalone server (contains server.js)
COPY --from=builder /app/.next/standalone ./

# Static assets (REQUIRED for /_next/static/*)
COPY --from=builder /app/.next/static ./.next/static

# Public assets (if you have any)
COPY --from=builder /app/public ./public

EXPOSE 3000
CMD ["node", "server.js"]
