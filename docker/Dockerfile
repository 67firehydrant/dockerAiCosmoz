# syntax=docker/dockerfile:1

# ---------- Stage 1: Dependencies ----------
FROM node:20-slim AS deps
WORKDIR /app
COPY package.json package-lock.json* ./
# npm ci = install deterministik dari lockfile (lebih konsisten untuk CI)
RUN npm ci

# ---------- Stage 2: Build ----------
FROM node:20-slim AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
ENV NEXT_TELEMETRY_DISABLED=1
RUN npm run build

# ---------- Stage 3: Runtime ----------
FROM node:20-slim AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000
ENV NEXT_TELEMETRY_DISABLED=1

# Jalankan sebagai non-root untuk keamanan
RUN groupadd --system --gid 1001 nodejs \
    && useradd --system --uid 1001 --gid nodejs nextjs

# Salin hasil build standalone (image minimal, tanpa devDependencies)
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD node -e "fetch('http://localhost:3000/').then(r=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"

# server.js dihasilkan oleh Next.js standalone output
CMD ["node", "server.js"]
