def classify_water_level(level: int, min_level: int, max_level: int, x: int) -> int:
    """
    Classify the water level based on the given parameters.

    Params
    ------
    - level (int): The water level to classify.
    - min_level (int): The minimum water level.
    - max_level (int): The maximum water level.
    - x (int): The number of classes to classify the water level.

    Returns
    -------
    - int: The class of the water level.
    """
    if level < min_level:
        return 0
    else:
        return round((level - min_level) / (max_level - min_level) * x)
