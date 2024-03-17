from os import path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    #### Application Settings
    """

    model_config = SettingsConfigDict(
        env_file=".env.dev",
        env_file_encoding="utf-8",
        validate_default=False,
        extra="ignore",
    )

    ROOT_DIR: str = path.realpath(path.dirname(__file__))
    API_KEY: str = ""
    CORS_ORIGINS: str = ""
    DETECT_CONFIDENCE: Optional[float] = 0.5
    RETENTION_PERIOD: Optional[int] = 5
    IMAGE: str = "RESULT_IMAGE"
    CLS_LIST: str = "CLASS_LIST"
    DATABASE_NAME: str = "API_DB"
    DATABASE_TYPE: str = "sqlite3"
    QUERY_FILE_NAME: str = "API_QUERY"
    CONF_LIST: str = "CONFIDENCE_LIST"
    DETECT_LIST: str = "DETECT_XY_LIST"
    PREDICTIONS_ACCESS_PATH: str = "/static/PREDICTIONS"
    DATABASE_PATH: str = f"{ROOT_DIR}/DATABASE/DB/{DATABASE_NAME}.db"
    MODEL_PATH: str = f"{ROOT_DIR}/DETECTION/model/best.pt"
    QUERY_FILE_PATH: str = f"{ROOT_DIR}/DATABASE/QUERIES/{QUERY_FILE_NAME}.sql"
    PREDICTIONS_SAVE_PATH: str = f"{ROOT_DIR}{PREDICTIONS_ACCESS_PATH}/"
