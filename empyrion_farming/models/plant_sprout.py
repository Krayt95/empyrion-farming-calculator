from typing import Dict, Optional, Text, Union

from pydantic.class_validators import validator
from pydantic.types import PositiveFloat, PositiveInt

from .base_item import BaseItem
from .harvest_product import HarvestProduct

class PlantSprout(BaseItem):

    name: Text

    harvest_type: Union[Text, HarvestProduct]
    growth_time: PositiveInt
    harvest_yield: PositiveInt
    harvest_yield_per_hour: PositiveFloat = None

    @validator(
        "harvest_yield_per_hour",
        pre=True, always=True,
        allow_reuse=True
    )
    def calculate_harvest_yield_per_hour(
            cls,
            harvest_yield_per_hour: Optional[PositiveFloat],
            values: Dict
    ) -> PositiveFloat:
        if not harvest_yield_per_hour:
            harvest_yield_per_hour = (
                values["harvest_yield"] / values["growth_time"]
            ) * 60

        return harvest_yield_per_hour

    def update_references(self, values: Dict):
        self.harvest_type = values["harvest_products"].get(
            self.harvest_type, self.harvest_type
        )

        if isinstance(self.harvest_type, Text):
            self.harvest_type = HarvestProduct(
                name=self.harvest_type
            )
            values["harvest_products"][self.harvest_type.name] = (
                self.harvest_type
            )
            self.harvest_type.plant_sprouts[self.name] = self



PlantSprout.update_forward_refs()
