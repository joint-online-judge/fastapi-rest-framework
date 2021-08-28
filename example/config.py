from pydantic import BaseModel

from fastapi_rest_framework import config


@config.add
class BaseConfig(BaseModel):
    debug: bool = False
    host: str = "localhost"
    port: int = 9000


FastAPIConfig = config.generate_config_class(
    mixins=[config.EnvFileMixin, config.CLIMixin]
)
