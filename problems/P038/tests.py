import pandas as pd

from src.testing import case


def make_cases():
    return [
        case("基本ケース",
             {"train": pd.DataFrame({"region": ["Kanto", "Kansai", "Kanto"]}),
              "test": pd.DataFrame({"region": ["Kanto", "Okinawa", "Kansai", "Okinawa"]})},
             {"Okinawa"}),
        case("trainにだけある値は含めない",
             {"train": pd.DataFrame({"region": ["A", "B", "C"]}), "test": pd.DataFrame({"region": ["A", "D"]})},
             {"D"}),
        case("違いがない",
             {"train": pd.DataFrame({"region": ["A", "B"]}), "test": pd.DataFrame({"region": ["B", "B"]})},
             set()),
    ]
