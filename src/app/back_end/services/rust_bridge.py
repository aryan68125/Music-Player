import importlib
from types import ModuleType


def _load_rust_backend_module() -> ModuleType:
    try:
        return importlib.import_module("rust_back_end_native")
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Rust backend module 'rust_back_end_native' is not installed. "
            "Build it with 'venv/bin/python -m maturin develop --manifest-path rust_back_end/Cargo.toml'."
        ) from exc


def get_rust_backend_version() -> str:
    module = _load_rust_backend_module()

    if not hasattr(module, "backend_version"):
        raise RuntimeError("Rust backend module is missing required function 'backend_version'.")

    version = module.backend_version()
    if not isinstance(version, str):
        raise TypeError("Rust backend function 'backend_version' must return a string.")
    if not version.strip():
        raise ValueError("Rust backend version must be a non-empty string.")

    return version
