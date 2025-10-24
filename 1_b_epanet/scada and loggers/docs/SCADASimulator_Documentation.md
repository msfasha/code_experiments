# SCADASimulator Class Documentation

## 📋 **Class Overview**

The `SCADASimulator` class is the core component that generates realistic SCADA sensor data for water distribution networks. It simulates pressure, flow, and tank level readings based on baseline network conditions with time-of-day variations and sensor noise.

## 🏗️ **Class Structure**

```python
class SCADASimulator:
    """SCADA data simulator that generates synthetic sensor readings"""
```

## 🔧 **Instance Variables**

| **Variable** | **Type** | **Purpose** |
|--------------|----------|-------------|
| `_running` | `bool` | Tracks if simulator is currently running |
| `_task` | `asyncio.Task` | Async task handle for simulation loop |
| `_config` | `SCADASimulatorConfig` | Database configuration object |
| `_network_loader` | `NetworkLoader` | Handles EPANET network loading |
| `_demand_forecaster` | `DemandForecaster` | Estimates time-based demand patterns |

---

## 📚 **Public Methods**

### **1. `__init__(self)`**
**Purpose**: Initialize the SCADA simulator instance
**Parameters**: None
**Returns**: None

**What it does**:
- Sets initial state variables (`_running = False`)
- Initializes task handle (`_task = None`)
- Creates service dependencies (NetworkLoader, DemandForecaster)

---

### **2. `is_running` (Property)**
**Purpose**: Check if simulator is currently running
**Parameters**: None
**Returns**: `bool`

**What it does**:
- Returns the current running state
- Used by other components to check simulator status

---

### **3. `async start(self, config: Dict[str, Any] = None) -> Dict[str, Any]`**
**Purpose**: Start the SCADA simulation
**Parameters**: 
- `config` (optional): Configuration overrides
**Returns**: Dictionary with success status and configuration

**What it does**:
1. **Check if already running**: Prevents multiple instances
2. **Load/Create configuration**: Gets config from database or creates new
3. **Update configuration**: Applies any provided config overrides
4. **Validate network**: Ensures network file is loaded (REQUIRED)
5. **Start simulation loop**: Creates async task for data generation
6. **Update database**: Marks simulator as running
7. **Return status**: Provides configuration and success message

**Error Handling**:
- Returns error if already running
- Returns error if no network loaded
- Logs and returns error on database failures

---

### **4. `async stop(self) -> Dict[str, Any]`**
**Purpose**: Stop the SCADA simulation
**Parameters**: None
**Returns**: Dictionary with success status

**What it does**:
1. **Check database state**: Verifies simulator is actually running
2. **Set running flag**: `_running = False`
3. **Cancel async task**: Stops the simulation loop
4. **Update database**: Marks simulator as stopped
5. **Return status**: Confirms successful stop

**Error Handling**:
- Returns error if simulator not running
- Logs and returns error on database failures

---

### **5. `async get_status(self) -> Dict[str, Any]`**
**Purpose**: Get current simulator status and configuration
**Parameters**: None
**Returns**: Dictionary with status and configuration

**What it does**:
1. **Query database**: Gets current configuration
2. **Return status**: Provides running state and all config parameters
3. **Include config**: Shows update_interval, variation percentages, fault_injection

**Error Handling**:
- Returns error if no configuration found
- Logs and returns error on database failures

---

### **6. `async get_latest_readings(self, limit: int = 100) -> Dict[str, Any]`**
**Purpose**: Get the most recent SCADA readings from database
**Parameters**: 
- `limit`: Maximum number of readings to return (default: 100)
**Returns**: Dictionary with readings grouped by node and sensor type

**What it does**:
1. **Query database**: Gets latest readings ordered by timestamp
2. **Group by node**: Organizes readings by node_id and sensor_type
3. **Format data**: Provides value, unit, timestamp, quality for each reading
4. **Return results**: Includes count and grouped readings

**Error Handling**:
- Logs and returns error on database failures

---

## 🔄 **Private Methods (Internal)**

### **7. `async _simulation_loop(self)`**
**Purpose**: Main simulation loop that continuously generates SCADA data
**Parameters**: None
**Returns**: None

**What it does**:
1. **Start loop**: Logs simulation start
2. **Continuous generation**: While `_running = True`:
   - Generate SCADA data
   - Wait for update interval
   - Handle cancellation
   - Handle errors with retry
3. **End loop**: Logs simulation stop

**Error Handling**:
- Catches `CancelledError` for graceful shutdown
- Catches other exceptions and retries after 5 seconds
- Logs all errors for debugging

---

### **8. `async _generate_scada_data(self)`**
**Purpose**: Generate one batch of SCADA readings
**Parameters**: None
**Returns**: None

**What it does**:
1. **Check network**: Ensures network is loaded
2. **Get current time**: For time-of-day variations
3. **Check baseline**: Requires established baseline (no fallback)
4. **Generate data**: Calls baseline-based data generation
5. **Commit to database**: Saves all readings
6. **Log success**: Confirms data generation

**Error Handling**:
- Returns early if no network loaded
- Raises exception if baseline not established
- Rolls back database on errors
- Logs all errors

---

