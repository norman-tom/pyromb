"""
Hydrological Analysis Module
This module provides tools for loading, analysing and visualising hydrological data from RORB outputs.

Example usage:
    # Create client with default configuration
    config = HydroConfig.default_config()
    client = HydroClient(config=config)
   
    # Load data
    client.load_data()
   
    # Analyze 1% AEP scenario
    fig_boxplot = client.plot_duration_boxplot('1p')
    fig_boxplot.savefig('peak_flows_boxplot.png')
   
    # Find and plot critical scenario
    fig_hydrograph, critical_data = client.plot_critical_hydrograph('1p', 36)
    fig_hydrograph.savefig('critical_hydrograph.png')
   
    # Print critical scenario details
    print("Critical Scenario Details:")
    print(f"Peak Flow: {critical_data['peak_flow']:.2f} m³/s")
    print(f"Duration: {critical_data['duration']} hours")
    print(f"Temporal Pattern: {critical_data['temporal_pattern']}")
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass

import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure


@dataclass
class Config:
    """Configuration parameters for hydrological analysis."""
    base_path: str
    run_prefix: str
    aep_values: List[str]
    durations: List[str]
    temporal_patterns: List[int]
    focus_node: str
    plot_style: str = 'ggplot'
    time_threshold: float = 36.0
    
    @classmethod
    def default_config(cls, base_path: str = './output/') -> 'Config':
        """Create a default configuration."""
        return cls(
            base_path=base_path,
            run_prefix='24013_predev_catchment_ ',
            aep_values=['10', '5', '2', '1', '0.05'],
            durations=['2', '3', '4_5', '6', '9', '12', '18', '24', '36', '48'],
            temporal_patterns=list(range(1, 11)),
            focus_node='Calculated hydrograph:',
            plot_style='ggplot',
            time_threshold=36.0
        )
    
    def __repr__(self):
        return (
            f"HydroConfig(\nbase_path={self.base_path}\n"
            f"run_prefix={self.run_prefix}\n"
            f"aep_values={self.aep_values}\n"
            f"durations={self.durations}\n"
            f"temporal_patterns={self.temporal_patterns}\n"
            f"focus_node={self.focus_node}\n"
            f"plot_style={self.plot_style}\n"
            f"time_threshold={self.time_threshold})"
        )


class ResultLoader:
    """Handles loading and processing of hydrological data files."""
    
    def __init__(self, config: Config):
        self.config = config
        
    def _format_aep(self, aep_value: str) -> str:
        """Format AEP value for file paths."""
        match aep_value:
            case '0.05':
                return 'aep1in2000'
            case '0.1':
                return 'aep1in1000'
            case '0.2':
                return 'aep1in500'
            case '0.5':
                return 'aep1in200'
            case _:
                return f"aep{aep_value}"

    def _format_duration(self, duration: str) -> str:
        """Format duration value for file paths."""
        return f"du{duration}hour"
    
    def _format_file_path(self, aep: str, duration: str, tp: int) -> str:
        """Create the full file path for a specific scenario."""
        return f"{self.config.base_path}{self.config.run_prefix}{aep}_{duration}tp{tp}.csv"
    
    def load_ensemble(self, aep: str, duration: str, 
                                   temporal_patterns: Optional[List[int]] = None,
                                   ) -> pd.DataFrame:
        """
        Load and join data for a specific AEP and duration across multiple temporal patterns.
        
        Args:
            aep: Annual exceedance probability value
            duration: Storm duration
            temporal_patterns: List of temporal pattern indices to load (defaults to config value)
            
        Returns:
            DataFrame with time and flow data for each temporal pattern
        """
        if temporal_patterns is None:
            temporal_patterns = self.config.temporal_patterns.copy()
        
        formatted_aep = self._format_aep(aep)
        formatted_duration = self._format_duration(duration)
        
        # Try up to 10 times with different TP ranges (handling RORB inconsistency)
        for _ in range(10):
            try:
                dfs = [pd.read_csv( # type: ignore
                    self._format_file_path(formatted_aep, formatted_duration, tp), 
                    header=2
                ) for tp in temporal_patterns]
                
                # Keep only relevant columns
                for df in dfs:
                    df.drop(columns=[col for col in df.columns if col not in 
                                    ['Inc', 'Time (hrs)', self.config.focus_node]], 
                            inplace=True)
                break
            except FileNotFoundError:
                # Handle inconsistent TP numbering in RORB output
                temporal_patterns = [t + 10 for t in temporal_patterns]
        else:
            raise FileNotFoundError("Files not found after 10 attempts")
        
        # Process and join dataframes
        for i, df in enumerate(dfs):
            if i == 0:
                df.drop(columns=['Inc'], inplace=True)
            else:
                df.drop(columns=['Inc', 'Time (hrs)'], inplace=True)
        
        # Combine all temporal patterns into one dataframe   
        result_df = pd.concat(dfs, axis=1)
        result_df.columns = ['time'] + [f'Q_tp{i}' for i in range(1, len(temporal_patterns) + 1)]
        
        return result_df
        
    def load_all_scenarios(self) -> Dict[str, List[pd.DataFrame]]:
        """
        Load all scenarios based on config settings.
        
        Returns:
            Dictionary with AEP as keys and lists of dataframes for each duration as values
        """
        result: dict[str, list[pd.DataFrame]] = {}
        
        for aep_value in self.config.aep_values:
            key = f"{aep_value}p"  # Format as '10p', '5p', etc.
            result[key] = []
            
            for duration in self.config.durations:
                df = self.load_ensemble(aep_value, duration)
                result[key].append(df)
                
        return result


class ResultProcessor:
    """Analyzes hydrological data for peak flows and critical scenarios."""
    
    def __init__(self, data: Dict[str, List[pd.DataFrame]], config: Config):
        self.data = data
        self.config = config
        self.results_cache: dict[str, pd.DataFrame] = {}  # Store calculated results for reuse
        
    def get_formatted_durations(self) -> List[str]:
        """Get formatted duration strings for display."""
        return [d.replace('du', '').replace('hour', '').replace('_', '.') 
                for d in [f"du{d}hour" for d in self.config.durations]]
    
    def calculate_peak_flows(self, aep: str) -> pd.DataFrame:
        """
        Calculate peak flows across all durations for a given AEP.
        
        Args:
            aep: Annual exceedance probability key (e.g., '10p')
            
        Returns:
            DataFrame with peak flows for each duration and temporal pattern
        """
        # Use cached results if available
        if f"{aep}_peaks" in self.results_cache:
            return self.results_cache[f"{aep}_peaks"]
            
        durations = [f"du{d}hour" for d in self.config.durations]
        to_join = [self.data[aep][i].max(axis=0).drop('time') for i in range(len(durations))] #type: ignore
        result_df = pd.DataFrame(to_join).T
        result_df.columns = self.get_formatted_durations()
        
        # Cache results
        self.results_cache[f"{aep}_peaks"] = result_df
        return result_df
    
    def find_critical_scenario(self, aep: str, time_threshold: Optional[float] = None) -> Dict[str, Any]:
        """
        Find the critical storm scenario closest to the median peak flow.
        
        Args:
            aep: Annual exceedance probability key (e.g., '10p')
            time_threshold: Maximum time to consider (hours)
            
        Returns:
            Dictionary with critical scenario details
        """
        if time_threshold is None:
            time_threshold = self.config.time_threshold
            
        # Get peak flows if not already calculated
        peak_flows = self.calculate_peak_flows(aep)
        
        # Find duration with highest median flow
        median_flows = peak_flows.median(axis=0)
        critical_duration = median_flows.idxmax()
        max_median_flow = median_flows[critical_duration]
        
        # Get full duration index and corresponding dataframe
        duration_index = self.config.durations.index(critical_duration.replace('.', '_'))
        duration_df = self.data[aep][duration_index]
        
        # Filter by time threshold and find closest temporal pattern to median
        filtered_df = duration_df[duration_df['time'] <= time_threshold]
        flow_columns = [col for col in filtered_df.columns if col != 'time']
        max_flows = filtered_df[flow_columns].max(axis=0)
        
        # Find temporal pattern closest to median peak flow
        closest_tp = (max_flows - max_median_flow).abs().idxmin()
        critical_flow = max_flows[closest_tp]
        
        # Create result dictionary
        result = {
            'peak_flow': float(critical_flow),
            'temporal_pattern': closest_tp,
            'duration': critical_duration,
            'hydrograph': filtered_df[['time', closest_tp]].rename(columns={closest_tp: 'flow'}),
            'median_flow': max_median_flow
        }
        
        return result


class ResultVisualizer:
    """Visualizes hydrological data and analysis results."""
    
    def __init__(self, config: Config):
        self.config = config
        
    def set_style(self, style: Optional[str] = None):
        """Set the plotting style."""
        plt.style.use(style or self.config.plot_style)

    def plot_boxplot(self, peak_flows: pd.DataFrame, aep: str, climate_year: str, title: str,) -> Figure:
        """
        Create a boxplot of peak flows across durations.
        Create a boxplot of peak flows across durations.
        
        Args:
            peak_flows: DataFrame with peak flows
            aep: AEP value for title
            climate_year: Climate year for title
            title: Title for the plot
            
        Returns:
            Matplotlib figure
        """
        self.set_style()
        fig, ax = plt.subplots(figsize=(12, 5))
        
        # Format AEP for display (remove 'p' and add '%')
        display_aep = aep[:-1] if aep.endswith('p') else aep
        
        ax.set_title(f"{title} - {display_aep}% AEP - {climate_year} Climate Year")
        peak_flows.boxplot(ax=ax, showfliers=False)
        
        ax.set_xlabel('Duration (hours)')
        ax.set_ylabel('Q (m³/s)')
        
        return fig
    
    def plot_critical_hydrograph(self, 
                                critical_data: Dict[str, Any], 
                                climate_year: str, 
                                title: str) -> Figure:
        """
        Plot the critical storm hydrograph.
        Plot the critical storm hydrograph.
        
        Args:
            critical_data: Critical scenario data from HydroAnalyzer
            climate_year: Climate year for title
            title: Title for the plot
            
        Returns:
            Matplotlib figure
        """
        self.set_style('bmh')  # Use bmh style for hydrograph plots
        
        # Extract data
        hydrograph = critical_data['hydrograph']
        duration = critical_data['duration']
        tp = critical_data['temporal_pattern']
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))
        
        ax.plot(hydrograph['time'], hydrograph['flow'])
        
        # Set labels
        ax.set_title(f"{title} - {duration} hours - {tp} - {climate_year} Climate Year")
        ax.set_xlabel('Time (hours)')
        ax.set_ylabel('Q (m³/s)')
        ax.grid(True)
        
        return fig


class ResultReporter:
    """Client interface for hydrological analysis and visualization."""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the hydrological analysis client.
        
        Args:
            config: Configuration parameters (optional, uses defaults if not provided)
        """
        self.config = config or Config.default_config()
        self.loader = ResultLoader(self.config)
        self.data = None
        self.analyzer = None
        self.visualizer = ResultVisualizer(self.config)
        
    def load_data(self) -> Dict[str, List[pd.DataFrame]]:
        """
        Load all hydrological data based on configuration.
        
        Returns:
            Dictionary of loaded data
        """
        self.data = self.loader.load_all_scenarios()
        self.analyzer = ResultProcessor(self.data, self.config)
        return self.data
    
    def get_peak_flows(self, aep: str) -> pd.DataFrame:
        """
        Get peak flows for a specific AEP.
        
        Args:
            aep: Annual exceedance probability (e.g., '1p')
            
        Returns:
            DataFrame with peak flows
        """
        if self.analyzer is None:
            raise ValueError("Data not loaded. Call load_data() first.")
            
        return self.analyzer.calculate_peak_flows(aep)
    
    def analyze_critical_scenario(self, aep: str, 
                                 time_threshold: Optional[float] = None) -> Dict[str, Any]:
        """
        Analyze and find the critical storm scenario.
        
        Args:
            aep: Annual exceedance probability (e.g., '1p')
            time_threshold: Maximum time to consider (hours)
            
        Returns:
            Dictionary with critical scenario details
        """
        if self.analyzer is None:
            raise ValueError("Data not loaded. Call load_data() first.")
            
        return self.analyzer.find_critical_scenario(aep, time_threshold)
    def plot_duration_boxplot(self, aep: str, climate_year: str, title: str) -> Figure:
        """
        Create a boxplot of flows across durations.
        Create a boxplot of flows across durations.
        
        Args:
            aep: Annual exceedance probability (e.g., '1p')
            climate_year: Climate year for title
            title: Title for the plot
            
        Returns:
            Matplotlib figure
        """
        peak_flows = self.get_peak_flows(aep)
        return self.visualizer.plot_boxplot(peak_flows, aep, climate_year, title)
    def plot_critical_hydrograph(self, 
                                aep: str, 
                                climate_year: str,
                                title: str,
                                time_threshold: Optional[float] = None) -> Figure:
        """
        Analyze and plot the critical storm hydrograph.
        Analyze and plot the critical storm hydrograph.
        
        Args:
            aep: Annual exceedance probability (e.g., '1p')
            climate_year: Climate year for title
            title: Title for the plot
            time_threshold: Maximum time to consider (hours)
            
        Returns:
            Tuple of (Figure, critical scenario data)
        """
        critical_data = self.analyze_critical_scenario(aep, time_threshold)
        fig = self.visualizer.plot_critical_hydrograph(critical_data, climate_year, title)
        return fig