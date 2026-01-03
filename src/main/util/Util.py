class Util:
    def __init__(self):
        raise Exception("This is a utility class!")
    
    @staticmethod
    def inchesToMeters(inches):
        return inches * 0.0254

    @staticmethod
    def metersToInches(meters):
        return meters / 0.0254

    @staticmethod
    def millimetersToMeters(mm):
        return mm / 1000

    @staticmethod
    def metersToMillimeters(m):
        return 1000 * m

    @staticmethod
    def isSimilar(a: float, b: float, tolerance: float) -> bool:
        if (abs(a - b) < tolerance):
            return True

        return False
