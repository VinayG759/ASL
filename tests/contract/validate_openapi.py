import sys
from pathlib import Path

from openapi_spec_validator import validate
from openapi_spec_validator.readers import read_from_filename

ROOT = Path(__file__).resolve().parents[2]
OPENAPI_PATH = ROOT / "packages" / "asl-schemas" / "openapi" / "asl-v1.yaml"


def main() -> None:
    if not OPENAPI_PATH.exists():
        print(f"OpenAPI spec not found: {OPENAPI_PATH}", file=sys.stderr)
        sys.exit(1)
    spec = read_from_filename(str(OPENAPI_PATH))[0]
    validate(spec)
    assert spec["openapi"].startswith("3.")
    assert any("govern/tool-use" in p for p in spec["paths"])
    print(f"OpenAPI valid: {OPENAPI_PATH}")


if __name__ == "__main__":
    main()
