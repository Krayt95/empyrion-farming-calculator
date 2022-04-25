from __future__ import annotations
from typing import Dict, ForwardRef, Optional, Text

from pydantic import Field
from pydantic.class_validators import validator
from pydantic.types import PositiveFloat, PositiveInt

from .base_item import BaseItem


class HarvestProduct(BaseItem):

    name: Text

    average_market_value: Optional[PositiveInt] = None

    harvest_quantities: Dict[Text, PositiveInt] = Field(
        default_factory=dict
    )
    harvest_growth_times: Dict[Text, PositiveInt] = Field(
        default_factory=dict
    )
    harvest_quantities_per_hour: Dict[Text, PositiveFloat] = Field(
        default_factory=dict
    )
    average_market_values_per_hour: Dict[Text, PositiveFloat] = Field(
        default_factory=dict
    )

    plant_sprouts: Dict[Text, BaseItem] = Field(
        default_factory=dict,
        exclude=True
    )
    food_items: Dict[Text, BaseItem] = Field(
        default_factory=dict,
        exclude=True
    )

    def update_references(self, values: Dict):
        self.plant_sprouts = {
            plant_sprout_name: plant_sprout
            for (
                plant_sprout_name,
                plant_sprout
            ) in values["plant_sprouts"].items()
            if (
                isinstance(plant_sprout.harvest_type, Text)
                and plant_sprout.harvest_type == self.name
            ) or (
                hasattr(plant_sprout.harvest_type, "name")
                and plant_sprout.harvest_type.name == self.name
            )
        }

        for plant_sprout_name, plant_sprout in self.plant_sprouts.items():
            self.harvest_quantities[plant_sprout_name] = (
                plant_sprout.harvest_yield
            )
            self.harvest_growth_times[plant_sprout_name] = (
                plant_sprout.growth_time
            )
            self.harvest_quantities_per_hour[plant_sprout_name] = (
                plant_sprout.harvest_yield_per_hour
            )

            if plant_sprout.harvest_yield_per_hour and self.average_market_value:
                self.average_market_values_per_hour[plant_sprout_name] = (
                    plant_sprout.harvest_yield_per_hour * self.average_market_value
                )

        self.food_items = {
            food_item.name: food_item
            for food_item in values["food_items"]
            if self.name in food_item.ingredients
        }


HarvestProduct.update_forward_refs()
