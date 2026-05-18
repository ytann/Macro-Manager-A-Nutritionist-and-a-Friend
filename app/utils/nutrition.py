def normalize_to_100g(value: float, serving_size: float) -> float:
    """
    Normalizes a nutritional value to 100g given the serving size in grams or ml.
    Calculates: (value / serving_size) * 100
    """
    if serving_size <= 0:
        return 0.0
    return round((float(value) / float(serving_size)) * 100, 2)
