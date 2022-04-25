from pydantic import BaseConfig, BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel):

    class Config(BaseConfig):
        pass
