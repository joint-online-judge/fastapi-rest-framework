from typing import Any, Dict, Generic, Iterable, List, Optional, Type, TypeVar, Union

from pydantic import BaseModel, BaseSettings, root_validator

T = TypeVar("T", bound=BaseSettings)

_global_settings_models_dict: Dict[str, Type[BaseModel]] = {}
_global_settings_models_names: List[str] = []


def add(name: Optional[Union[str, Type[BaseModel]]] = None) -> Any:
    def decorator(cls: Type[BaseModel]) -> Type[BaseModel]:
        if isinstance(name, str) and name:
            model_name = name
        else:
            model_name = cls.__name__
        if model_name in _global_settings_models_dict:
            raise KeyError(f"Error: settings {model_name} already added!")
        # else:
        #     print(model_name)
        _global_settings_models_dict[model_name] = cls
        _global_settings_models_names.append(model_name)
        return cls

    if name is None or isinstance(name, str):
        return decorator
    else:
        return decorator(name)


def parse_settings_models(
    settings_models: Union[None, str, Iterable[str]]
) -> List[Type[BaseModel]]:
    _settings_models = []
    if settings_models is None:
        _settings_models = _global_settings_models_names
    elif isinstance(settings_models, str):
        _settings_models = [settings_models]
    elif isinstance(settings_models, Iterable):
        _settings_models = list(settings_models)
    result = []
    for model_name in _settings_models:
        if model_name not in _global_settings_models_dict:
            raise KeyError(f"Error: settings {model_name} not added!")
        result.append(_global_settings_models_dict[model_name])
    return result


class EnvFileMixin:
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class CLIMixin:
    @root_validator(allow_reuse=True)
    def _inject_cli(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        from fastapi_rest_framework.cli import cli_settings

        for key, value in cli_settings.items():
            if key in values and value is not None:
                values[key] = value
        return values


def generate_config_class(
    settings_models: Union[None, str, Iterable[str]] = None,
    name: Optional[str] = None,
    mixins: Optional[List[type]] = None,
) -> Any:
    if not name:
        name = "FastAPIConfig"
    if mixins is None:
        mixins = []
    base_classes = parse_settings_models(settings_models)
    new_class = type(
        name,
        (
            *mixins,
            *base_classes,
            BaseSettings,
        ),
        {},
    )
    return new_class


class SettingsProxy(Generic[T]):
    def __init__(self) -> None:
        self._settings: Optional[T] = None

    def __getattr__(self, attr: str) -> Any:
        if attr in self.__dict__:
            return self.__dict__[attr]
        if self._settings is None:
            raise ValueError("settings not initialized")
        return getattr(self._settings, attr)


def init_settings(settings_cls: Type[T]) -> Union[T, SettingsProxy[T]]:
    _settings = settings_cls()
    setattr(settings, "_settings", _settings)
    return _settings


settings: Union[BaseSettings, SettingsProxy[Any]] = SettingsProxy()
