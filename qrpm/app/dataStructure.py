import numpy as np

from qrpm.analysis.quantityState import determine_quantity_state_qop
import qrpm.analysis.objectQuantities as oqtyy
from qrpm.app.data_operations.log_overview import get_log_overview
from qel_simulation import QuantityEventLog
from qrpm.analysis.dataImport import load_qel_from_file
from qrpm.analysis.generalDataOperations import convert_timestamp_columns_to_string, convert_numeric_columns
from qrpm.GLOBAL import TERM_E2O, TERM_QUANTITY_OPERATIONS, TERM_EVENT_DATA, TERM_OBJECT_DATA, TOOL_STATE_QTY, TERM_TIME, \
    STATE_DEMO, TERM_INITIAL_ILVL, TERM_ITEM_LEVELS, TERM_OBJECT_QTY, TERM_ALL

import base64
import pandas as pd
import json

def serialise_dataframe(df: pd.DataFrame):
    """Converts a DataFrame to a dictionaries that can be serialized to JSON."""

    if df is None or len(df) == 0:
        return None
    else:
        pass

    df = convert_timestamp_columns_to_string(df)
    # df = df.fillna("NAN")
    df_dict = df.to_dict(orient="tight")

    return df_dict

def transform_dict_to_json(data_dict: dict|None):
    """Transforms a dictionary to a JSON object."""

    if data_dict is None:
        return None
    else:
        pass

    df_json = json.dumps(data_dict)
    return df_json

def prepare_data_for_storage(data):
    """Prepare data for upload."""

    if data is None:
        return None
    else:
        pass

    if isinstance(data, pd.DataFrame):
        data = serialise_dataframe(data)
    elif isinstance(data, dict):
        for key, value in data.items():
            if isinstance(value, pd.DataFrame):
                data[key] = serialise_dataframe(value)
            else:
                pass
    else:
        pass

    return transform_dict_to_json(data)

def deserialize_dataframe(df_dict: dict | None):
    """Converts a dictionary to a DataFrame."""

    if df_dict is None:
        return None
    else:
        pass

    df = pd.DataFrame.from_dict(df_dict, orient="tight")
    df = df.replace("NAN", np.nan)
    df = convert_numeric_columns(df)
    if TERM_TIME in df.columns:
        df[TERM_TIME] = pd.to_datetime(df[TERM_TIME])
    else:
        pass

    return df

def get_raw_data(overview_json):
    overview_dict = json.loads(overview_json)


    e2o_dict = overview_dict[TERM_E2O]
    e2o = deserialize_dataframe(e2o_dict)
    overview_dict[TERM_E2O] = e2o
    event_dict = overview_dict[TERM_EVENT_DATA]
    events = deserialize_dataframe(event_dict)
    overview_dict[TERM_EVENT_DATA] = events
    object_dict = overview_dict[TERM_OBJECT_DATA]
    objects = deserialize_dataframe(object_dict)
    overview_dict[TERM_OBJECT_DATA] = objects

    qop_dict = overview_dict[TERM_QUANTITY_OPERATIONS]
    if  qop_dict is not None:
        qop = deserialize_dataframe(qop_dict)
        oqty_dict = overview_dict[TERM_OBJECT_QTY]
        oqty = deserialize_dataframe(oqty_dict)
        ilvl_dict = overview_dict[TERM_ITEM_LEVELS]
        ilvl = deserialize_dataframe(ilvl_dict)
    else:
        qop = None
        oqty = None
        ilvl = None


    overview_dict[TERM_QUANTITY_OPERATIONS] = qop
    overview_dict[TERM_OBJECT_QTY] = oqty
    overview_dict[TERM_ITEM_LEVELS] = ilvl

    return overview_dict

def get_raw_data_dataframes(overview_json):
    overview = get_raw_data(overview_json)
    events = overview[TERM_EVENT_DATA]
    objects = overview[TERM_OBJECT_DATA]
    e2o = overview[TERM_E2O]
    qop = overview[TERM_QUANTITY_OPERATIONS]
    ilvl = overview[TERM_ITEM_LEVELS]
    oqty = overview[TERM_OBJECT_QTY]

    return events, objects, e2o, qop, ilvl, oqty

def get_ocel_data(ocel_json):
    ocel_dict = json.loads(ocel_json)

    e2o_dict = ocel_dict[TERM_E2O]
    e2o = deserialize_dataframe(e2o_dict)
    event_dict = ocel_dict[TERM_EVENT_DATA]
    events = deserialize_dataframe(event_dict)
    object_dict = ocel_dict[TERM_OBJECT_DATA]
    objects = deserialize_dataframe(object_dict)

    return events, e2o, objects

