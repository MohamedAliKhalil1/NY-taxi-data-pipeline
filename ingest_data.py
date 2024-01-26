#!/usr/bin/env python

import os
import argparse
from time import time
import pandas as pd
from sqlalchemy import create_engine

# user
# pass
# host
# url
# db
# table
# port

def main(params):
    user = params.user
    password = params.password
    host = params.host
    url = params.url
    db = params.db
    port = params.port
    table = params.table

    print(params)
    csv_name = "output.csv"

    os.system(f"wget {url} -O {csv_name}")
    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")
    engine.connect()

    df_iter = pd.read_csv(csv_name, chunksize=100000, iterator=True)
    #zone_data_df_iter = pd.read_csv("./data/taxi+_zone_lookup.csv", chunksize=100000, iterator=True)

    df = next(df_iter)
    df = try_cast_cols(df)
    df.head(n=0).to_sql(name=table, con=engine, if_exists="replace")

    df.to_sql(name=table, con=engine, if_exists="append")

    for df in df_iter:
        t_start = time()
        df = try_cast_cols(df)
        df.to_sql(name=table, con=engine, if_exists="append")
        t_end = time()
        print("inserted another chunk, took %.3f seconds" % (t_end - t_start))

    #zone_df = next(zone_data_df_iter)
    #zone_df.head(n=0).to_sql(name="zone_taxi_data", con=engine, if_exists="replace")
    #zone_df.to_sql(name="zone_taxi_data", con=engine, if_exists="append")


def try_cast_cols(df):
    """
    - try to cast timestamp cols for table yellow_taxi_data
    - in case of any other table casting will fail and df will be returned
    """
    try:
        df.lpep_pickup_datetime = pd.to_datetime(df.lpep_pickup_datetime)
        df.lpep_dropoff_datetime = pd.to_datetime(df.lpep_dropoff_datetime)
    except Exception:
        return df
    return df


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="data source link")
    parser.add_argument("--user", help="database user")
    parser.add_argument("--password", help="database passwort")
    parser.add_argument("--host", help="database host")
    parser.add_argument("--db", help="database name")
    parser.add_argument("--port", help="database port")
    parser.add_argument("--table", help="table name")
    args = parser.parse_args()
    print(args)
    main(args)