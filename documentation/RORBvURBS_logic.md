Author: Lindsay Millard 21 Aug 2025
Purpose: To provide notes and roadmap for implementation of URBS plugin to work with pyromb and in parallel to RORB.

### 1. Conceptual Model and Traversal Logic

Your analysis is spot on. Both RORB and URBS use a sequential, depth-first traversal of the catchment network to build their instruction set.

*   **RORB:** Calls this sequence the **"Control Vector"**. It's a list of numerical codes (1, 2, 3, 4, etc.) that dictate the order of operations. The data for each operation (like reach length) follows the code on the same line.
*   **URBS:** Uses a series of **text-based commands** (`RAIN`, `ADD RAIN`, `STORE`, etc.). The data for each command is provided as named parameters within the command line (e.g., `L=4.7`).

**Conclusion:** The core traversal logic you've implemented in your Python `Traveller` is **perfectly applicable to both**. The primary difference will be in the function that *writes* the output string at each step of the traversal.

### 2. File Structure Comparison

This is a fundamental difference in philosophy that your GUI's "Save" function must handle.

| Feature | RORB (.catg) | URBS (.vec/.u & .cat) |
| :--- | :--- | :--- |
| **Primary File(s)** | A single, monolithic file containing the control vector, sub-area data, reach data, graphical data, and often the storm data. | Two primary files. The **`.vec` or `.u`** file contains the control sequence (commands). The **`.cat`** file contains the tabular sub-catchment data (Area, Imperviousness, etc.). |
| **Data Linkage** | All data is contained within the file. | The `.vec` file links to the `.cat` file via the sub-catchment index number (`RAIN #1` refers to Index 1 in the `.cat` file). |
| **GUI Implication** | "Save" writes one comprehensive file. | "Save" must write/update **two separate files** that are inter-dependent. |

### 3. Command / Control Code Equivalence

This is the core of the translation. The logic is nearly identical, but the syntax is different.

| Hydrologic Action | RORB Control Code | URBS Command | Notes |
| :--- | :--- | :--- | :--- |
| **Start a branch (Headwater)** | `Code 1` (Sub-area Inflow) | `RAIN #{index}` | Both commands initiate a "running hydrograph" from a headwater sub-catchment. |
| **Add inflow & route** | `Code 2` (Add in Sub-area Inflow & Route) | `ADD RAIN #{index}` | Both commands add runoff from a subcatchment to the existing "running hydrograph". |
| **Store hydrograph (at junction)** | `Code 3` (Store Hydrograph) | `STORE.` | The logic is identical: save the main channel flow, then process the tributary. |
| **Add stored hydrograph** | `Code 4` (Add in Stored Hydrograph) | `GET.` | The logic is identical: retrieve the main channel flow and add the tributary flow to it. |
| **Route without local inflow** | `Code 5` (Route Hydrograph) | `ROUTE THRU #{index}` | Both are used for pure routing reaches. URBS's `THRU` command is used to associate the reach with the physical properties of a specific sub-catchment from the `.cat` file. |
| **Print Output at a Node** | `Code 7` (Print Calculated) / `Code 7.1` (Print vs Gauged) | `PRINT. {location_name}` | Both define an output location. URBS requires a text-based location name. |
| **Special Storage** | `Code 6` (Existing Special Storage) | `DAM ROUTE ...` | Both are used to model reservoirs, dams, etc. The implementation details vary significantly. |
| **End of Model Definition** | `Code 0` (End of Control Vector) | `END OF CATCHMENT DATA.` | Both commands signify the end of the routing instructions. |

### 4. Parameter and Data Input Comparison

| Data Type | RORB | URBS |
| :--- | :--- | :--- |
| **Sub-catchment Properties** (Area, Imperviousness) | Entered directly in the `.catg` file within a dedicated "sub-area data" block (Item 6.x). | Entered in a separate **`.cat` CSV file**. Your GUI will need a dedicated table editor for this. |
| **Reach Properties** (Length, Type/Slope) | Entered on the same line as the control code (e.g., `1, 1, 4.7, -99`). | Entered as named parameters within the command (e.g., `L=4.7 Sc=0.01`). |
| **Global Parameters** (kc, m, IL) | Entered interactively via the program's GUI windows. | Entered in the `.vec` file using the `DEFAULT PARAMETERS` command, or set via environment variables. |

### 5. Units Comparison


