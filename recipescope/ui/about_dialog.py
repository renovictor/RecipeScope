from __future__ import annotations

from PySide6.QtWidgets import QDialog, QLabel, QVBoxLayout

from version import (
    AUTHOR_EMAIL,
    AUTHOR_NAME,
    COMPANY_NAME,
    DEPARTMENT_NAME,
    RELEASE_DATE,
    get_display_name,
)


class AboutDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("About RecipeScope")
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(get_display_name()))
        layout.addWidget(QLabel(f"Company: {COMPANY_NAME}"))
        layout.addWidget(QLabel(f"Department: {DEPARTMENT_NAME}"))
        layout.addWidget(QLabel(f"Author: {AUTHOR_NAME}"))
        layout.addWidget(QLabel(f"Email: {AUTHOR_EMAIL}"))
        layout.addWidget(QLabel(f"Release Date: {RELEASE_DATE}"))
