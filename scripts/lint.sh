#!/bin/bash

echo "🔍 Running linting checks..."

# Python linting
echo "🐍 Python linting..."
ruff check .
ruff format --check .
mypy .

# JavaScript/TypeScript linting (if frontend exists)
if [ -d "frontend" ]; then
  echo "📦 JavaScript/TypeScript linting..."
  cd frontend
  npx biome check --error-on-warnings
  npx eslint . --config eslint.config.mjs --max-warnings 0
  cd ..
fi

# CSS linting (if frontend exists)
if [ -d "frontend" ]; then
  echo "🎨 CSS linting..."
  cd frontend
  npx stylelint "**/*.{css,svelte}" --fix
  cd ..
fi

# Prettier (if frontend exists)
if [ -d "frontend" ]; then
  echo "💅 Prettier formatting..."
  cd frontend
  npx prettier --check --list-different .
  cd ..
fi

# Markdown formatting
echo "📝 Markdown formatting..."
pip install mdformat mdformat-gfm --quiet
mdformat --check --wrap 80 .

echo "✅ All checks passed!"
