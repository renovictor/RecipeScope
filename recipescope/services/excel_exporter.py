from __future__ import annotations

from pathlib import Path

import pandas as pd


class ExcelExporter:
    def export(self, dataframe: pd.DataFrame, output_path: str | Path) -> None:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        dataframe.to_excel(output, index=False, engine="openpyxl")
