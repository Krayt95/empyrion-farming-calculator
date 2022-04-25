from typing import Dict, Text
from .base_model import BaseModel


class BaseItem(BaseModel):
    name: Text

    def update_references(self, values: Dict):
        pass
