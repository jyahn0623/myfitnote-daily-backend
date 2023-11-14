import json 

def data_to_dict(data: str) -> dict:
    """
    this is for data to dict.
    this is needed to loads two times.
    """
    walk_data = json.loads((json.loads(data)))
    return walk_data