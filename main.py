# add main menu code in here when testing is done

from __future__ import annotations
import importlib

from Classes import database_class, report_class
from Functions.Helper import (
    dbs_load,
    report_print,
    db_choose)
from Functions.Helper import check_input
from Functions.Main import (
    api_search, 
    report_add, 
    report_remove, 
    save_all, 
    db_reports, 
    report_search,
    report_edit
)
from Procedures import clean_text

importlib.reload(api_search)
importlib.reload(report_class)
importlib.reload(database_class)
importlib.reload(check_input)
importlib.reload(report_print)
importlib.reload(dbs_load)
importlib.reload(report_add)
importlib.reload(save_all)
importlib.reload(report_remove)
importlib.reload(db_reports)
importlib.reload(db_choose)
importlib.reload(report_search)
importlib.reload(report_edit)
importlib.reload(clean_text)

# make/load databases
databases = dbs_load.create_databases()

original_db = databases["original"]
chosen_db   = databases["chosen"]
cleaned_db  = databases["cleaned"]
prepared_db = databases["prepared"]
final_db    = databases["final"]

def main() -> None:
    # basic interface code
    while True:
        print("\nMenu: ")
        print("1) Use API") # via API #
        print("2) Add a paper to a database") # add paper to a different database #
        print("3) Remove a paper from a database") # remove paper from its original database #
        print("4) List reports in a database") # print database contents #
        print("5) Search for a paper") #
        print("6) Edit paper information")
        print("7) Cleaning procedures")
        print("8) Analyze data") # analyze data in database #
        print("9) Save") #
        print("Q) Exit \n")

        choice = input("Enter your choice (1-9):").strip().lower()


        # quit
        if choice in {'q', 'quit', 'exit'}:
            print("Bye!")
            break

        # use the api
        elif choice == "1":
            api_search.run_api_search(original_db)

        # add to a database
        elif choice == '2':
            result= db_choose.db_choose(
                original_db = original_db, 
                chosen_db = chosen_db, 
                cleaned_db = cleaned_db, 
                prepared_db = prepared_db, 
                final_db = final_db,
            )

            if result is None:
                continue

            target_db, previous_db = result

            report_add.add_report(
                target_db = target_db,
                previous_db = previous_db
            )

            print("\n")

            save_all.save_all(
                original_db = original_db, 
                chosen_db = chosen_db,
                cleaned_db = cleaned_db,
                prepared_db = prepared_db,
                final_db = final_db
            )


        # remove from database
        elif choice == '3':
            result= db_choose.db_choose(
                original_db = original_db, 
                chosen_db = chosen_db, 
                cleaned_db = cleaned_db, 
                prepared_db = prepared_db, 
                final_db = final_db,
            )

            if result is None:
                continue

            target_db, _ = result # previous_db is unused

            report_remove.remove_report(
                target_db = target_db
            )


        # list reports in a database
        elif choice == '4':
            result= db_choose.db_choose(
                original_db = original_db, 
                chosen_db = chosen_db, 
                cleaned_db = cleaned_db, 
                prepared_db = prepared_db, 
                final_db = final_db,
            )

            if result is None:
                continue

            target_db, _ = result # previous_db is unused

            db_reports.db_reports_list(
                target_db = target_db
            )


        # get info by doi
        elif choice == '5':
            report_search.doi_search(
                original_db = original_db, 
                chosen_db = chosen_db, 
                cleaned_db = cleaned_db, 
                prepared_db = prepared_db, 
                final_db = final_db,
            )

        # edit paper by doi
        elif choice == '6':
            result= db_choose.db_choose(
                original_db = original_db, 
                chosen_db = chosen_db, 
                cleaned_db = cleaned_db, 
                prepared_db = prepared_db, 
                final_db = final_db,
            )

            if result is None:
                continue

            target_db, _ = result # previous_db is unused

            report_edit.edit_paper(target_db = target_db)

            print("\n")

            save_all.save_all(
                original_db = original_db, 
                chosen_db = chosen_db,
                cleaned_db = cleaned_db,
                prepared_db = prepared_db,
                final_db = final_db
            )


        # cleaning procedures
        elif choice == '7':
            print("No cleaning procedures added yet")
            continue
            #clean_text...
            # more procedures will be added late
    

        # analyze data
        elif choice == '8':
            print("No analyzation functions added yet")
            continue
            # functions for this will go into the analyzation folder


        # save
        elif choice == '9':
            print("\n")

            save_all.save_all(
                original_db = original_db, 
                chosen_db = chosen_db,
                cleaned_db = cleaned_db,
                prepared_db = prepared_db,
                final_db = final_db
            )
            print("All databases saved.")
        
        else:
            print("Invalid choice. Please enter a number between 1 and 9.")

if __name__ == "__main__":
    main()
