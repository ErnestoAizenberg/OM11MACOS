[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=FFD43B)](https://www.python.org/) [![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white&labelColor=101010&color=E34F26)](https://developer.mozilla.org/en-US/docs/Web/HTML) [![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript) [![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white&labelColor=101010)](https://developer.mozilla.org/en-US/docs/Web/CSS) ![Flask](https://img.shields.io/badge/Flask-2.2.5-ff9e00) ![Flask-SQLAlchemy](https://img.shields.io/badge/Flask--SQLAlchemy-3.1.1-00cc88) ![redis](https://img.shields.io/badge/redis-latest-cc0000)
# OM11MACOS

macOS Web UI for Open Manus Agent  

Gateway API for web interface that communicates with OM11TG and open-manus-agent microservices.

## Quick Start

```shell
git clone https://github.com/ErnestoAizenberg/OM11MACOS.git
cd OM11MACOS
cp .env.example .env
pip install -r requirements.txt
python run.py
```

- Configure ports during setup (press Enter for defaults)
- Access the UI at: http://localhost:5000/

## Related Components

- **Telegram Integration**: [OM11TG](https://github.com/ErnestoAizenberg/OM11TG)
- **Core Agent**: [open-manus-agent](https://github.com/ErnestoAizenberg/open-manus-agent) (Browser + LLM management)
