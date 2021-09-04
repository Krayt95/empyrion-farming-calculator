from __future__ import annotations
from typing import Dict, ForwardRef, Literal, Optional, Text

from pydantic import BaseModel, root_validator, HttpUrl

import empyrion_farming.models as models

class EmpyrionScenario(BaseModel):

    name: Text
    version: Text
    scenario_type: Literal["Vanilla", "Mod"]
    link: Optional[HttpUrl] = None

    harvest_products: Optional[
        Dict[Text, ForwardRef("models.HarvestProduct")]
    ] = None
    plant_sprouts: Optional[
        Dict[Text, ForwardRef("models.PlantSprout")]
    ] = None
    food_items: Optional[
        Dict[Text, ForwardRef("models.FoodItem")]
    ] = None

    @root_validator(allow_reuse=True)
    def initialize_dicts(cls, values: Dict) -> Dict:
        for key in [
                "harvest_products",
                "plant_sprouts",
                "food_items"
        ]:
            if values[key] is None:
                values[key] = dict()

        return values

