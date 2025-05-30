![Python](https://img.shields.io/badge/Python-3.7-ff69b4) ![Flask](https://img.shields.io/badge/Flask-2.2.5-ff9e00) ![Flask-SQLAlchemy](https://img.shields.io/badge/Flask--SQLAlchemy-3.1.1-00cc88) ![redis](https://img.shields.io/badge/redis-latest-cc0000)
# OM11MACOS

macOS Web UI for Open Manus Agent  

Gateway API for web interface that communicates with OM11TG and open-manus-agent microservices.

## Quick Start

```shell
git clone https://github.com/ErnestoAizenberg/OM11MACOS.git
cd OM11MACOS
pip install -r requirements.txt
python run.py
```

- Configure ports during setup (press Enter for defaults)
- Access the UI at: http://localhost:5000/

## Related Components

- **Telegram Integration**: [OM11TG](https://github.com/ErnestoAizenberg/OM11TG)
- **Core Agent**: [open-manus-agent](https://github.com/ErnestoAizenberg/open-manus-agent) (Browser + LLM management)
