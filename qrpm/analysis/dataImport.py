import sqlite3

import pandas as pd

from qel_simulation import QuantityEventLog
from qrpm.GLOBAL import *


# TODO: Paramerize the names of the tables and columns so that data not using the standard's names can be imported

class ImporterQEL:

    def __init__(self, path_to_sqlite_file, **kwargs):

        self.object_id_col = OBJECT_ID
        self.event_id_col = EVENT_ID
        self.activity_col = ACTIVITY
        self.object_type_col = OBJECT_TYPE
        self.timestamp_col = TIMESTAMP
        self.collection_col = COLLECTION_ID
        self.object_change = OBJECT_CHANGE
        self.qualifier = QUALIFIER
        self.o2o_source = O2O_SOURCE
        self.o2o_target = O2O_TARGET
        self.activity_map = ACTIVITY_MAP
        self.object_map = OBJECT_TYPE_MAP
        self.e2o_event = E2O_EVENT
        self.e2o_object = E2O_OBJECT
        self.term_active = TERM_ACTIVE
        self.term_qop = TERM_QOP
        self.term_init = TERM_INIT
        self.term_item_types = TERM_ITEM_TYPES
        self.term_end_time = TERM_END_TIME
        self.activity_table = TABLE_ACTIVITY_PREFIX
        self.object_type_table = TABLE_OBJECT_PREFIX
        self.object_map_table = TABLE_MAPPING_OBJECT
        self.event_map_table = TABLE_MAPPING_EVENT
        self.object_qty_table = TABLE_OBJECT_QTY
        self.e2o_table = TABLE_EVENT_OBJECT
        self.o2o_table = TABLE_OBJECT_OBJECT
        self.event_table = TABLE_EVENT
        self.eqty_table = TABLE_EQTY
        self.object_table = TABLE_OBJECT

        for key, value in kwargs.items():
            setattr(self, key, value)

        self._path_to_sqlite_file = path_to_sqlite_file
        self.create_types_table_frame()
        self.get_mapping_tables()
        self.create_event_dict()
        self.create_object_dict()
        self.get_event_to_object_table()
        self.get_object_to_object_table()
        self.get_eqty_table()
        self.get_oqty_table()


    @property
    def file(self):
        return self._path_to_sqlite_file

    @property
    def type_table(self):
        return self._types_tables

    @property
    def object_mapping(self):
        return self._object_mapping

    @property
    def event_mapping(self):
        return self._event_mapping

    @property
    def events(self):
        return self._events

    @property
    def objects(self):
        return self._objects

    @property
    def o2o(self):
        return self._o2o_table

    @property
    def e2o(self):
        return self._e2o_table

    @property
    def eqty(self):
        return self._eqty_table

    @property
    def oqty(self):
        return self._oqty_table

    def get_mapping_tables(self):

        self._object_mapping = self.get_table_from_sqlite(self.object_map_table)
        self._event_mapping = self.get_table_from_sqlite(self.event_map_table)

    def get_table_names_from_sqlite(self):
        # Connect to your SQLite database
        conn = sqlite3.connect(self.file)

        # Create a cursor object to execute SQL queries
        cursor = conn.cursor()

        # Query the sqlite_master table to get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

        # Fetch all table names as a list
        table_names = cursor.fetchall()

        # Close the cursor and the connection
        cursor.close()
        conn.close()

        table_names = [table[0] for table in table_names]

        return table_names

    def get_table_from_sqlite(self, table_name):

        # Connect to the SQLite database
        conn = sqlite3.connect(self.file)

        # Define your SQL query
        sql_query = f"SELECT * FROM {table_name}"

        # Use pandas.read_sql_query() to fetch the data into a DataFrame
        df = pd.read_sql_query(sql_query, conn)

        # Close the database connection
        conn.close()

        if "index" in df.columns:
            df = df.set_index("index")
        elif table_name == "quantity_operations":
            pass
        elif "ocel_id" in df.columns:
            if "object" in table_name:
                if table_name == "object":
                    df = df.set_index("ocel_id")
                else:
                    pass
            else:
                df = df.set_index("ocel_id")
        else:
            pass

        return df

    def create_types_table_frame(self):

        # get activity - table name overview and mark as activity
        activity_table_names = self.get_table_from_sqlite(table_name=TABLE_MAPPING_EVENT)
        activity_table_names["type"] = ["activity"] * len(activity_table_names)

        # get object type - table name overview and mark as object type
        object_table_names = self.get_table_from_sqlite(table_name=TABLE_MAPPING_OBJECT)
        object_table_names["type"] = ["object"] * len(object_table_names)

        # combine overview tables
        types_tables = pd.concat([activity_table_names, object_table_names], axis=0)

        # set overview tables
        self._types_tables = types_tables

    def get_table_name_of_type(self, ocel_type):

        return self.type_table.loc[self.type_table["ocel_type"] == ocel_type, "ocel_type_map"].to_list()[0]

    def get_type_name_of_table(self, table_name):

        return self.type_table.loc[self.type_table["ocel_type_map"] == table_name, "ocel_type"].to_list()[0]

    def get_activity_names(self):
        return self.type_table.loc[self.type_table["type"] == "activity", "ocel_type"].to_list()

    def get_object_type_names(self):
        return self.type_table.loc[self.type_table["type"] == "object", "ocel_type"].to_list()

    def create_event_dict(self):

        event_dict = {}

        for activity in self.get_activity_names():
            # get table name
            table_name = self.get_table_name_of_type(activity)

            # get table
            activity_table = self.get_table_from_sqlite(f"event_{table_name}")

            # add table to events dict
            event_dict[activity] = activity_table

        self._events = event_dict

    def create_object_dict(self):

        object_dict = {}
        for object_type in self.get_object_type_names():
            # get table name
            table_name = self.get_table_name_of_type(object_type)

            # get table
            object_type_table = self.get_table_from_sqlite(f"object_{table_name}")

            # remove index
            object_type_table = object_type_table

            # add table to object_type dict
            object_dict[object_type] = object_type_table

        self._objects = object_dict

    def get_event_to_object_table(self):

        # get table
        e2o_table = self.get_table_from_sqlite(TABLE_EVENT_OBJECT)

        self._e2o_table = e2o_table

    def get_object_to_object_table(self):

        o2o_table = self.get_table_from_sqlite(TABLE_OBJECT_OBJECT)

        self._o2o_table = o2o_table

    def get_eqty_table(self):

        table_names = self.get_table_names_from_sqlite()

        if TABLE_EQTY in table_names:
            eqty = self.get_table_from_sqlite(TABLE_EQTY)
            self._eqty_table = eqty
        else:
            self._eqty_table = None

    def get_oqty_table(self):

        table_names = self.get_table_names_from_sqlite()

        if TABLE_OBJECT_QTY in table_names:
            oqty = self.get_table_from_sqlite(TABLE_OBJECT_QTY)
            self._oqty_table = oqty
        else:
            self._oqty_table = None

    def create_quantity_event_log(self):
        qel = QuantityEventLog(event_data=self.events, object_data=self.objects, e2o=self.e2o, o2o=self.o2o, eqty=self.eqty,
                         object_quantities=self.oqty, object_map_type=self.object_mapping,
                         event_map_type=self.event_mapping)

        return qel
def load_qel_from_file(file_path: str, **kwargs) -> QuantityEventLog:
    imp = ImporterQEL(path_to_sqlite_file=file_path, **kwargs)
    qel = imp.create_quantity_event_log()
    return qel
