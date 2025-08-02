# Environment Setup

## API Keys Configuration

This project uses environment variables to securely store API keys and credentials. Follow these steps to set up your environment:

### 1. Copy the environment template
```bash
cp .env.example .env
```

### 2. Fill in your actual API keys in the `.env` file

- **OpenAI API Key**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)
- **Google Cloud Service Account**: Create from [Google Cloud Console](https://console.cloud.google.com/)
- **Other APIs**: Add as needed for LinkedIn, Naukri, etc.

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Test the configuration
```python
from config.api_keys import APIKeys

# This will raise an error if required keys are missing
APIKeys.validate_keys()
```

## Security Notes

- The `.env` file is ignored by Git and should never be committed
- Use `.env.example` as a template for other developers
- Keep your API keys secure and rotate them regularly
- Consider using more advanced secret management for production deployments
