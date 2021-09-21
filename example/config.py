from typing import Type, Union

from fastapi_rest_framework import config


@config.add
class BaseConfig(config.Base):
    debug: bool = False
    host: str = "localhost"
    port: int = 9000


FastAPIConfig: Type[Union[BaseConfig]] = config.generate_config_class(
    mixins=[config.EnvFileMixin, config.CLIMixin]
)
