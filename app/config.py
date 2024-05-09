import os

# Basic application configuration
# Basic application configuration class
class Config:
    DEBUG = os.getenv('DEBUG', 'False') == 'True'
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 8000))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'info').upper()

    # OpenAI API configurations
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_API_VERSION = "2020-11-07"
    OPENAI_API_TYPE = "open_ai"
    OPENAI_ORGANIZATION = "org-2NSCKElNkP4xGwyheiFVhjsX"
    OPENAI_API_BASE = "https://api.openai.com/v1"

    # Token and image file size configurations
    MAX_ALLOWED_TOKENS = 128000
    REQUESTED_OUTPUT_TOKENS = 4096
    IMAGE_SIZE_LIMIT = 20 * 1024 * 1024  # 20 MB in bytes

    # File handling configurations
    MAX_FILE_SIZE = 4.5 * 1024 * 1024  # 4.5 MB in bytes
    TEMP_FILE_DIR = "/tmp"




# Optionally, you can define different configurations for different environments
class DevelopmentConfig(Config):
    DEBUG = True
    LOG_LEVEL = 'debug'

class ProductionConfig(Config):
    DEBUG = False
    LOG_LEVEL = 'warning'

# Choose the appropriate configuration based on an environment variable
def get_config():
    env = os.getenv('ENV', 'development').lower()
    if env == 'production':
        return ProductionConfig
    else:
        return DevelopmentConfig
