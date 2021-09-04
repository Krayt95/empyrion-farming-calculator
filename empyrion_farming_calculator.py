import math
from pathlib import Path
from typing import Dict, List, Text, Tuple, Type

from pydantic import BaseModel
from pydantic.types import NonNegativeInt, PositiveInt
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
COLUMN_BATCH_SIZE = 3


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

SCENARIO_OPTIONS: List[Tuple[Text, Path]] = sorted(
    [
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
    ],
    key=lambda option: option[0]
)

def format_file_name_path_tuple_for_select(
        option: Tuple[Text, Path]
) -> Text:
    file_name, _path = option

    return file_name.replace("-", " ")

with SCENARIO_SELECTION_COLUMN:
    SELECTED_SCENARIO = streamlit.selectbox(
        "Select a Scenario",
        options=[
            *SCENARIO_OPTIONS
        ],
        format_func=format_file_name_path_tuple_for_select
    )

(
    SELECTED_SCENARIO_NAME,
    SELECTED_SCENARIO_PATH
) = SELECTED_SCENARIO

if not SELECTED_SCENARIO_PATH is None:
    SCENARIO_VERSION_OPTIONS: List[Tuple[Text, Path]] = sorted(
        [
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
        ],
        key=lambda option: option[0]
    )
else:
    SCENARIO_VERSION_OPTIONS = []

