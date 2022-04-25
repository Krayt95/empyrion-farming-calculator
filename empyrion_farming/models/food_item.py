from __future__ import annotations
from typing import Dict, ForwardRef, Optional, Text

from pydantic import root_validator, Field
from pydantic.types import PositiveInt

from .base_item import BaseItem


class FoodItem(BaseItem):

    name: Text

    average_market_value: PositiveInt

    ingredients: Dict[Text, PositiveInt]
    harvest_products: Dict[Text, BaseItem] = Field(
        default_factory=dict,
        exclude=True
    )

    def update_references(self, values: Dict):
        self.harvest_products = {
            ingredient: values["harvest_products"][ingredient]
            for ingredient in self.ingredients
            if ingredient in values["harvest_products"]
        }


FoodItem.update_forward_refs()
