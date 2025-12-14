```md
[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=FFD43B)](https://www.python.org/)
[![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/HTML)
[![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)](https://developer.mozilla.org/en-US/docs/Web/CSS)
![Flask](https://img.shields.io/badge/Flask-2.3.3-000000?style=for-the-badge&logo=flask)
![Flask-SQLAlchemy](https://img.shields.io/badge/Flask_SQLAlchemy-3.0.5-00cc88?style=for-the-badge)

# OM11MACOS

**Web UI for Open Manus Agent**

A gateway API for web interfaces that facilitates communication between OM11TG and open-manus-agent microservices.

## Quick Start

Follow these steps to set up the project:

```shell
# Clone the repository
git clone https://github.com/ErnestoAizenberg/OM11MACOS.git

# Navigate to the project directory
cd OM11MACOS

# Create a virtual environment (recommended)
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Set up environment configuration
cp .env.example .env

# Install dependencies
pip install -r requirements.txt

# Run the application
python run.py
```

Note: You will be prompted to configure ports during the initial setup. Press Enter to accept the default values.

After successful setup, access the web interface at:
http://localhost:5000/ (default port)

Related Components

This project integrates with the following components:

· Telegram Integration: OM11TG
    Telegram bot interface for the Open Manus Agent system.
· Core Agent: open-manus-agent
    Core microservice responsible for browser automation and LLM management.

Architecture

OM11MACOS serves as a middleware component that:

· Provides a web-based user interface for macOS users
· Acts as an API gateway between different system components
· Manages communication with Telegram and core agent services
· Handles session management and user authentication

Features

· Modern web interface
· Real-time communication with agent services
· Configuration management through environment variables
· Support for multiple backend services
· Session persistence and state management