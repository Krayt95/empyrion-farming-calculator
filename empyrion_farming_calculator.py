from pathlib import Path
from typing import Dict, Text, Tuple, Type

from pydantic import BaseModel
import srsly
import streamlit

from empyrion_farming.models import (
    EmpyrionScenario,
    HarvestProduct, FoodItem, PlantSprout
)


TITLE = "Empyrion Farming Calculator"
ICON = "🪴"
DESCRIPTION = """
An interactive web application for farming calculation
in _Empyrion - Galactic Survival_ or its _Reforged Eden_ mod
"""


streamlit.set_page_config(
    page_title=TITLE,
    page_icon=ICON,
    layout="centered",  # "wide"
    initial_sidebar_state="auto"
)

streamlit.title(
    f"{ICON} {TITLE}"
)


DATA_PATH = Path("./data")
SCENARIO_VERSION_GLOB_PATTERN = "*-*.*"
SCENARIO_CONFIG_NAME = "Scenario.yaml"
HARVEST_PRODUCTS_CONFIG_NAME = "Harvest-Products.yaml"
PLANT_SPROUTS_CONFIG_NAME = "Plant-Sprouts.yaml"
FOOD_ITEMS_CONFIG_NAME = "Food-Items.yaml"

MINUTES_PER_HOUR = 60


streamlit.info(
    DESCRIPTION
)

streamlit.header(
    "Scenario Selection"
)

(
    SCENARIO_SELECTION_COLUMN,
    SCENARIO_VERSION_SELECTION_COLUMN
) = streamlit.columns(2)

SCENARIO_OPTIONS = [
    (
        scenario_directory_path.name,
        scenario_directory_path
    )
    for scenario_directory_path in DATA_PATH.iterdir()
    if scenario_directory_path.is_dir() and len(
        list(
            scenario_directory_path.glob(
                f"{SCENARIO_VERSION_GLOB_PATTERN}/{SCENARIO_CONFIG_NAME}"
            )
        )
    )
]

def format_file_name_path_tuple_for_select(
        option: Tuple[Text, Path]
) -> Text:
    file_name, _path = option

    return file_name.replace("-", " ")

with SCENARIO_SELECTION_COLUMN:
    SELECTED_SCENARIO = streamlit.selectbox(
        "Select a Scenario",
        options=[
            *SCENARIO_OPTIONS,
            # TODO: ("Custom", None)
        ],
        format_func=format_file_name_path_tuple_for_select
    )

(
    SELECTED_SCENARIO_NAME,
    SELECTED_SCENARIO_PATH
) = SELECTED_SCENARIO

if not SELECTED_SCENARIO_PATH is None:
    SCENARIO_VERSION_OPTIONS = [
        (
            scenario_version_path.name,
            scenario_version_path
        )
        for scenario_version_path in SELECTED_SCENARIO_PATH.glob(
            f"{SCENARIO_VERSION_GLOB_PATTERN}"
        )
        if scenario_version_path.is_dir() and (
            scenario_version_path / SCENARIO_CONFIG_NAME
        ).exists()
    ]
else:
    SCENARIO_VERSION_OPTIONS = []

with SCENARIO_VERSION_SELECTION_COLUMN:
    SELECTED_SCENARIO_VERSION = streamlit.selectbox(
        "Select the Scenario Version",
        options=[
            *SCENARIO_VERSION_OPTIONS,
            # TODO: ("Custom", None)
        ],
        format_func=format_file_name_path_tuple_for_select
    )

(
    SELECTED_SCENARIO_VERSION_NAME,
    SELECTED_SCENARIO_VERSION_PATH
) = SELECTED_SCENARIO_VERSION

streamlit.header(
    f"_{format_file_name_path_tuple_for_select(SELECTED_SCENARIO_VERSION)}_ "
    "Farming Calculator"
)

def load_data_model(
        class_type: Type[BaseModel],
        yaml_path: Path
) -> Dict[Text, BaseModel]:
    return {
        name: class_type.parse_obj(
            {
                "name": name,
                **data
            }
        )
        for name, data in srsly.read_yaml(
            yaml_path
        ).items()
    }

with streamlit.spinner("Loading data"):
    SCENARIO_CONFIG: EmpyrionScenario = EmpyrionScenario.parse_obj(
        srsly.read_yaml(SELECTED_SCENARIO_VERSION_PATH / SCENARIO_CONFIG_NAME)
    )

    HARVEST_PRODUCTS: Dict[Text, HarvestProduct] = load_data_model(
        HarvestProduct,
        SELECTED_SCENARIO_VERSION_PATH / HARVEST_PRODUCTS_CONFIG_NAME
    )

    SCENARIO_CONFIG.harvest_products = HARVEST_PRODUCTS

    PLANT_SPROUTS: Dict[Text, PlantSprout] = load_data_model(
        PlantSprout,
        SELECTED_SCENARIO_VERSION_PATH / PLANT_SPROUTS_CONFIG_NAME
    )

    SCENARIO_CONFIG.plant_sprouts = PLANT_SPROUTS

    FOOD_ITEMS: Dict[Text, FoodItem] = load_data_model(
        FoodItem,
        SELECTED_SCENARIO_VERSION_PATH / FOOD_ITEMS_CONFIG_NAME
    )

    SCENARIO_CONFIG.food_items = FOOD_ITEMS

    for plant_sprout_name, plant_sprout in PLANT_SPROUTS.items():
        if plant_sprout.harvest_yield_per_hour is None:
            plant_sprout.harvest_yield_per_hour = (
                plant_sprout.harvest_yield / (
                    plant_sprout.growth_time / MINUTES_PER_HOUR
                )
            )

        if not plant_sprout.harvest_type in HARVEST_PRODUCTS:
            HARVEST_PRODUCTS[plant_sprout.harvest_type] = HarvestProduct(
                name=plant_sprout.harvest_type
            )

        HARVEST_PRODUCTS[
                plant_sprout.harvest_type
        ].plant_sprouts[
                plant_sprout_name
        ] = plant_sprout

        HARVEST_PRODUCTS[
                plant_sprout.harvest_type
        ].harvest_quantities[
                plant_sprout_name
        ] = plant_sprout.harvest_yield

        HARVEST_PRODUCTS[
                plant_sprout.harvest_type
        ].harvest_growth_times[
                plant_sprout_name
        ] = plant_sprout.growth_time

        HARVEST_PRODUCTS[
                plant_sprout.harvest_type
        ].harvest_quantities_per_hour[
                plant_sprout_name
        ] = plant_sprout.harvest_yield_per_hour

        if HARVEST_PRODUCTS[
                plant_sprout.harvest_type
        ].average_market_value:
            HARVEST_PRODUCTS[
                    plant_sprout.harvest_type
            ].average_market_values_per_hour[
                    plant_sprout_name
            ] = (
                plant_sprout.harvest_yield_per_hour * HARVEST_PRODUCTS[
                        plant_sprout.harvest_type
                ].average_market_value
            )

    # TODO: Food Items

    streamlit.write(
        SCENARIO_CONFIG.dict()
    )