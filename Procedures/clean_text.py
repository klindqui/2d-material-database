# this py should contain multiple functions used to clean text

# code to search for the paper you need in the og database

# return the data object

# using the link in the data object get the text

# do cleaning procedures on the text

# add the text and the data object to the chosen database

import importlib

from Classes import database_class, report_class

importlib.reload(report_class)
importlib.reload(database_class)

def clean_procedure(
        *,
        original_db: database_class.Database,
        cleaned_db: database_class.Database
) -> None:
    
    while True:
        doi = input("Enter DOI (enter to cancel): ").strip()
        if not doi:
            return
    
        if original_db.contains_doi(doi):
            report: report_class.Report = original_db.get(doi)
            break
        else:
            print(f"This database, {original_db.name}, does not contain the DOI {doi}")
            continue

    url = report.link
