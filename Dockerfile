FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .

# Create download directory
RUN mkdir -p /tmp/terabox

# Run bot
CMD ["python", "bot.py"]
