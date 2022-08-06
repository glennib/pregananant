from pathlib import Path
from typing import Dict, Any
import json

def load(path: Path) -> Dict[str, Any]:
    if not path.exists():
        print(f"json file at {path} didn't exist, creating new with empty dict")
        with path.open("w+") as f:
            json.dump({"annotations": []}, f)
    with path.open("r") as f:
        try:
            print(f"json file at {path} exists, loading")
            meta = json.load(f)
            print(f"Loaded {len(meta['annotations'])} annotations")
        except json.JSONDecodeError:
            meta = {}
            print(f"Couldn't decode {path} as json, overwriting and loading empty dict")
    return meta


def dump(meta: Dict[str, Any], path: Path):
    with path.open("w") as f:
        json.dump(meta, f, indent=4, sort_keys=True)
    print(f"Dumped {len(meta['annotations'])} annotations")
