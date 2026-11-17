from __future__ import annotations

from pathlib import Path

from matplotlib.figure import Figure


class WaveformExporter:
    def export(self, figure: Figure, output_path: str | Path) -> None:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        ext = output.suffix.lower()
        if ext not in {".png", ".svg", ".pdf"}:
            raise ValueError("Waveform export supports .png, .svg, .pdf")
        figure.savefig(output, dpi=300, bbox_inches="tight")
