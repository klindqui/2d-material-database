import importlib

from Classes import database_class

importlib.reload(database_class)


def remove_report(
        *,
        target_db: database_class.Database
) -> None:

    while True:
        doi = input("Enter DOI (enter to cancel): ").strip()
        if not doi:
            return
        
        if not target_db.contains_doi(doi):
            print(F"DOI {doi} not found in {target_db.name}. Try again.")
            continue
    
        target_db.remove_report(doi)

        return
