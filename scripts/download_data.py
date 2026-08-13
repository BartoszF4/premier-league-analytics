import requests
from pathlib import Path

SEASON_CODES = [
    "1516", "1617", "1718", "1819", "1920",
    "2021", "2122", "2223", "2324", "2425",
]

CURRENT_SEASON_CODE = "2526"

BASE_URL = "https://www.football-data.co.uk/mmz4281/{code}/E0.csv"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"


def download_season(code: str) -> None:
    url = BASE_URL.format(code=code)
    output_path = OUTPUT_DIR / f"E0_{code}.csv"

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    output_path.write_bytes(response.content)
    print(f"Downloaded season {code} -> {output_path}")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for code in SEASON_CODES + [CURRENT_SEASON_CODE]:
        try:
            download_season(code)
        except requests.RequestException as exc:
            print(f"Failed to download season {code}: {exc}")


if __name__ == "__main__":
    main()