from .model import Model
from ..core.traveller import Traveller
from ..core.attributes.basin import Basin
from ..core.attributes.confluence import Confluence
from ..core.attributes.reach import ReachType
import csv
from io import StringIO

class UrbsVectorWriter:
    """
    Writes URBS .vec file commands following proper URBS text-based command structure.
    Implements the traversal logic from URBS_logic.md and RORBvURBS_logic.md
    """

    def __init__(self, model_name: str = "URBS_Model") -> None:
        self._storedHydro: list[int] = []
        self._runningHydro: bool = False
        self._stateVector = []
        self._commandVector = []
        self._model_name = model_name
        self._subcatchment_index_map = {}  # Map positions to subcatchment indices
    
    def step(self, traveller: Traveller) -> None:
        """ 
        Calculate action to take at current step and generate URBS command.
        
        Parameters
        ----------
        traveller : Traveller
            The traveller for the catchment being built. 
        """
        self._state(traveller)
        if self._stateVector:
            self._control(self._stateVector[-1], traveller)
    
    def build_vec_file(self) -> str:
        """ 
        Builds the URBS .vec file content with proper header and commands.
            
        Returns
        -------
        str
            The complete .vec file content with header and commands
        """
        vec_content = f"{self._model_name}\n"
        vec_content += "MODEL: SPLIT\n"
        vec_content += "USES: L CS U\n"
        vec_content += "DEFAULT PARAMETERS: alpha = 0.5 m = 0.8 beta = 3 n = 1.0 x = 0.25\n"
        vec_content += f"CATCHMENT DATA FILE = {self._model_name}.cat\n"
        
        for command in self._commandVector:
            vec_content += f"{command}\n"
        
        vec_content += "END OF CATCHMENT DATA.\n"
        return vec_content

    def _state(self, traveller: Traveller) -> None:
        """
        Store the current state of the traveller and determine URBS command.
        
        URBS Command Logic:
        - RAIN: Start hydrograph at headwater subcatchment
        - ADD RAIN: Add subcatchment inflow to running hydrograph
        - STORE: Save hydrograph at junction before processing tributary
        - GET: Retrieve stored hydrograph and combine with tributary flow
        - ROUTE: Route through reach without local inflow
        - PRINT: Output results at designated nodes
        
        Parameters
        ----------
        traveller : Traveller
            The traveller traversing this catchment.
        """
        i = traveller._pos
        up = traveller.top(i)
        
        if i == traveller._endSentinel:
            ret = (0, i)  # End of traversal
        elif (self._runningHydro == False) and (isinstance(traveller._catchment._vertices[i], Basin)):
            # Start of new branch - use RAIN command
            self._runningHydro = True
            traveller.next()
            ret = (1, i)  # RAIN
        elif (self._storedHydro) and (self._storedHydro[-1] == i) and (self._runningHydro):
            # Retrieve stored hydrograph - use GET command
            self._storedHydro.pop()
            ret = (4, i)  # GET
        elif (self._runningHydro) and (isinstance(traveller._catchment._vertices[i], Basin)) and (up == i):
            # Add subcatchment to running hydrograph - use ADD RAIN command
            traveller.next()
            ret = (2, i)  # ADD RAIN
        elif (self._runningHydro) and (up != i):
            # Junction with tributary - use STORE command
            self._storedHydro.append(i)
            self._runningHydro = False
            traveller.next()
            ret = (3, i)  # STORE
        elif (self._runningHydro) and (isinstance(traveller._catchment._vertices[i], Confluence)) and (up == i):
            # Route without local inflow - use ROUTE command
            traveller.next()
            ret = (5, i)  # ROUTE
        else:
            # Default case
            traveller.next()
            ret = (0, i)
        
        self._stateVector.append(ret)

    def _control(self, code: tuple, traveller: Traveller) -> None:
        """
        Generate URBS text commands based on traversal state.

        Parameters
        ----------
        code : tuple
            Command code tuple: [0] = command type, [1] = position
        traveller : Traveller
            The traveller traversing this catchment.
        """
        command_code, pos = code
        
        try:
            if command_code == 1:  # RAIN - Start branch at headwater
                self._generate_rain_command(pos, traveller)
                
            elif command_code == 2:  # ADD RAIN - Add subcatchment inflow
                self._generate_add_rain_command(pos, traveller)
                
            elif command_code == 3:  # STORE - Store hydrograph at junction
                self._commandVector.append("STORE.")
                
            elif command_code == 4:  # GET - Retrieve stored hydrograph
                self._commandVector.append("GET.")
                
            elif command_code == 5:  # ROUTE - Route without local inflow
                self._generate_route_command(pos, traveller)
                
            elif command_code == 7:  # PRINT - Output at node
                self._generate_print_command(pos, traveller)
                
        except Exception as e:
            # Fallback for errors
            self._commandVector.append(f"! Error generating command for code {command_code} at position {pos}: {str(e)}")

    def _generate_rain_command(self, pos: int, traveller: Traveller) -> None:
        """Generate RAIN command for headwater subcatchment."""
        basin = traveller._catchment._vertices[pos]
        reach = traveller.getReach(pos)
        
        # Get or create subcatchment index
        subcatchment_index = self._get_subcatchment_index(pos, basin)
        length_km = reach.length() / 1000
        
        command = f"RAIN #{subcatchment_index} L={length_km:.3f}"
        
        # Add slope parameter if available (URBS uses m/m, not %)
        if hasattr(reach, 'slope') and reach.slope is not None:
            slope_mm = reach.slope  # Assume internal format is m/m
            command += f" Sc={slope_mm:.6f}"
        
        self._commandVector.append(command)

    def _generate_add_rain_command(self, pos: int, traveller: Traveller) -> None:
        """Generate ADD RAIN command for subcatchment."""
        basin = traveller._catchment._vertices[pos]
        reach = traveller.getReach(pos)
        
        # Get or create subcatchment index
        subcatchment_index = self._get_subcatchment_index(pos, basin)
        length_km = reach.length() / 1000
        
        command = f"ADD RAIN #{subcatchment_index} L={length_km:.3f}"
        
        # Add slope parameter if available (URBS uses m/m, not %)
        if hasattr(reach, 'slope') and reach.slope is not None:
            slope_mm = reach.slope  # Assume internal format is m/m
            command += f" Sc={slope_mm:.6f}"
        
        self._commandVector.append(command)

    def _generate_route_command(self, pos: int, traveller: Traveller) -> None:
        """Generate ROUTE command for routing without local inflow."""
        reach = traveller.getReach(pos)
        
        # Use position as subcatchment reference for routing properties
        subcatchment_index = pos
        length_km = reach.length() / 1000
        
        command = f"ROUTE THRU #{subcatchment_index} L={length_km:.3f}"
        
        # Add slope parameter if available (URBS uses m/m, not %)
        if hasattr(reach, 'slope') and reach.slope is not None:
            slope_mm = reach.slope  # Assume internal format is m/m
            command += f" Sc={slope_mm:.6f}"
        
        self._commandVector.append(command)

    def _generate_print_command(self, pos: int, traveller: Traveller) -> None:
        """Generate PRINT command for output nodes."""
        node = traveller.getNode(pos)
        node_name = node.name if hasattr(node, 'name') else f"Node_{pos}"
        self._commandVector.append(f"PRINT. {node_name}")

    def _get_subcatchment_index(self, pos: int, basin: Basin) -> int:
        """Get or create subcatchment index for basin."""
        if pos not in self._subcatchment_index_map:
            # Use basin index if available, otherwise use position
            if hasattr(basin, 'index') and basin.index is not None:
                self._subcatchment_index_map[pos] = basin.index
            else:
                # Create sequential index
                self._subcatchment_index_map[pos] = len(self._subcatchment_index_map) + 1
        
        return self._subcatchment_index_map[pos]


