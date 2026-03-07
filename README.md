# VartaBharathi

AI Assistant and Automation tool for downloading the Udayavani Manipal edition newspaper and emailing it to a list of recipients.

## Features

- **Automated Downloads**: Fetches the daily Udayavani Manipal edition PDF using Playwright.
- **Email Distribution**: Automatically emails the downloaded PDF to a configured list of recipients using Gmail SMTP.
- **CLI Interface**: Easy-to-use command-line interface with options to download specific dates and specify custom environment files.
- **GitHub Actions**: Includes a workflow for daily automated execution via a self-hosted runner.

## Prerequisites

- Python 3.12+
- A Gmail account with an App Password generated.
- [Playwright](https://playwright.dev/python/)

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. **Configuration**:
   Create a `.env` file in the root directory (or copy a template if you have one) and fill in your Gmail credentials and recipient list.
   ```env
   # .env
   GMAIL__USERNAME=your_email@gmail.com
   GMAIL__PASSWORD=your_app_password
   GMAIL__RECEIVERS=["recipient1@gmail.com", "recipient2@example.com"]
   ```

## Usage

Run the CLI tool using Python:

```bash
# Download today's edition and send emails
python cli.py

# Download a specific date's edition
python cli.py --date 2026-03-01

# Use a custom environment file
python cli.py --env .my_custom_env

# See help menu
python cli.py --help
```

## Automation

This project includes a GitHub Actions workflow (`.github/workflows/daily_newspaper.yml`) configured to run daily at 6:00 AM UTC. It is currently set up to use a `self-hosted` runner, which requires the `.env` file to be present on the runner machine.
