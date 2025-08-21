Author: Lindsay Millard 21 Aug 2025
Purpose: To provide notes and roadmap for implementation of URBS plugin to work with pyromb

A conceptual bridge between how a visual, node-and-link based GUI (like one for RORB) would work and how to translate that structure into the sequential, command-based format of a URBS `.vec` file.

### The URBS Conceptual Model: "The Running Hydrograph"

Unlike RORB, which often defines the entire network structure first and then simulates, URBS builds its network sequentially. Think of the `.vec` file as a series of instructions for a single "running hydrograph" that flows through the catchment.

1.  **Start a Flow:** You begin at a headwater subcatchment. The `RAIN` command takes the rainfall, applies it to this subcatchment (using properties from the `.cat` file), and generates the initial "running hydrograph". This command also routes that hydrograph down its associated reach.
2.  **Add to the Flow:** As you move downstream, you encounter another subcatchment. The `ADD RAIN` command calculates the runoff from this new subcatchment, adds it to the "running hydrograph," and routes the *combined* flow down the next reach.
3.  **Handle Tributaries (Junctions):** When the main channel meets a tributary, you need to pause the main flow.
    *   `STORE` temporarily saves the "running hydrograph" of the main channel.
    *   You then define the entire tributary from its headwaters down to the junction using a new set of `RAIN` and `ADD RAIN` commands.
    *   `GET` retrieves the saved main channel hydrograph and adds the now-complete tributary hydrograph to it. The "running hydrograph" is now the combined flow downstream of the junction.
4.  **Route without Local Inflow:** Sometimes you have a long river reach with no significant local inflow. The `ROUTE` command simply takes the current "running hydrograph" and routes it through this reach. The `ROUTE THRU #i` syntax is powerful here, as it tells URBS to use the physical characteristics (like slope or roughness) of subcatchment `#i` for this routing reach.
5.  **Define Output:** The `PRINT` command tells URBS, "At this point in the sequence, write the current state of the 'running hydrograph' to an output file." This is how you define an output node.

### Translating a Visual GUI to a URBS `.vec` File

Here is the logic and pseudo-code for translating a graphical network of nodes and links from your GUI into the sequential URBS command file. The core of this logic is a **depth-first traversal** of the stream network tree.

#### GUI Elements:

*   **Subcatchment Object:** Has properties like `Index`, `Name`, `Area`, `UrbanFraction`, etc. This data populates the `.cat` file.
*   **Reach Object (Link):** Connects two nodes. Has properties like `Length`, and is associated with one `Subcatchment Object` for its physical characteristics.
*   **Node Object (Junction):** A point where reaches connect. Can be designated as an "Output Point".

#### Pseudo-code for Generating the `.vec` file:

The main idea is a recursive function that traverses each branch of the river network from top to bottom.

```python
# --- Main Function to Start the Process ---
def generate_urbs_model_files(network_data, output_path):
    # 1. Generate the .cat file (the easy part)
    generate_cat_file(network_data.subcatchments, output_path)

    # 2. Generate the .vec file
    vec_file = open(output_path + ".vec", "w")

    # Write header commands (MODEL, USES, CATCHMENT DATA FILE, etc.)
    write_headers(vec_file, network_data.global_parameters)

    # Find the main river channel's most upstream reach to start the traversal
    main_headwater_reach = find_main_headwater(network_data)

    # Start the recursive traversal
    traverse_and_write_branch(main_headwater_reach, vec_file)

    # Write the final command
    vec_file.write("END OF CATCHMENT DATA.\n")
    vec_file.close()


# --- Recursive Traversal Function ---
def traverse_and_write_branch(current_reach, vec_file):
    # This function processes a single branch of the river until it ends or hits a major junction

    # Process the first reach in this branch
    subcatchment = current_reach.associated_subcatchment
    
    # Use RAIN for the very first subcatchment of any branch
    vec_file.write(f"RAIN #{subcatchment.index} L={current_reach.length}\n")

    # If this node is an output point, print the results after this first reach
    if current_reach.start_node.is_output_point:
        vec_file.write(f"PRINT. {current_reach.start_node.name}\n")
        
    # --- Loop through the rest of the reaches in this branch ---
    while current_reach.end_node is not None:
        downstream_node = current_reach.end_node
        
        # Check for tributaries joining at the downstream node
        tributaries = find_tributaries(downstream_node)
        for tributary_reach in tributaries:
            vec_file.write("STORE.\n")
            # --- RECURSIVE CALL for the tributary branch ---
            traverse_and_write_branch(tributary_reach, vec_file)
            vec_file.write("GET.\n")

        # Get the next reach continuing down the current branch
        next_reach_in_branch = find_main_outgoing_reach(downstream_node)

        if next_reach_in_branch is not None:
            # This reach has a local subcatchment, so use ADD RAIN
            next_subcatchment = next_reach_in_branch.associated_subcatchment
            vec_file.write(f"ADD RAIN #{next_subcatchment.index} L={next_reach_in_branch.length}\n")
            current_reach = next_reach_in_branch
        else:
            # End of this branch
            current_reach = None 

        # If the downstream node is an output point, write a PRINT command
        if downstream_node.is_output_point:
            vec_file.write(f"PRINT. {downstream_node.name}\n")

```

### Key Instructions for GUI Development:

1.  **Network Traversal is Key:**  GUI's primary job when writing the `.vec` file is to correctly traverse the user-drawn network. It must identify the main channel and tributaries to correctly order the commands.
2.  **`STORE`/`GET` for Junctions:** Every time traversal algorithm encounters a junction with a tributary, it must write a `STORE`, then call the traversal function for the tributary, and then write a `GET`.
3.  **`RAIN` vs. `ADD RAIN`:** `RAIN` is the command to *start* a hydrograph at the top of a branch. `ADD RAIN` is for every subsequent subcatchment that adds flow to that same branch. Your code must distinguish between the headwater reach of a branch and subsequent reaches.
4.  **Link `Reach` to `Subcatchment`:** In GUI's data structure, every `Reach` object should be linked to a `Subcatchment` object. This is because URBS routing commands (`RAIN`, `ADD RAIN`, `ROUTE`) need the physical properties of a subcatchment to function. This is how the `.vec` file knows which parameters from the `.cat` file to use for routing.
5.  **Generate `.cat` File First:** Create a simple function that iterates through all `Subcatchment` objects in your GUI and writes their properties line-by-line into a CSV file. This is straightforward. The `Index` you write to this file is the same one you'll use in the `.vec` file (`RAIN #1`, `ADD RAIN #2`, etc.).

