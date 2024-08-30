
EVENT_ID = "ocel_id"
TIMESTAMP = "ocel_time"
ACTIVITY = "ocel_type"
OBJECT_ID = "ocel_id"
OBJECT_TYPE = "ocel_type"
QTY_OPERATION = "ocel_object_qty_operation"
QUALIFIER = "ocel_qualifier"
O2O_SOURCE = "ocel_source_id"
O2O_TARGET = "ocel_target_id"
E2O_EVENT = "ocel_event_id"
E2O_OBJECT = "ocel_object_id"
COLLECTION_ID = "ocel_cpid"
OBJECT_CHANGE = "ocel_changed_field"
ACTIVITY_MAP = "ocel_type_map"
OBJECT_TYPE_MAP = "ocel_type_map"
TABLE_MAPPING_OBJECT = "object_map_type"
TABLE_MAPPING_EVENT = "event_map_type"
TABLE_OBJECT_QTY = "object_quantity"
TABLE_EVENT_OBJECT = "event_object"
TABLE_OBJECT_OBJECT = "object_object"
TABLE_EVENT = "event"
TABLE_EQTY = "quantity_operations"
TABLE_OBJECT = "object"
TABLE_ACTIVITY_PREFIX = "event_"
TABLE_OBJECT_PREFIX = "object_"
OBJECT_COLUMNS = [OBJECT_ID, OBJECT_TYPE, TIMESTAMP, OBJECT_CHANGE]

TOOL_STATE_QTY = "log_quantity_state"
STATE_DEMO = "demo_mode"

TERM_ACTIVE = "active"
TERM_INACTIVE = "inactive"
TERM_QOP = "quantity_operation"
TERM_INIT = "init"
TERM_INITIAL_ILVL = "initial_item_levels"
TERM_OBJECT_QTY = "object_quantity"
TERM_END_TIME = "end_timestamp"
TERM_NAME = "name"
TERM_ID = "id"
TERM_TYPE = "type"
TERM_DATA = "data"
TERM_DIRECTION = "qty_direction"
TERM_ADDING_REMOVING = "both"

TERM_ADDING = "adding"
TERM_REMOVING = "removing"
TERM_EVENT_PERSPECTIVE = "event"
TERM_QUANTITY_UPDATE_PERSPECTIVE = "quantity_update"
TERM_QUANTITY_OPERATION_PERSPECTIVE = "quantity_operation"
TERM_COLLECTION = "Collection"
TERM_ACTIVITY = "Activity"
TERM_EVENT = "Events"
TERM_EVENTS = TERM_EVENT
TERM_OBJECT = "Objects"
TERM_OBJECT_TYPE = "Object Types"
TERM_QUANTITY_OPERATIONS = "Quantity Operations"
TERM_TIME = "Time"
TERM_ITEM_TYPES = "Item Types"
TERM_QTY_OBJECTS = "Quantity Objects"
TERM_QTY_OBJECT_TYPES = "Quantity Object Types"
TERM_QTY_EVENTS = "Quantity Events"

# terminology element overview
TERM_RELATED_EVENTS = "related events"
TERM_RELATED_QTY_OPERATIONS = "related quantity operations"
TERM_RELATED_QTY_EVENTS = "related quantity events"
TERM_QUANTITY_RELATIONS = "quantity relations"
TERM_QTY_ACTIVITIES = "q-activities"
TERM_RELATED_QTY_ACTIVITIES = "related quantity activities"
TERM_OBJECT_TYPES = "object types"
TERM_RELATED_OBJECT_TYPES = "related object types"
TERM_RELATED_OBJECTS = "related objects"
TERM_RELATED_ITEM_TYPES = "related item types"
TERM_RELATED_QTY_OBJECTS = "related quantity objects"
TERM_RELATED_QTY_OBJECT_TYPES = "related quantity object types"
TERM_RELATED_ACTIVITIES = "related activities"
TERM_E2O = "Event to Object Relations"
TERM_ACTIVE_QOP = "Active Quantity Relations"
TERM_ITEM_LEVELS = "Item Levels"
TERM_ITEM_QUANTITY = "Item Quantities"
TERM_ALL = "All"
TERM_ANY = "Any"
TERM_NONE = "None"
TERM_ITEM_TYPE_ACTIVE = "Item Type Active"
TERM_QUANTITY_UPDATES: str = "Quantity Updates"
TERM_COMBINED = "Combined"
TERM_COMBINED_INSTANCES = "Combined Instances"

