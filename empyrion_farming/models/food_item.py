from __future__ import annotations
from typing import Dict, ForwardRef, Optional, Text

from pydantic import BaseModel, root_validator
from pydantic.types import PositiveInt

import empyrion_farming.models as models

class FoodItem(BaseModel):

    name: Text

    average_market_value: PositiveInt

    ingredients: Dict[Text, PositiveInt]
    harvest_products: Optional[
        Dict[Text, ForwardRef("models.HarvestProduct")]
    ] = None

    @root_validator(allow_reuse=True)
    def initialize_dicts(cls, values: Dict) -> Dict:
        for key in [
                "harvest_products"
        ]:
            if values[key] is None:
                values[key] = dict()

        return values

