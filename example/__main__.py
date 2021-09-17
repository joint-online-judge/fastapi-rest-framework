import uvicorn

from example.config import FastAPIConfig
from fastapi_rest_framework import cli, config


@cli.command()
def main() -> None:
    settings = config.init_settings(FastAPIConfig)
    uvicorn.run(
        "example.app:app",
        host=settings.host,
        port=settings.port,
        debug=settings.debug,
        reload=settings.debug,
        reload_dirs=["example", "fastapi_rest_framework"],
    )


if __name__ == "__main__":
    main()
