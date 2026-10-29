"""Settings loaded from environment variables (or a local .env file)."""

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Every field maps to an env var with the WAZUH_ prefix: api_url -> WAZUH_API_URL
    model_config = SettingsConfigDict(env_prefix="WAZUH_", env_file=".env", extra="ignore")

    api_url: str = "https://localhost:55000"
    api_user: str
    # SecretStr hides the value in logs and reprs: str(settings) won't leak it
    api_password: SecretStr
    # Lab only: the manager API ships with a self-signed cert issued for "wazuh.com"
    verify_ssl: bool = True
