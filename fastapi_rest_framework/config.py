from typing import Any, Generic, Optional, Type, TypeVar, Union

from pydantic import BaseSettings

T = TypeVar("T", bound=BaseSettings)


class SettingsProxy(Generic[T]):
    def __init__(self) -> None:
        self._settings: Optional[T] = None

    def __getattr__(self, attr: str) -> Any:
        if attr in self.__dict__:
            return self.__dict__[attr]
        if self._settings is None:
            raise ValueError("settings not initialized")
        return getattr(self._settings, attr)


def init_settings(settings_cls: Type[T]) -> Any:
    _settings = settings_cls()
    setattr(settings, "_settings", _settings)
    return _settings


settings: Union[BaseSettings, SettingsProxy[Any]] = SettingsProxy()
