from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class ValidationIssue:
    level: str
    message: str
    row: int | None = None


@dataclass(slots=True)
class ValidationResult:
    errors: list[ValidationIssue] = field(default_factory=list)
    warnings: list[ValidationIssue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def add_error(self, message: str, row: int | None = None) -> None:
        self.errors.append(ValidationIssue("error", message, row))

    def add_warning(self, message: str, row: int | None = None) -> None:
        self.warnings.append(ValidationIssue("warning", message, row))
