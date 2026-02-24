from pathlib import Path


def test_required_directories_exist():
    required = [
        "src/app/front_end",
        "src/app/back_end/controllers",
        "src/app/back_end/services",
        "src/app/back_end/data/database_handler",
        "src/app/back_end/data/repositories",
        "src/app/back_end/utils",
        "rust_back_end/src",
    ]
    for rel in required:
        assert Path(rel).exists(), rel
