import json
import os

# Adjust the import path to find the application
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.app.api.main import app


def generate_openapi_spec():
    """Generates and saves the OpenAPI specification in JSON format."""
    spec_path = os.path.join(os.path.dirname(__file__), "..", "docs")
    os.makedirs(spec_path, exist_ok=True)

    json_spec_path = os.path.join(spec_path, "openapi.json")

    openapi_content = app.openapi()

    with open(json_spec_path, "w") as f:
        json.dump(openapi_content, f, indent=2)
    print(f"✅ OpenAPI JSON specification saved to: {json_spec_path}")


if __name__ == "__main__":
    generate_openapi_spec()
