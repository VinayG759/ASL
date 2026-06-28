import json
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator
from openapi_spec_validator import validate
from openapi_spec_validator.readers import read_from_filename

ROOT = Path(__file__).resolve().parents[2]
SCHEMAS_DIR = ROOT / "packages" / "asl-schemas" / "jsonschema"
OPENAPI_PATH = ROOT / "packages" / "asl-schemas" / "openapi" / "asl-v1.yaml"
POLICY_EXAMPLE = ROOT / "policies" / "examples" / "default-policy.yaml"


def test_openapi_spec_is_valid() -> None:
    spec, _ = read_from_filename(str(OPENAPI_PATH))
    validate(spec)


def test_govern_request_example_validates() -> None:
    schema = json.loads((SCHEMAS_DIR / "govern-request.json").read_text())
    example = schema["examples"][0]
    Draft202012Validator(schema).validate(example)


def test_govern_response_examples_validate() -> None:
    schema = json.loads((SCHEMAS_DIR / "govern-response.json").read_text())
    validator = Draft202012Validator(schema)
    for example in schema["examples"]:
        validator.validate(example)


def test_default_policy_validates() -> None:
    schema = json.loads((SCHEMAS_DIR / "policy-v1.json").read_text())
    policy = yaml.safe_load(POLICY_EXAMPLE.read_text())
    Draft202012Validator(schema).validate(policy)
    assert policy["default_unclassified"] == "ESCALATE"