class UrbsCatWriter:
    """
    Writes URBS .cat file containing subcatchment data in CSV format.
    """
    
    def __init__(self) -> None:
        pass
    
    def build_cat_file(self, traveller: Traveller, subcatchment_index_map: dict = None) -> str:
        """
        Generate URBS .cat file content with subcatchment data.
        
        Parameters
        ----------
        traveller : Traveller
            The traveller that traversed the catchment.
        subcatchment_index_map : dict
            Mapping of positions to subcatchment indices
            
        Returns
        -------
        str
            The complete .cat file content in CSV format
        """
        csv_output = StringIO()
        writer = csv.writer(csv_output)
        
        # Write header - URBS .cat file format
        writer.writerow(['Index', 'Name', 'Area', 'Imperviousness', 'IL', 'CL'])
        
        # Extract and write subcatchment data
        subcatchments = self._extract_subcatchments(traveller)
        
        for subcatchment in subcatchments:
            pos = subcatchment['position']
            basin = subcatchment['basin']
            
            # Get index from mapping or use sequential
            if subcatchment_index_map and pos in subcatchment_index_map:
                index = subcatchment_index_map[pos]
            elif hasattr(basin, 'index') and basin.index is not None:
                index = basin.index
            else:
                index = pos
            
            name = basin.name if hasattr(basin, 'name') else f"Sub_{index}"
            area = basin.area if hasattr(basin, 'area') else 0.0
            imperviousness = basin.fi if hasattr(basin, 'fi') else 0.0
            il = basin.il if hasattr(basin, 'il') else 0.0  # Initial Loss
            cl = basin.cl if hasattr(basin, 'cl') else 2.5  # Continuing Loss (default)
            
            writer.writerow([index, name, area, imperviousness, il, cl])
        
        return csv_output.getvalue()
    
    def _extract_subcatchments(self, traveller: Traveller) -> list:
        """Extract all basin subcatchments from the catchment."""
        subcatchments = []
        
        for i, vertex in enumerate(traveller._catchment._vertices):
            if isinstance(vertex, Basin):
                subcatchments.append({
                    'position': i,
                    'basin': vertex
                })
        
        return subcatchments