### **9. `async _generate_baseline_based_data(self, db, current_time: datetime)`**
**Purpose**: Generate SCADA data based on baseline + variations
**Parameters**: 
- `db`: Database session
- `current_time`: Current timestamp for time variations
**Returns**: None

**What it does**:
1. **Get baseline values**: Pressures, flows, tank levels from baseline engine
2. **Generate pressure readings**: For all junctions with time variations and noise
3. **Generate flow readings**: For all pumps with time variations and noise
4. **Generate level readings**: For all tanks with time variations and noise
5. **Apply constraints**: Ensures realistic value ranges
6. **Store readings**: Adds all readings to database

**Error Handling**:
- Logs and re-raises errors for upstream handling

---

### **10. `_get_time_of_day_variation(self, current_time: datetime) -> float`**
**Purpose**: Calculate time-of-day variation factor
**Parameters**: 
- `current_time`: Current timestamp
**Returns**: Float between -1 and +1

**What it does**:
1. **Extract hour**: Gets hour from current time
2. **Apply patterns**:
   - **Morning peak (7-9 AM)**: +50% to +100%
   - **Evening peak (6-8 PM)**: +30% to +80%
   - **Night low (2-5 AM)**: -50% to -80%
   - **Normal day**: -20% to +20%
3. **Return factor**: Random value within appropriate range

---

### **11. `_run_hydraulic_simulation(self, network, demands: Dict[str, float]) -> Optional[Dict[str, Any]]`**
**Purpose**: Run EPANET hydraulic simulation (legacy method)
**Parameters**: 
- `network`: EPANET network object
- `demands`: Dictionary of junction demands
**Returns**: Simulation results or None if failed

**What it does**:
1. **Set demands**: Applies demand values to network
2. **Run analysis**: Opens and runs hydraulic analysis
3. **Check convergence**: Ensures simulation converged
4. **Extract results**: Gets pressures, flows, tank levels
5. **Close analysis**: Cleans up EPANET resources
6. **Return results**: Structured data with all values

**Error Handling**:
- Returns None if simulation fails to converge
- Logs and returns None on EPANET errors
- Ensures proper cleanup of EPANET resources

---

### **12. `async _store_pressure_readings(self, db, results: Dict[str, Any])`**
**Purpose**: Store pressure readings with sensor noise (legacy method)
**Parameters**: 
- `db`: Database session
- `results`: Simulation results dictionary
**Returns**: None

**What it does**:
1. **Extract pressures**: Gets pressure values from results
2. **Convert units**: Meters to PSI (1 meter = 1.42 PSI)
3. **Add noise**: ±2% typical sensor noise
4. **Apply constraints**: 10-150 PSI range
5. **Create readings**: SCADAReading objects
6. **Store in database**: Adds readings to session

---

### **13. `async _store_flow_readings(self, db, results: Dict[str, Any])`**
**Purpose**: Store flow readings for pumps (legacy method)
**Parameters**: 
- `db`: Database session
- `results`: Simulation results dictionary
**Returns**: None

**What it does**:
1. **Get pump data**: Extracts pump IDs and flows
2. **Convert units**: L/s to GPM (1 L/s = 15.85 GPM)
3. **Add noise**: ±5% typical flow meter noise
4. **Apply constraints**: Non-negative flow values
5. **Create readings**: SCADAReading objects
6. **Store in database**: Adds readings to session

**Error Handling**:
- Logs warnings for individual pump failures
- Continues processing other pumps

---

### **14. `async _store_tank_levels(self, db, results: Dict[str, Any])`**
**Purpose**: Store tank level readings (legacy method)
**Parameters**: 
- `db`: Database session
- `results`: Simulation results dictionary
**Returns**: None

**What it does**:
1. **Get tank data**: Extracts tank IDs and levels
2. **Convert units**: Meters to feet (1 meter = 3.28 feet)
3. **Add noise**: ±1% typical level sensor noise
4. **Apply constraints**: Non-negative level values
5. **Create readings**: SCADAReading objects
6. **Store in database**: Adds readings to session

---

## 🔄 **Data Flow Summary**

```
1. start() → _simulation_loop() → _generate_scada_data()
2. _generate_scada_data() → _generate_baseline_based_data()
3. _generate_baseline_based_data() → Creates SCADAReading objects
4. SCADAReading objects → db.add() → Database storage
5. Time variations → _get_time_of_day_variation()
6. stop() → Cancels _simulation_loop()
```

## 🎯 **Key Features**

- **Baseline-Based**: Uses established network baseline as reference
- **Time-Aware**: Applies realistic time-of-day variations
- **Sensor Realism**: Adds appropriate noise for each sensor type
- **Physical Constraints**: Enforces realistic value ranges
- **Error Handling**: No fallback - requires proper baseline
- **Asynchronous**: Non-blocking simulation loop
- **Configurable**: Adjustable intervals and variations

## ⚠️ **Important Notes**

- **Baseline Required**: Simulation will fail if baseline not established
- **No Fallback**: No fake data generation - requires real baseline
- **Network Required**: Must have network loaded before starting
- **Database Dependent**: All readings stored in database
- **Async Operations**: All methods are asynchronous for non-blocking operation
