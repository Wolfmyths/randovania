import collections


def remove_expensive(recipes_raw: dict) -> None:
    """Given the data.raw.recipes dict, remove all mentions of expensive versions."""
    for recipe_data in recipes_raw.values():
        if "expensive" not in recipe_data:
            continue

        assert "normal" in recipe_data
        del recipe_data["expensive"]
        recipe_data.update(recipe_data.pop("normal"))


def get_recipes_for(recipes_raw: dict) -> dict[str, set[str]]:
    """Given the data.raw.recipes dict, returns a dict mapping item names to all recipes that can craft it."""
    recipes_for = collections.defaultdict(set)

    for recipe_name, recipe_data in recipes_raw.items():
        if recipe_data.get("subgroup") == "empty-barrel":
            continue

        results = []
        if "result" in recipe_data:
            results.append(recipe_data["result"])

        for it in recipe_data.get("results", []):
            if isinstance(it, dict):
                results.append(it["name"])
            else:
                results.append(it[0])

        for result in results:
            recipes_for[result].add(recipe_name)

    # Manual Overrides
    recipes_for["uranium-235"].remove("uranium-processing")  # no expecting 235 for science without kovarex
    recipes_for["uranium-238"].remove("kovarex-enrichment-process")  # costs more 238 than makes
    recipes_for["uranium-238"].remove("nuclear-fuel-reprocessing")  # not viable either
    del recipes_for["electric-energy-interface"]  # cheat item

    return recipes_for


def get_recipes_unlock_by_tech(techs_raw: dict[str, dict]) -> dict[str, list[str]]:
    return {
        tech_name: [effect["recipe"] for effect in data.get("effects", []) if effect["type"] == "unlock-recipe"]
        for tech_name, data in techs_raw.items()
    }


def get_techs_for_recipe(techs_raw: dict[str, dict]) -> dict[str, list[str]]:
    result = collections.defaultdict(set)

    for tech_name, recipes_unlocked in get_recipes_unlock_by_tech(techs_raw).items():
        for recipe in recipes_unlocked:
            result[recipe].add(tech_name)

    return {recipe: sorted(techs) for recipe, techs in result.items()}


def count_for_result(recipe: dict, target_result: str) -> int:
    """Given a recipe from data.raw.recipes and one item name, return how many copies of that item the recipe crafts.
    0 if not present."""
    results = []
    if "result" in recipe:
        results.append(recipe["result"])
    results.extend(recipe.get("results", []))

    for it in results:
        if isinstance(it, dict):
            if it["name"] == target_result:
                return it["amount"]
        elif isinstance(it, list):
            if it[0] == target_result:
                return it[1]
        elif it == target_result:
            return recipe.get("result_count", 1)

    return 0
