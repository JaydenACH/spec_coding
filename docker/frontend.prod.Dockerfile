# Dependencies stage
FROM node:18-alpine AS dependencies

WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci --only=production && npm cache clean --force

# Builder stage
FROM node:18-alpine AS builder

WORKDIR /app
COPY frontend/package*.json ./

# Install all dependencies (including dev dependencies)
RUN npm ci

# Copy source code
COPY frontend/ .

# Build arguments for environment variables
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_WS_URL

# Set environment variables for build
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_WS_URL=$NEXT_PUBLIC_WS_URL
ENV NODE_ENV=production

# Build the application
RUN npm run build

# Production stage
FROM node:18-alpine AS production

WORKDIR /app

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nextjs -u 1001

# Copy package.json for production dependencies
COPY frontend/package*.json ./
RUN npm ci --only=production && npm cache clean --force

# Copy built application from builder stage
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
COPY --from=builder --chown=nextjs:nodejs /app/public ./public

# Switch to non-root user
USER nextjs

# Expose port
EXPOSE 3000

# Set environment variable
ENV PORT 3000
ENV NODE_ENV production

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000 || exit 1

# Start the application
CMD ["node", "server.js"] 