| Parameter | RORB Unit (Table 5-1) | URBS Unit (Table 2) | Notes |
| :--- | :--- | :--- | :--- |
| Reach Length | `km` | `km` | Identical. |
| Sub-catchment Area | `km²` | `km²` | Identical. |
| Discharge | `m³/s` | `m³/s` | Identical. |
| Rainfall | `mm` | `mm` | Identical. |
| Initial / Continuing Loss | `mm` / `mm/h` | `mm` / `mm/h` | Identical. |
| **Channel / Reach Slope** | **`%`** | **`m/m`** | **CRITICAL DIFFERENCE!** Your GUI must handle this conversion. |
| Fraction Imperviousness | Fraction (0-1) | Fraction (0-1) | Identical. |

### 6. Adapting Your Python Logic (Pseudo-code)

#### RORB `traverse_and_write_branch` (Existing Logic)

```python
# --- For RORB ---
def traverse_and_write_rorb(current_reach, vec_file):
    subcatchment = current_reach.associated_subcatchment
    
    # Write RORB-specific command: Code, Type, Length, End
    vec_file.write(f"1, {current_reach.type.value}, {current_reach.length}, -99\n") 
    
    # ... loop through branch ...
    while current_reach.end_node is not None:
        downstream_node = current_reach.end_node
        
        # Junction Logic
        tributaries = find_tributaries(downstream_node)
        for tributary_reach in tributaries:
            vec_file.write("3\n") # RORB STORE
            traverse_and_write_rorb(tributary_reach, vec_file) # Recursive call
            vec_file.write("4\n") # RORB GET

        # ... get next reach ...
        if next_reach_in_branch:
             next_subcatchment = next_reach_in_branch.associated_subcatchment
             # RORB Add Inflow & Route command
             vec_file.write(f"2, {next_reach.type.value}, {next_reach.length}, -99\n")
        
        if downstream_node.is_output_point:
            vec_file.write(f"7.1\n{downstream_node.name}\n") # RORB PRINT
```

#### URBS `traverse_and_write_branch` (URBS Logic)

```python
# --- For URBS ---
def traverse_and_write_urbs(current_reach, vec_file):
    subcatchment = current_reach.associated_subcatchment
    
    # Write URBS-specific command with named parameters
    # Note: Other params like Sc, CS could be added here.
    vec_file.write(f"RAIN #{subcatchment.index} L={current_reach.length}\n") 
    
    # ... loop through branch ...
    while current_reach.end_node is not None:
        downstream_node = current_reach.end_node
        
        # Junction Logic
        tributaries = find_tributaries(downstream_node)
        for tributary_reach in tributaries:
            vec_file.write("STORE.\n") # URBS STORE
            traverse_and_write_urbs(tributary_reach, vec_file) # Recursive call
            vec_file.write("GET.\n") # URBS GET

        # ... get next reach ...
        if next_reach_in_branch:
             next_subcatchment = next_reach_in_branch.associated_subcatchment
             # URBS Add Inflow & Route command
             vec_file.write(f"ADD RAIN #{next_subcatchment.index} L={next_reach.length}\n")
        
        if downstream_node.is_output_point:
            vec_file.write(f"PRINT. {downstream_node.name}\n") # URBS PRINT
```

**Summary for Your Agnostic Python Code:**

1.  **Shared Core:** Use a single `Traveller` class and a single traversal algorithm. The logic of visiting nodes, identifying headwaters, and handling junctions with `STORE`/`GET` is common to both.
2.  **Model-Specific "Writers":** Create separate classes or functions (`RorbVectorWriter`, `UrbsVectorWriter`) that are called during the traversal.
3.  **The Writer's Job:**
    *   The `RorbVectorWriter` will output numeric codes and their associated parameters on single lines. It will also be responsible for writing the sub-area data blocks (`Item 6.x`) at the end.
    *   The `UrbsVectorWriter` will output text commands with named parameters. It will *not* write the sub-area data to the `.vec` file. Instead, your GUI's "Save" function must also call a separate `UrbsCatWriter` that iterates through all subcatchment objects and generates the `.cat` CSV file.
4.  **Unit Conversion:** The GUI should store all data in a consistent internal format (e.g., slope as `m/m`). When the `RorbVectorWriter` is called, it must convert the internal `m/m` slope value to `%` before writing it to the file. The `UrbsVectorWriter` can write it directly.

