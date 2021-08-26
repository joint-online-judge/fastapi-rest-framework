import uvicorn


def main() -> None:
    uvicorn.run(
        "example.app:app",
        port=9000,
        debug=True,
        # host=settings.host,
        # port=settings.port,
        # reload=settings.debug,
        reload_dirs=["example", "fastapi_rest_framework"],
    )


if __name__ == "__main__":
    main()
