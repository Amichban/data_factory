* New resistance event vertical slice: *

** event definition **
What: new_resistance or a level or prices where sellers overtake buyers.

How to identify: at ech snapshot (market data period) check previous green candle followed by current red candle -> new_resistance

- properties:
    - original_event_id: unique id
    - event_type: 'new_resistance'
    - event_creation_date: utc datetime when events happens
    - granularity: W,D,H4 or H1
    - instrument: instrument symbol (EUR_USD etc)
    - event_price_level : level at whcih event happened, formula = max of high or prev and current candle
    - atr_at_event: atr level at event creation
    - volume_at_event: volume number at event creation
    - new_resistance_negative_rebound: amplitude of rebound in absolute, formula = close - high (should be negative)
    - new_resistance_ngative_rebound_in_atr: amplitude of negative rebound in atr, formula = (close - high) / atr_at_event (should be negative, watch for divide by zero)
    - day_of_week
    - hours_of_day

- dependencies:
    - ohlc price data of previous and current candle
    - atr

- db: 
    - new_resistance_events_table: one row per event
    - support_and_resistance_master_table: all new resistance events will have an entry here with the same properties as above . Other properties will be filled later when other events will aplly to this support and resistance.

- UI: 
    - Side bar with Events as a collapsable menu
    - Events tables page under Events: 
        - selector for instrument and granularity and event type -> if new resistance selected, then display new_resistance_events_table

- Features: list of features created from new resistance table:
    - distance_from_last_new_resistance: formula = current reistance price level - previous new resistance price level
    - new_resistance_distance_velocity: last two distance_from_last_new_resistance. if most recent one is higher then accelerate otherwise decelerate.
    - distance_from_last_resistance_in_atr: formula = (current reistance price level - previous new resistance price level) / atr_at_event
    - time_between_new_and_last_new_resistance: time in hours between last new resistance and previous new resistance
    - double_time_between_new_resistance : last two time_between_new_and_last_new_resistance. if recent one lower then 'higher frequency' else 'lower frequency'
    - new_resistance_pattern: HH if distance_from_last_new_resistance is positive, LH if negative
    - volume_roc: rate of change of volue between this new resistance volume and the previous new resistance volume
    - double_volume_roc : last two volumes roc difference. if new volume roc is hgher then 'accelerating' otherwise 'decelerating
    - time since new resistance: time between snapshot time and last new resistance (incremented at each snapshot)
    - sum_of_new_resistances_last_30_periods: rolling sum
    - new_resistance_3_levels_sequence_encoder: formula take last 3 new_resistance_pattern and change them into numbers and cpncatenate. for instance HH, then LH, then HH should be 101. 
    _ new_resistance_4_levels_sequence_encoder: formula take last 4 new_resistance_pattern and change them into numbers and cpncatenate. for instance HH, then LH, then HH then HH should be 1011. 
    - new_resistance_5_levels_sequence_encoder: formula take last 5 new_resistance_pattern and change them into numbers and cpncatenate. for instance HH, then LH, then HH then HH then LH should be 10110. 
    - new_resistance_6_levels_sequence_encoder: formula take last 6 new_resistance_pattern and change them into numbers and cpncatenate. for instance HH, then LH, then HH then same sequence should be 101101. 
    - new_res_dustance_sequence_analysis : take th elast 4 distance_from_last_new_resistance in atr and apply the following:
    def encode_sequence_full(sequence):
    """
    Full encoding of [4, 2, 1] with all features
    """
    
    # Input validation
    if not sequence:
        return {'no_data': 1}
    
    features = {}
    
    # Level 1: Always computable
    features['last'] = 1
    features['count'] = 3
    
    # Level 2: Need 2+ points
    if len(sequence) >= 2:
        features['change'] = -3         # 1-4
        features['change_rate'] = -0.75 # -3/4
        features['final_velocity'] = -1  # 1-2
        
    # Level 3: Need 3+ points  
    if len(sequence) >= 3:
        features['acceleration'] = 1    # -1-(-2)
        features['curvature'] = 0.25    # 1/4 (convexity measure)
        
    # Encoded representation
    features['is_accelerating'] = 1
    features['is_geometric_decay'] = 1
    features['urgency_level'] = 3       # 1=low, 3=high based on last value
    
    return features

# Result for [4, 2, 1]:
result = {
    'last': 1,
    'count': 3,
    'change': -3,
    'change_rate': -0.75,
    'final_velocity': -1,
    'acceleration': 1,
    'curvature': 0.25,
    'is_accelerating': 1,
    'is_geometric_decay': 1,
    'urgency_level': 3
}


- Features UI:
    - Side bar with Features as a collapsable menu
    - Features tables page under Features: 
        - selector for instrument and granularity and event type -> if new resistance selected, then display new_resistance_features_table

- compute: 
    - mode1: batch: once at initiation of table. might have to deal with 140k candles for H1. Backfill the event table and features. can take few minutes. we can make it work locally and then copy to cloud if necessary as functions and cloud run can be limited in time. Need perfromance here (vectorize if possible)

    - mode2: spike mode. only if tables are backfilled. every hour for H1 for instance, process starts checks last time events and features were computed then fetch required data and computes everything in less than one second. can be cloud fucntion or run on kubernetes. 

