# make/load databases

from Classes import database_class

def create_databases() -> dict[str, database_class.Database]:
    base = r"C:\Users\kwinw\OneDrive\Desktop\Junior S1\Yang. Lab\Structured Database for 2D Materials\Databases"

    dbs = {
        "original": database_class.Database("Original Database"),
        "chosen": database_class.Database("Cleaned Database"),
        "cleaned": database_class.Database("Chosen Database"),
        "prepared": database_class.Database("Prepared Database"),
        "final": database_class.Database("Final Database"),
    }

    dbs["original"].load(f"{base}\\original_database.json")
    dbs["chosen"].load(f"{base}\\chosen_database.json")
    dbs["cleaned"].load(f"{base}\\cleaned_database.json")
    dbs["prepared"].load(f"{base}\\prepared_database.json")
    dbs["final"].load(f"{base}\\final_database.json")

    return dbs