def events_e2o_objects_from_ocel_dict(ocel):
    if ocel is None:
        return None, None, None
    else:
        return ocel[TERM_EVENT_DATA], ocel[TERM_E2O], ocel[TERM_OBJECT_DATA]

def events_e2o_objects_to_ocel_dict(events, e2o, objects):
    if len(events) > 0:
        return {TERM_EVENT_DATA: events, TERM_E2O: e2o, TERM_OBJECT_DATA: objects}
    else:
        return None

def qop_ilvl_oqty_to_qty_dict(qop, ilvl, oqty):

    if qop is not None and len(qop) > 0:
        return {TERM_QUANTITY_OPERATIONS: qop, TERM_ITEM_LEVELS: ilvl, TERM_OBJECT_QTY: oqty}
    else:
        if ilvl is not None and oqty is not None:
            return {TERM_QUANTITY_OPERATIONS: None, TERM_ITEM_LEVELS: ilvl, TERM_OBJECT_QTY: oqty}
        else:
            return None

def get_qty_data(qty_json):
    qty_dict = json.loads(qty_json)

    qop_dict = qty_dict[TERM_QUANTITY_OPERATIONS]
    qop = deserialize_dataframe(qop_dict)
    ilvl_dict = qty_dict[TERM_ITEM_LEVELS]
    ilvl = deserialize_dataframe(ilvl_dict)
    oqty_dict = qty_dict[TERM_OBJECT_QTY]
    oqty = deserialize_dataframe(oqty_dict)

    return qop, ilvl, oqty

def reset_qel(overview_json):
    events, objects, e2o, qop, ilvl, oqty = get_raw_data_dataframes(overview_json=overview_json)

    ocel = events_e2o_objects_to_ocel_dict(e2o=e2o,
                                           events=events,
                                           objects=objects)

    qty = qop_ilvl_oqty_to_qty_dict(qop=qop,
                                    ilvl=ilvl,
                                    oqty=oqty)

    return ocel, qty

def get_single_dataframe(df_json):

    df_dict = json.loads(df_json)

    return deserialize_dataframe(df_dict)

def store_single_dataframe(df: pd.DataFrame):
    if df is None:
        return None
    return json.dumps(serialise_dataframe(df))


#### one time functions ####
def parse_demo_data() -> (QuantityEventLog, dict):
    """Parse demo data and return a QuantityEventLog object."""

    with open('files/overview_data.json') as f:
        overview_data = json.load(f)

    qty_state = True
    demo_state = True
    state_store = create_initial_state_store(qty_state=qty_state, demo_state=demo_state)

    return transform_dict_to_json(overview_data), transform_dict_to_json(state_store)

def parse_upload(contents, **kwargs) -> QuantityEventLog:
    """Parse uploaded file, write sqlite and read it into a QuantityEventLog object."""

    # Decode the uploaded file
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    file_path = f"files/passed_file.sqlite"

    # write temporary file
    with open(file_path, 'wb') as tmp:
        tmp.write(decoded)

    # Create QEL object
    qel = load_qel_from_file(file_path)

    # # Delete the temporary file
    # os.unlink(tmp_path)
    return qel

def create_initial_state_store(qty_state: bool, demo_state: bool):
    state = dict()
    state[TOOL_STATE_QTY] = qty_state
    state[STATE_DEMO] = demo_state
    return state

def create_initial_stores(qel: QuantityEventLog):

    overview = get_log_overview(qel)

    # data frames
    e2o = qel.get_e2o_relationships()
    qop = qel.get_quantity_operations()
    events = qel.get_events()
    objects = qel.get_objects()
    initial_item_levels = overview[TERM_INITIAL_ILVL]


    overview[TERM_E2O] = serialise_dataframe(e2o)
    overview[TERM_QUANTITY_OPERATIONS] = serialise_dataframe(qop)
    overview[TERM_EVENT_DATA] = serialise_dataframe(events)
    overview[TERM_OBJECT_DATA] = serialise_dataframe(objects)

    if len(qop) > 0:
        qty_state = True
        ilvl = determine_quantity_state_qop(qop, initial_item_levels)
        oqty = oqtyy.determine_object_quantity(qop=qop, e2o=e2o,
                                               object_types=TERM_ALL)
        overview[TERM_ITEM_LEVELS] = serialise_dataframe(ilvl)
        overview[TERM_OBJECT_QTY] = serialise_dataframe(oqty)
    else:
        qty_state = False

    state_store = create_initial_state_store(qty_state=qty_state, demo_state=False)

    with open("files/overview_data.json", 'w') as file:
        json.dump(overview, file)

    return transform_dict_to_json(overview), transform_dict_to_json(state_store)