Operations: 
    - stats about tables and runs ust be kept somewhere and also run status and time whether batch or spike. 

Operations UI:
    - Operations in the sidebar menu with page that provide access to the operations data. 

data source for market data:
# Firestore Schema Documentation

## Collection: `market_data`

This collection stores OHLCV (Open, High, Low, Close, Volume) market data for various instruments and time granularities.

### Document ID Format
```
{instrument_id}_{granularity}_{unix_timestamp}
```

**Example**: `EUR_USD_D_1722380400`

Where:
- `instrument_id`: Trading pair (e.g., EUR_USD, GBP_USD, etc.)
- `granularity`: Time frame (H1, H4, D, W)
- `unix_timestamp`: Unix timestamp in seconds

### Document Structure

```javascript
{
  // Required fields
  "instrument": "EUR_USD",        // String: Instrument/trading pair
  "granularity": "D",            // String: Time granularity (H1, H4, D, W)
  "timestamp": Timestamp,         // Firestore Timestamp object
  
  // OHLCV Candle data (required)
  "candle": {
    "open": 1.08550,            // Number: Opening price
    "high": 1.08780,            // Number: Highest price
    "low": 1.08420,             // Number: Lowest price
    "close": 1.08650,           // Number: Closing price
    "volume": 125000.0          // Number: Trading volume
  },
  
  // Bid prices (optional)
  "bid": {
    "open": 1.08548,
    "high": 1.08778,
    "low": 1.08418,
    "close": 1.08648
  },
  
  // Ask prices (optional)
  "ask": {
    "open": 1.08552,
    "high": 1.08782,
    "low": 1.08422,
    "close": 1.08652
  },
  
  // Mid prices (optional, calculated from bid/ask)
  "mid": {
    "open": 1.08550,
    "high": 1.08780,
    "low": 1.08420,
    "close": 1.08650
  }
}
```

### Supported Instruments (29 total)

see 'instruments_specs.py' in the same specs folder




### Supported Granularities

- **H1**: Hourly (timestamps at :00)
- **H4**: 4-hour (timestamps at 1:00, 5:00, 9:00, 13:00, 17:00, 21:00 in ET/NY time)
- **D**: Daily (timestamps at 21:00 or 22:00 UTC depending on DST)
- **W**: Weekly (timestamps on Sundays)

### Timestamp Generation

To query a specific candle, generate the document ID:

```python
from datetime import datetime

# For daily data at 21:00 UTC
ts = datetime(2025, 8, 11, 21, 0, 0)
unix_ts = int(ts.timestamp())
doc_id = f"EUR_USD_D_{unix_ts}"
# Result: "EUR_USD_D_1723410000"
```

### Query Examples

**Python - Get specific candle**:
```python
from google.cloud import firestore
from datetime import datetime

db = firestore.Client(project="dezoomcamp23")
collection = db.collection('market_data')

# Get specific daily candle
ts = datetime(2025, 8, 11, 21, 0, 0)
doc_id = f"EUR_USD_D_{int(ts.timestamp())}"
doc = collection.document(doc_id).get()

if doc.exists:
    data = doc.to_dict()
    candle = data['candle']
    print(f"Open: {candle['open']}, Close: {candle['close']}")
```

**Python - Query range of candles**:
```python
# Query H1 candles for EUR_USD
query = collection.where('instrument', '==', 'EUR_USD')\
                 .where('granularity', '==', 'H1')\
                 .order_by('timestamp', direction=firestore.Query.ASCENDING)\
                 .limit(100)

for doc in query.stream():
    data = doc.to_dict()
    print(f"{data['timestamp']}: {data['candle']['close']}")
```

### Data Availability

- **Historical depth**: Varies by instrument, typically from 2002-2005 onwards
- **Update frequency**: Real-time for H1, end-of-period for H4/D/W
- **Data gaps**: Weekends and holidays for forex markets
- **Quality**: Production data from OANDA

### Notes

1. **No data during weekends**: Forex markets are closed from Friday 21:00 UTC to Sunday 21:00 UTC
2. **Holiday gaps**: No data on major market holidays (Christmas, New Year, etc.)
3. **Timestamp alignment**: All timestamps are in UTC
4. **Volume data**: May be 0 or missing for some periods
5. **Bid/Ask spread**: Optional fields, not always present

### Access Requirements

- **Project ID**: `dezoomcamp23` (or your GCP project)
- **Authentication**: Google Cloud credentials with Firestore read access
- **Python SDK**: `google-cloud-firestore` package

### Example Connection

```python
from google.cloud import firestore
import os

# Set project (if not set via environment or gcloud)
os.environ['GCP_PROJECT_ID'] = 'dezoomcamp23'

# Initialize client
db = firestore.Client()

# Access collection
market_data = db.collection('market_data')
```

### Related Collections

There may be other collections like:
- `EUR_USD_D_snapshots_v8`: Versioned snapshot collections (legacy)
- Individual instrument collections (deprecated)

The primary collection for all market data is `market_data`.