class URBS(Model):
    """
    Create URBS model files for input to the URBS runoff routing model.
    
    This implementation follows the proper URBS approach as outlined in the documentation:
    - Generates separate .vec and .cat files
    - Uses text-based commands instead of numeric codes
    - Handles proper unit conversions (m/m for slope)
    - Implements depth-first traversal logic for URBS command generation
    """
    
    def __init__(self, model_name: str = "URBS_Model"):
        self.model_name = model_name
    
    def getVector(self, traveller: Traveller) -> str:
        """
        Generate URBS .vec file content.
        
        Parameters
        ----------
        traveller : Traveller
            The traveller for traversing the catchment.
            
        Returns
        -------
        str
            The .vec file content with URBS commands
        """
        # Initialize traveller
        traveller.next()
        
        # Create URBS vector writer
        vector_writer = UrbsVectorWriter(self.model_name)
        
        # Traverse catchment and generate commands
        while traveller._pos != traveller._endSentinel:
            vector_writer.step(traveller)
        
        return vector_writer.build_vec_file()
    
    def getCatFile(self, traveller: Traveller) -> str:
        """
        Generate URBS .cat file content.
        
        Parameters
        ----------
        traveller : Traveller
            The traveller for traversing the catchment.
            
        Returns
        -------
        str
            The .cat file content with subcatchment data
        """
        cat_writer = UrbsCatWriter()
        return cat_writer.build_cat_file(traveller)
    
    def getFiles(self, traveller: Traveller) -> tuple[str, str]:
        """
        Generate both URBS .vec and .cat file contents.
        
        Parameters
        ----------
        traveller : Traveller
            The traveller for traversing the catchment.
            
        Returns
        -------
        tuple[str, str]
            A tuple containing (.vec content, .cat content)
        """
        # Reset traveller to start
        original_pos = traveller._pos
        traveller._pos = 0
        traveller.next()
        
        # Create writers
        vector_writer = UrbsVectorWriter(self.model_name)
        
        # Traverse catchment and generate commands
        while traveller._pos != traveller._endSentinel:
            vector_writer.step(traveller)
        
        # Generate files
        vec_content = vector_writer.build_vec_file()
        
        # Reset for cat file generation
        traveller._pos = original_pos
        cat_content = self.getCatFile(traveller)
        
        return vec_content, cat_content
