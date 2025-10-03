# report class

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Report:
    DOI: str = field(repr=False)
    title: str = field(repr=False)
    link: str = field(repr=False)
    notes : Optional[str] = None
    text: Optional[str] = None


    # guard
    def __setattr__(self, name, value):
        if hasattr(self, name) and name in {'DOI', 'title', 'link'}:
            raise AttributeError(f"{name} is immutable and cannot be changed.")
        super().__setattr__(name, value)

    def __post_init__(self):
        if not isinstance(self.DOI, str):
            raise TypeError("DOI must be a string")
        if not isinstance(self.title, str):
            raise TypeError("title must be a string")
        if not isinstance(self.link, str):
            raise TypeError("link must be a string")


    # printing method
    def __str__(self) -> str:
        t = (self.title[:60] + "...") if len(self.title) > 60 else self.title
        return f"Report(DOI = {self.DOI}, title = {t!r}, link = {self.link})"


    # methods
    def add_notes(self, note: str) -> None:
        self.notes = (self.notes + "\n" if self.notes else "") + note

    def clean_title(self) -> None:
        cleaned = " ".join(self.title.split()).strip()
        object.__setattr__(self, "title", cleaned)

    def attach_text(self, text: str) -> None:
        self.text = text


    # serialization
    def to_dict(self) -> dict:
        return {
            "DOI": self.DOI,
            "title": self.title,
            "link": self.link,
            "notes": self.notes,
            "text": self.text
        }
    
    @staticmethod
    def from_dict(data: dict) -> "Report":
        return Report(
            DOI=data["DOI"],
            title=data["title"],
            link=data["link"],
            notes=data.get("notes"),
            text=data.get("text")
        )
