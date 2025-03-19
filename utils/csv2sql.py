#!/usr/bin/env python3
import pandas as pd
from sqlalchemy import create_engine

def main():

    # 1. Create a SQLAlchemy engine (modify the connection string for your database)
    engine = create_engine('sqlite:///my_database.db')

    for chunk in pd.read_csv('./healthy_all_associated_runs.csv', chunksize=100000, low_memory=False):
        chunk.to_sql('my_table', engine, if_exists='append', index=False)

    print("CSV data has been successfully inserted into the SQL table.")

if __name__ == "__main__":
    main()