TERM_OBJECT_TYPE_COUNT = "object_count"
TERM_OBJECT_COUNT = "total_objects"
TERM_EXECUTION_COUNT = "Execution no."
TERM_INSTANCE_COUNT = "instance_count"

EVENT_COUNT = "Event Count"
TERM_RELATIVE_FREQUENCY = "relative_frequency"
TERM_CP_ACTIVE = "collection point active"

TERM_ITEM_MOVEMENTS = "Material Movement"
TERM_QUANTITY_CHANGES = "Quantity Changes"
TERM_ACTIVE_OPERATIONS = "Active Quantity Operations"
TERM_ACTIVE_UPDATES = "Active Quantity Updates"

POST_EVENT_ILVL = "Post Event Item Level"
PRE_EVENT_ILVL = "Pre Event Item Level"

TERM_ITEM_ASSOCIATION = "Item Association"
ILVL_AVAILABLE = "Available"
ILVL_REQUIRED = "Required"

QOP_ID = "qop_id"
QOP_COUNT = "qop_count"
TERM_EVENT_DATA = "event_data"
TERM_OBJECT_DATA = "object_data"
TERM_OBJECT_TYPE_COMBINATION = "object type combinations"
TERM_OBJECT_TYPE_COMBINATION_FREQUENCY = "object type combination frequency"
TERM_SUBLOG = "Sublog"
TERM_COUNT = "Count"
TERM_DAILY = "Daily"
TERM_MONTHLY = "Monthly"
TERM_QUP_TYPE = "Quantity Update Type"

AGG_QTY = "Quantity"
AGG_ABS = "Items"
AGG_POSITIVE = "Positive"
AGG_NEGATIVE = "Negative"
AGG_ILVL_QTY = "Item Balance"
AGG_ILVL_ITEM = "Item Association"
AGG_ILVL_AVAILABLE = "Available Items"
AGG_ILVL_REQUIRED = "Required Items"
AGG_QOP_IT_BALANCE = "Total Quantity Balance"
AGG_QOP_IT_MOVEMENTS = "Total Item Moves"
AGG_QOP_IT_ADDING = "Total Added Items"
AGG_QOP_IT_REMOVING = "Total Removed Items"

QOP_AGG_CP_QTY = "Joint Quantity Operation"
QOP_AGG_CP_ABS = "Joint Item Movements"
TERM_VALUE = "Value"

TERM_AGG_CP = "Joint"
TERM_AGG_ITEM_TYPES = "Total"

ILVL_AGG_CP_QTY_STATE = "Joint Quantity State"


EVENT_AGG_QTY = "Overall Quantity Operation"
EVENT_AGG_ABS = "Overall Item Movements"

TERM_TIME_SINCE_LAST_EXECUTION = "Time since last execution"

# ###### Defaults #######
# INITIAL_TIME = datetime.datetime(year=2019, month=10, day=12, hour=12, minute=21)



CHART_COLOURS = ["#006165", # petrol
                 "#CE108A", # pink
                 "#0098A1", # turquoise
                 "#F6A800", # orange
                "#00549F", # blue
                "#6f2b4b",# purple
                 "#8EBAE5", # light blue
                "#000080", # dark blue
                "#007e56", # lighter greeny-turquoise
                "#005d4c", # perl-ophal green
                "#a1dfd7", #light-turquoise
                "#cd00cd", # pink

                 "#28713e", # green
                 "#701f29", # purpur-red

                 "#5d2141", # other purple
                 "#a1dfd7", #light-turquoise

                "#00ffff", # cyan
                "#39ff14", # neon green
                 "#800080", #purpur
                "#005f6a", # blue-petrol
                "#76e1e0", # another turquopise
                "#f5ff00" # neon-yellow
                 ]

