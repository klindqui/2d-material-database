# database class

from dataclasses import dataclass, field, replace
from typing import  Optional, List, Dict, Tuple
import json
from Classes.report_class import Report # import Report class


@dataclass
class Database:
    name: str
    _by_doi: Dict[str, Report] = field(default_factory=dict, init=False, repr=False)

    # guard
    def __setattr__(self, key, value):
        if key == "name" and hasattr(self, "name"):
            raise AttributeError("Database name is immutable and cannot be changed")
        super().__setattr__(key, value)


    def __len__(self) -> int:
        return len(self._by_doi)

    def __str__(self) -> str:
        return f"Database(name = {self.name}, size = {len(self)})"
    
    def __iter__(self):
        for doi in sorted(self._by_doi.keys()):
            yield self._by_doi[doi]

    def __contains__(self, doi: str) -> bool:
        return doi in self._by_doi


    # methods
    def add_report(self, r: Report) -> None:
        if r.DOI in self._by_doi:
            print (f" Duplicate report with DOI {r.DOI}, not added to {self.name}.")
            return
        self._by_doi[r.DOI] = r
        
    def remove_report(self, doi: str) -> None:
        if self._by_doi.pop(doi, None) is None:
            print(f"No report with DOI {doi} found in {self.name}.")
        else:
            print(f"Report with DOI {doi} removed from {self.name}")

    def get (self, doi: str) -> Optional[Report]:
        return self._by_doi.get(doi)
    
    def contains_doi(self, doi: str) -> bool:
        return doi in self._by_doi
    
    def list(self) -> List[Report]:
        return list(self._by_doi.values())
    
    def info(self, doi: str) -> Optional[Tuple[str, str, str]]:
        r = self._by_doi.get(doi)
        return (r.DOI, r.title, r.link) if r else None

    
    # persistence
    def save(self, filepath: str) -> None:
        data = [r.to_dict() for r in self._by_doi.values()]
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"Saved {len(data)} reports to {filepath}")

    def load(self, filepath: str) -> None:
        try:
            with open(filepath, "r", encoding='utf-8') as f:
                data = json.load(f)
            for item in data:
                r = Report.from_dict(item)
                self.add_report(r)
            print (f"Loaded {len(data)} reports from {filepath}")
        except FileNotFoundError:
            print (f"File {filepath} not found. Starting with an empty database.")