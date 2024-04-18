def get_input_by_id(e: dict, input_id: str) -> dict:
    for input in e["target"]["elements"]:
        if input.get("id") == input_id:
            return input
    raise Exception(f"Input not found: {input_id}")
