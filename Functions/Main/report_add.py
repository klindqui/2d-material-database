from __future__ import annotations

import importlib
from typing import Optional

from Classes import database_class, report_class
from Functions.Helper import report_print
from Functions.Helper import check_input
from Functions.Main import save_all

importlib.reload(report_class)
importlib.reload(database_class)
importlib.reload(check_input)
importlib.reload(report_print)
importlib.reload(save_all)

def add_report(
        *, 
        target_db: database_class.Database,
        previous_db: Optional[database_class.Database],
) -> None:

    # case a: brand new report added to original
    if previous_db is None:
        while True:
            doi = input("Enter DOI (enter to cancel): ").strip()
            
            if not doi:
                return
            
            if target_db.contains_doi(doi):
                print(f"DOI {doi} already exists in {target_db.name}. Try another.")
                continue

            title = input("Enter title (Enter to cancel): ").strip()
            if not title:
                return

            link = input("Enter link (Enter to cancel): ").strip()
            if not link:
                return

            r = report_class.Report(DOI=doi, title=title, link=link)
            target_db.add_report(r)
            
            print(f"\n Added to {target_db.name}")
            report_print.print_report(r)

            return  
                
    # case b: move/copy from the previous DB by DOI
    else:
        while True:
            doi = input(f"Enter DOI to copy from {previous_db.name} (Enter to cancel): ").strip()
            
            if not doi:
                return
            
            if not previous_db.contains_doi(doi):
                print(f"DOI {doi} was not found in {previous_db.name}. Try again.")
                continue
            
            if target_db.contains_doi(doi):
                print(f"DOI {doi} already exists in {target_db.name}. Try another.")
                continue

            r = previous_db.get(doi)
            target_db.add_report(r)

            print(f"\nCopied from {previous_db.name} to {target_db.name}:")
            report_print.print_report(r)

            return