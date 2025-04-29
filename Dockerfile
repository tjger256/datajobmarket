# 1. Base image with Python 3.13
FROM python:3.13-slim

# 2. Install required system packages for Chrome
RUN apt update && apt install -y \
  wget \
  curl \
  unzip \
  gnupg \
  libglib2.0-0 \
  libnss3 \
  libgconf-2-4 \
  libxss1 \
  libappindicator3-1 \
  libasound2 \
  libgtk-3-0 \
  fonts-liberation \
  xvfb \
  libu2f-udev \
  ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# 3. Install Google Chrome (with dependencies handled)
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt update && apt install -y ./google-chrome-stable_current_amd64.deb && \
    rm google-chrome-stable_current_amd64.deb

# 4. Set the working directory
WORKDIR /app

# 5. Copy all local files into the container
COPY . .

# 6. Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 7. Set the default command to run the main script
CMD ["python", "gemini.py"]