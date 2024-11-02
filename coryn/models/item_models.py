from pydantic import BaseModel


class ItemModel(BaseModel):
    name: str
    type: str
    stats: dict[str, str]

    class Config:
        extra = "allow"


class ObtainFromModel(BaseModel):
    boss: str | None
    dye: str | None
    map: str | None


class RecipeModel(BaseModel):
    class Config:
        extra = "allow"


class ArmorGenderModel(BaseModel):
    male: list
    female: list


class AppearanceModel(BaseModel):
    item_image: str | None = None
    appearance: ArmorGenderModel | None = None


class ItemCardModel(BaseModel):
    item: ItemModel | None = None
    recipe: RecipeModel | None = None
    obtain_from: list[ObtainFromModel] | None = None
    appearance: AppearanceModel | None = None