with SCENARIO_VERSION_SELECTION_COLUMN:
    SELECTED_SCENARIO_VERSION = streamlit.selectbox(
        "Select the Scenario Version",
        options=[
            *SCENARIO_VERSION_OPTIONS
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

HARVEST_INTERVAL: PositiveInt = streamlit.slider(
    "Harvest Interval (in Minutes)",
    min_value=10,
    max_value=180,
    step=10,
    value=60,
    help=(
        "**Harvest Interval** (in minutes)\n\n"
        "How often you intend to check on the plants for harvesting.\n\n"
        "Will filter out plants with a longer growth time, unless there "
        "are no alternatives for the harvest product.\n\n"
        "Used in calculating actual harvest product output."
    )
)

streamlit.subheader("Produce Food Items per Harvest")

FOOD_ITEM_PRODUCTION_COUNTS: Dict[Text, NonNegativeInt] = dict()

for batch_index in range(0, len(FOOD_ITEMS), COLUMN_BATCH_SIZE):
    food_item_batch = list(
        FOOD_ITEMS.items()
    )[batch_index:(batch_index + COLUMN_BATCH_SIZE)]

    food_item_batch_columns = streamlit.columns(COLUMN_BATCH_SIZE)

    for column_index, (
            food_item_name, food_item
    ) in enumerate(food_item_batch):

        with food_item_batch_columns[column_index]:
            FOOD_ITEM_PRODUCTION_COUNTS[
                    food_item_name
            ] = streamlit.number_input(
                food_item_name,
                min_value=0,
                step=1,
                key=f"Food Item {food_item_name} Count",
                help=(
                    "\n".join(
                        [
                            f"**{food_item.name}**\n",
                            f"Ingredients: \n",
                            *[
                                (
                                    f"* `{food_item_ingredient_count}` x "
                                    f"{food_item_ingredient}"
                                )
                                for (
                                    food_item_ingredient,
                                    food_item_ingredient_count
                                ) in food_item.ingredients.items()
                            ]
                        ]
                    )
                )
            )

HARVEST_PRODUCT_PRODUCTION_COUNTS: Dict[Text, NonNegativeInt] = {
    harvest_product_name: 0
    for harvest_product_name in HARVEST_PRODUCTS
}

for (
        food_item_name,
        food_item_count
) in FOOD_ITEM_PRODUCTION_COUNTS.items():
    for (
            harvest_product_name,
            harvest_product_count
    ) in FOOD_ITEMS[food_item_name].ingredients.items():
        if harvest_product_name in HARVEST_PRODUCTS:
            HARVEST_PRODUCT_PRODUCTION_COUNTS[harvest_product_name] += (
                food_item_count * harvest_product_count
            )

streamlit.subheader("Produce Harvest Products per Harvest")

for batch_index in range(0, len(HARVEST_PRODUCTS), COLUMN_BATCH_SIZE):
    harvest_product_batch = list(
        HARVEST_PRODUCTS.items()
    )[batch_index:(batch_index + COLUMN_BATCH_SIZE)]

    harvest_product_batch_columns = streamlit.columns(COLUMN_BATCH_SIZE)

    for column_index, (
            harvest_product_name,
            harvest_product
    ) in enumerate(harvest_product_batch):
        with harvest_product_batch_columns[column_index]:
            HARVEST_PRODUCT_PRODUCTION_COUNTS[
                    harvest_product_name
            ] = streamlit.number_input(
                harvest_product_name,
                min_value=int(
                    HARVEST_PRODUCT_PRODUCTION_COUNTS[harvest_product_name]
                ),
                step=1,
                value=int(
                    HARVEST_PRODUCT_PRODUCTION_COUNTS[harvest_product_name]
                ),
                key=f"Harvest Product {harvest_product_name} Count",
                help=(
                    "\n".join(
                        [
                            f"**{harvest_product.name}**\n",
                            f"Sprouts Yield: \n",
                            *[
                                (
                                    f"* {plant_sprout_name}: "
                                    f"`{plant_sprout_yield}` / "
                                    f"""
                                     `{PLANT_SPROUTS[
                                         plant_sprout_name
                                     ].growth_time}` min
                                     = `{PLANT_SPROUTS[
                                         plant_sprout_name
                                     ].harvest_yield_per_hour:.2f}` per hour
                                    """
                                )
                                for (
                                    plant_sprout_name,
                                    plant_sprout_yield
                                ) in harvest_product.harvest_quantities.items()
                            ]
                        ]
                    )
                )
            )

streamlit.header("Production Results per Harvest")

(
    REQUIRED_FOOD_ITEMS_COLUMN,
    REQUIRED_HARVEST_PRODUCTS_COLUMN,
    RECOMMENDED_PLANT_SPROUTS_COLUMN,
    ACTUAL_HARVEST_PRODUCTS_COLUMN
) = streamlit.columns(4)

with REQUIRED_FOOD_ITEMS_COLUMN:
    streamlit.write(FOOD_ITEM_PRODUCTION_COUNTS)

with REQUIRED_HARVEST_PRODUCTS_COLUMN:
    streamlit.write(HARVEST_PRODUCT_PRODUCTION_COUNTS)

PLANT_SPROUTS_COUNTS: Dict[Text, NonNegativeInt] = {
    plant_sprout_name: 0
    for plant_sprout_name in PLANT_SPROUTS
}

ACTUAL_HARVEST_PRODUCTS_COUNT: Dict[Text, NonNegativeInt] = {
    harvest_product_name: 0
    for harvest_product_name in HARVEST_PRODUCTS
}

for (
        harvest_product_name,
        harvest_product_count
) in HARVEST_PRODUCT_PRODUCTION_COUNTS.items():
    if harvest_product_count > 0:
        harvest_product = HARVEST_PRODUCTS[harvest_product_name]

        plant_sprouts = sorted(
            [
                PLANT_SPROUTS[plant_sprout_name]
                for (
                        plant_sprout_name,
                        growth_time
                ) in harvest_product.harvest_growth_times.items()
                if growth_time <= HARVEST_INTERVAL
            ],
            key=lambda plant_sprout: plant_sprout.harvest_yield_per_hour,
            reverse=True
        )

        best_plant_sprout: PlantSprout

        if len(plant_sprouts) == 0:
            best_plant_sprout, *_ = list(harvest_product.plant_sprouts.values())
        else:
            best_plant_sprout, *_ = plant_sprouts

        best_plant_sprout_count: PositiveInt = (
            harvest_product_count / HARVEST_INTERVAL
        ) / (
            best_plant_sprout.harvest_yield / best_plant_sprout.growth_time
        )

        PLANT_SPROUTS_COUNTS[best_plant_sprout.name] = math.ceil(
            best_plant_sprout_count
        )

for (
        plant_sprout_name,
        plant_sprout_count
) in PLANT_SPROUTS_COUNTS.items():
    plant_sprout = PLANT_SPROUTS[plant_sprout_name]

    ACTUAL_HARVEST_PRODUCTS_COUNT[plant_sprout.harvest_type] += (
        plant_sprout.harvest_yield / plant_sprout.growth_time
    ) * HARVEST_INTERVAL * plant_sprout_count

with RECOMMENDED_PLANT_SPROUTS_COLUMN:
    streamlit.write(PLANT_SPROUTS_COUNTS)

with ACTUAL_HARVEST_PRODUCTS_COLUMN:
    streamlit.write(ACTUAL_HARVEST_PRODUCTS_COUNT)  # TODO: fix
