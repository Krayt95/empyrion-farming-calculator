from __future__ import annotations
from typing import Dict, ForwardRef, Optional, Text

from pydantic import BaseModel, root_validator
from pydantic.types import PositiveFloat, PositiveInt

import empyrion_farming.models as models

class HarvestProduct(BaseModel):

    name: Text

    average_market_value: Optional[PositiveInt] = None
    harvest_quantities: Optional[Dict[Text, PositiveInt]] = None
    harvest_growth_times: Optional[Dict[Text, PositiveInt]] = None
    harvest_quantities_per_hour: Optional[Dict[Text, PositiveFloat]] = None
    average_market_values_per_hour: Optional[Dict[Text, PositiveFloat]] = None

    plant_sprouts: Optional[Dict[Text, ForwardRef("models.PlantSprout")]] = None
    food_items: Optional[Dict[Text, ForwardRef("models.FoodItem")]] = None

    @root_validator(allow_reuse=True)
    def initialize_dicts(cls, values: Dict) -> Dict:
        for key in [
                "harvest_quantities",
                "harvest_growth_times",
                "harvest_quantities_per_hour",
                "average_market_values_per_hour",
                "plant_sprouts",
                "food_items"
        ]:
            if values[key] is None:
                values[key] = dict()

        return values
