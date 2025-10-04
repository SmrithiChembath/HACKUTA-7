import os
import json
import yaml
from typing import Dict, Any, List

PACKS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../packs"))

class FormPack:
    def __init__(self, slug: str, data: Dict[str, Any]):
        self.slug = slug
        self.data = data

    @property
    def title(self) -> str:
        return self.data.get("title", self.slug)

    @property
    def welcome(self) -> str:
        return self.data.get("welcome", "Welcome!")

    @property
    def notes(self) -> List[Dict[str, Any]]:
        return self.data.get("notes", [])

    @property
    def flow_order(self) -> List[str]:
        return self.data.get("flow", {}).get("order", [])

    @property
    def fields(self) -> Dict[str, Any]:
        return self.data.get("fields", {})

    @property
    def doc_requirements(self) -> List[Dict[str, Any]]:
        return self.data.get("doc_requirements", [])

    @property
    def completion(self) -> Dict[str, Any]:
        return self.data.get("completion", {})

    def mapping(self) -> Dict[str, str]:
        path = os.path.join(PACKS_DIR, self.slug, "mapping.json")
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return {}


def list_packs() -> List[Dict[str, Any]]:
    items = []
    for name in os.listdir(PACKS_DIR):
        dirpath = os.path.join(PACKS_DIR, name)
        if os.path.isdir(dirpath):
            yml = os.path.join(dirpath, "pack.yaml")
            if os.path.exists(yml):
                with open(yml, "r") as f:
                    data = yaml.safe_load(f)
                items.append({"slug": data.get("slug", name), "title": data.get("title", name)})
    return items


def load_pack(slug: str) -> FormPack:
    yml = os.path.join(PACKS_DIR, slug, "pack.yaml")
    if not os.path.exists(yml):
        raise FileNotFoundError(f"Pack not found: {slug}")
    with open(yml, "r") as f:
        data = yaml.safe_load(f)
    return FormPack(slug=slug, data=data)
