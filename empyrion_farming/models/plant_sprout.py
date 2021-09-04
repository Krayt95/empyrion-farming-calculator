from __future__ import annotations
from typing import Dict, ForwardRef, Optional, Text, Union

from pydantic.main import BaseModel
from pydantic.types import PositiveFloat, PositiveInt

import empyrion_farming.models as models

class PlantSprout(BaseModel):

    name: Text

    harvest_type: Union[Text, ForwardRef("models.HarvestProduct")]
    growth_time: PositiveInt
    harvest_yield: PositiveInt
    harvest_yield_per_hour: Optional[PositiveFloat] = None
