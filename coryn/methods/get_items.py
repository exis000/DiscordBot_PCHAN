import re
from collections.abc import AsyncGenerator, AsyncIterator
from itertools import zip_longest
from typing import Any, ClassVar

from lxml.etree import _Element
from lxml.html import fromstring

from coryn.initializable import Initializable
from coryn.models.item_models import AppearanceModel, ItemCardModel, ItemModel, ObtainFromModel, RecipeModel
from coryn.types import Items


class ItemParser:
    item_selector: ClassVar[dict[str, str]] = {
        "item_name": "div.card-title",
        "details": "div > div > div > p",
        "status_effect": "ul > li.active > div.table-grid.item-basestat > div",
    }
    # content > div.card-container > div >
    recipe_selector: ClassVar[dict[str, str]] = {
        "recipe_key": "ul > li > div.item-prop.mini > div > p",
        "recipe_value": "ul > li > div.item-prop.mini > div > div",
    }
    obtain_from_selector: ClassVar[dict[str, str]] = {
        "boss": "ul > li > div[id^='obtain'] > div > div > div.pagination-js-item > div:first-of-type",
        "dye": "ul > li > div[id^='obtain'] > div > div > div.pagination-js-item > div > div",
        "map": "ul > li > div[id^='obtain'] > div > div > div.pagination-js-item > div:last-of-type",
    }

    appearance_selector: ClassVar[dict[str, str]] = {
        "item_image": "div > div.item-upper > div > div > table > tr > td[background]",
        "appearance": "ul > li > div > table > tr > td[background]",
    }

    @classmethod
    async def parse_item(cls, card_selector: _Element) -> ItemModel | None:
        card_data = {}
        item_data = {
            key: [v.text_content().strip() for v in card_selector.cssselect(selector)]
            for key, selector in cls.item_selector.items()
        }

        try:
            item_name, item_type = re.findall(r"([a-zA-Z0-9' ]+)", " ".join(item_data["item_name"]))
        except ValueError:
            return None

        card_data["name"] = item_name
        card_data["type"] = item_type

        details = item_data["details"]
        card_data.update({details[i]: details[i + 1] for i in range(0, len(details), 2)})

        card_data["stats"] = {
            " ".join(stats.split()[:-1]): stats.split()[-1] for stats in item_data["status_effect"][1:]
        }

        return ItemModel(**card_data)

    @classmethod
    async def parse_obtain_from(cls, card_selector: _Element) -> list[ObtainFromModel] | None:
        item_data = {
            key: [v.text_content().strip() for v in card_selector.cssselect(selector)]
            for key, selector in cls.obtain_from_selector.items()
        }

        obtain_from = []
        for boss, dye, map_location in zip_longest(
            item_data["boss"],
            item_data["dye"],
            item_data["map"],
            fillvalue=None,
        ):
            obtain_from_data = {
                "boss": " ".join(boss.split()) if boss else None,
                "dye": " ".join(dye.split()) if dye else None,
                "map": " ".join(map_location.split()) if map_location else None,
            }
            obtain_from.append(ObtainFromModel(**obtain_from_data))

        return obtain_from or None

    @classmethod
    async def parse_recipe(cls, card_selector: _Element) -> RecipeModel | None:
        card_data = {}
        item_data = {
            key: [v.text_content().strip() for v in card_selector.cssselect(selector)]
            for key, selector in cls.recipe_selector.items()
        }

        for key, value in zip(item_data["recipe_key"], item_data["recipe_value"], strict=False):
            key_text = " ".join(key.split())
            value_text = " ".join(value.split())
            card_data.update({key_text: value_text})
        return RecipeModel(**card_data) or None

    @classmethod
    async def parse_appearance(cls, card_selector: _Element) -> AppearanceModel | None:
        appearance_data = {}
        item_data = {
            key: [v.get("background") for v in card_selector.cssselect(selector)]
            for key, selector in cls.appearance_selector.items()
        }

        if item_data["item_image"]:
            appearance_data["item_image"] = item_data["item_image"][0]

        if item_data["appearance"]:
            appearance_data.update(
                {
                    "male": item_data["appearance"][:3],
                    "female": item_data["appearance"][3:],
                },
            )
        return AppearanceModel(**appearance_data) or None

    @classmethod
    async def parse_card(cls, cards_css: list[_Element]) -> AsyncGenerator[dict[str, Any], Any]:
        for card in cards_css:
            item_data = await cls.parse_item(card)

            if not item_data:
                continue

            yield ItemCardModel(
                item=item_data,
                recipe=await cls.parse_recipe(card),
                obtain_from=await cls.parse_obtain_from(card),
                appearance=await cls.parse_appearance(card),
            ).model_dump()


class GetItems(Initializable):
    async def get_items(self, item_type: Items, name: str = "", show: int = 10) -> AsyncIterator:
        url = f"{self.base_url}/item.php?type={item_type.value}&name={name}&show={show}"
        async with self.session.get(url) as resp:
            if resp.status != 200:  # noqa: PLR2004
                raise ValueError
            parse = fromstring(await resp.text())
            cards = parse.cssselect("#content > div.card-container > div")

            async for card_data in ItemParser.parse_card(cards):
                yield card_data
