from enum import Enum


# X - lewo(wartości ujemne), prawo(wartości dodatnie)
# Y - dół(wartości ujemne), góra(wartości dodatnie)
# Z - do przodu(wartości ujemne), do tyłu(wartości dodatnie)
class Axis(Enum):
    X = 0
    Y = 1
    Z = 2
