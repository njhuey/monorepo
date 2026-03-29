python_sources(name="lib")

pex_binary(
    name="accumulate",
    entry_point="accumulate.py",
    dependencies=[":lib", "third_party/python:typer", "third_party/python:sqlmodel"],
)
