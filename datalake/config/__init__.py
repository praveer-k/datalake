from datalake.config.settings import Settings

# Initialize settings
# -----------------------------------------------------------------------
settings = Settings(_env_file=['.env', '../../.env'], _env_file_encoding='utf-8')
# -----------------------------------------------------------------------
# -----------------------------------------------------------------------
logger = settings.logger
logger.setLevel(settings.LOG_LEVEL.alias)
logger.info("Initialized Settings ...")
# Visible only when log level is set to DEBUG manually in logger.py file
logger.debug(settings.__dict__)
