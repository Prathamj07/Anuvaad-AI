#!/bin/bash
cd frontend

# Install if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies (this may take a minute)..."
    npm install --prefer-offline --no-audit
    if [ $? -ne 0 ]; then
        echo "Installation failed, trying again..."
        npm install
    fi
fi

echo "Starting Vite dev server on port 5000..."
npm run dev -- --host 0.0.0.0 --port 5000
