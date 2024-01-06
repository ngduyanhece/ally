FROM node:20-slim AS base
ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

# Create the directory on the node image 
# where our Next.js app will live
RUN mkdir -p /app


# Set /app as the working directory
WORKDIR /app

# Copy package.json and yarn.lock
# to the /app working directory
COPY package*.json pnpm-lock.yaml* ./

# Install dependencies in /app
RUN pnpm i

# Copy the rest of our folder into /app
COPY . .

# Ensure port 3000 is accessible to our system
EXPOSE 3000

# Run yarn dev, as we would via the command line 
CMD ["pnpm", "run", "host"]