import asyncio
from functools import lru_cache, wraps
from typing import Any, Callable, Iterable, List, Optional, Tuple, Type, Union

import click
from click_option_group import optgroup
from pydantic import BaseModel

from fastapi_rest_framework.config import parse_settings_models


def parse_settings_group(cls: Type[BaseModel]) -> Tuple[str, str]:
    docstring = cls.__doc__ or ""
    help_index = docstring.find("\n\n")
    if help_index < 0:
        if docstring:
            name = docstring
        else:
            name = cls.__name__
        help_str = ""
    else:
        name = docstring[:help_index]
        help_str = docstring[help_index + 2 :]
    return name, help_str


def get_option_name(name: str, _type: type) -> str:
    name = name.replace("_", "-")
    if _type == bool:
        return f"--{name}/--no-{name}"
    return f"--{name}"


def get_option_help(description: Optional[str], default: Any) -> str:
    result = (description or "") + "\n"
    if default is not None:
        result += f"[default: {str(default)}]"
    return result


@lru_cache()
def get_settings_class_options(settings_class: Type[BaseModel]) -> List[Any]:
    options = []
    name, help_str = parse_settings_group(settings_class)
    options.append(optgroup.group(name=name, help=help_str))
    option_base = optgroup

    for key, value in settings_class.__fields__.items():
        opt_name = get_option_name(key, value.type_)
        help_str = get_option_help(value.field_info.description, value.default)
        options.append(
            option_base.option(
                opt_name,
                type=value.type_,
                help=help_str,
                default=None,
            )
        )
    return options


def get_global_options(settings_models: List[Type[BaseModel]]) -> List[Any]:
    global_options = [click.argument("args", nargs=-1)]
    for settings_class in settings_models:
        global_options.extend(get_settings_class_options(settings_class))
    return global_options


def add_options(options: List[Any]) -> Callable[..., Callable[..., Any]]:
    def _add_options(func: Any) -> Callable[..., Any]:
        for option in reversed(options):
            func = option(func)
        return func

    return _add_options


def command_start(
    settings_models: Union[None, str, Iterable[str]] = None,
    name: str = None,
    group: Optional[click.Group] = None,
) -> Any:
    parsed_settings_models = parse_settings_models(settings_models)
    context_settings = dict(
        help_option_names=["-h", "--help"],
        max_content_width=88,
    )
    if group is None:
        command_decorator = click.command
    else:
        command_decorator = group.command

    def decorator(func: Any) -> Any:
        @command_decorator(name=name, context_settings=context_settings)
        @add_options(get_global_options(parsed_settings_models))
        @wraps(func)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs, __settings_models=parsed_settings_models)

        return wrapped

    return decorator


cli_settings = {}


def command_end() -> Any:
    def decorator(func: Any) -> Any:
        @wraps(func)
        def wrapped(args: Any, **kwargs: Any) -> Any:
            if "__settings_models" not in kwargs:
                raise SystemError(
                    "Please use cli_command_start before cli_command_end!"
                )
            settings_models = kwargs.pop("__settings_models")
            fields = set()
            for settings_class in settings_models:
                fields.update(settings_class.__fields__.keys())

            new_kwargs = {}
            cli_settings["__not_empty"] = True
            for key, value in kwargs.items():
                if key in fields:
                    if value is not None:
                        cli_settings[key] = value
                else:
                    new_kwargs[key] = value
            return func(*args, **new_kwargs)

        return wrapped

    return decorator


def command(
    settings_models: Union[None, str, Iterable[str]] = None,
    name: str = None,
    group: Optional[click.Group] = None,
) -> Any:
    def decorator(func: Any) -> Any:
        @command_start(settings_models=settings_models, name=name, group=group)
        @command_end()
        @wraps(func)
        def wrapped(*args: Any, **kwargs: Any) -> Any:
            return func(*args, **kwargs)

        return wrapped

    return decorator


def async_command(f: Any) -> Any:
    @wraps(f)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return asyncio.run(f(*args, **kwargs))

    return wrapper
