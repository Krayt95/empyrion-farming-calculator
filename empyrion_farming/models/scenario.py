from pathlib import Path
from typing import Dict, Literal, Optional, Text, Union
from typing_extensions import Self

from pydantic import Field
from pydantic.class_validators import root_validator, validator
from pydantic.networks import HttpUrl
from pydantic.types import FilePath
import srsly

from .base_model import BaseModel
from .harvest_product import HarvestProduct
from .plant_sprout import PlantSprout
from .food_item import FoodItem


class EmpyrionScenario(BaseModel):

    name: Text
    version: Text
    scenario_type: Literal["Vanilla", "Mod"]
    link: Optional[HttpUrl] = None

    source_file: Optional[FilePath]

    harvest_products: Optional[
        Dict[Text, "HarvestProduct"]
    ] = Field(default_factory=dict)
    plant_sprouts: Optional[
        Dict[Text, "PlantSprout"]
    ] = Field(default_factory=dict)
    food_items: Optional[
        Dict[Text, "FoodItem"]
    ] = Field(default_factory=dict)

    @validator(
        "harvest_products", "plant_sprouts", "food_items",
        pre=True, allow_reuse=True
    )
    def load_from_file(
            cls,
            value: Union[Text, Dict],
            values: Dict
    ) -> Dict:
        if isinstance(value, Text):
            source_path: Path = Path(
                values["source_file"]
            ).parent / value

            value = {
                name: attributes | dict(name=name)
                for name, attributes in srsly.read_yaml(
                    source_path
                ).items()
            }

        return value

    @root_validator(allow_reuse=True)
    def update_references(
            cls,
            values: Dict
    ) -> Dict:
        for field in (
            "harvest_products",
            "plant_sprouts",
            "harvest_products",
            "food_items"
        ):
            for key, field_value in values.get(field, {}).items():
                field_value.update_references(
                    values=values
                )

        return values


    @classmethod
    def from_source_file(cls, source_path: Path) -> Self:
        return cls.parse_obj(
            dict(
                srsly.read_yaml(source_path)
            ) | dict(
                source_file=source_path
            )
        )
