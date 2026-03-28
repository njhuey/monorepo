python_sources(name="lib")

pex_binary(
    name="connections",
    entry_point="connections.__main__",
    dependencies=[":lib", "third_party/python:typer"],
)
