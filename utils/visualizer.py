import networkx as nx
import matplotlib.pyplot as plt
import io
import base64
from typing import Dict, List, Set, Tuple
import os

class DependencyVisualizer:
    """Visualize codebase dependencies as interactive graphs."""
    
    def __init__(self, indexer):
        """
        Initialize the visualizer with an indexer.
        
        Args:
            indexer: An instance of CodebaseIndexer with indexed codebase
        """
        self.indexer = indexer
    
    def generate_dependency_graph(self, central_file: str) -> str:
        """
        Generate an HTML representation of a dependency graph centered on a file.
        
        Args:
            central_file: The file path to center the graph on
            
        Returns:
            HTML string with the dependency visualization
        """
        # Create a directed graph
        G = nx.DiGraph()
        
        # Set to keep track of files we've processed
        processed_files = set()
        
        # Files to process
        files_to_process = {central_file}
        
        # Track dependency depth (limit to 2 levels)
        max_depth = 2
        depth = 0
        
        while files_to_process and depth < max_depth:
            next_level = set()
            
            for file_path in files_to_process:
                if file_path in processed_files:
                    continue
                    
                # Mark as processed
                processed_files.add(file_path)
                
                # Add node for this file
                file_name = os.path.basename(file_path)
                G.add_node(file_path, label=file_name)
                
                # Add dependency edges
                if file_path in self.indexer.dependencies:
                    for dep in self.indexer.dependencies[file_path]:
                        # Add edge from file to dependency
                        G.add_edge(file_path, dep)
                        next_level.add(dep)
                
                # Add dependent edges (files that include this file)
                for dep_file, deps in self.indexer.dependencies.items():
                    if file_path in deps:
                        # Add edge from dependent to file
                        G.add_edge(dep_file, file_path)
                        next_level.add(dep_file)
            
            # Move to next level
            files_to_process = next_level - processed_files
            depth += 1
        
        # Limit graph size for clarity (max 20 nodes)
        if len(G.nodes) > 20:
            # Keep central file and most important nodes
            central_neighbors = list(nx.neighbors(G, central_file))
            important_nodes = [central_file] + central_neighbors[:19]
            
            # Create a subgraph with only the important nodes
            G = G.subgraph(important_nodes)
        
        # Generate graph visualization using D3.js
        return self._generate_d3_graph(G, central_file)
    
    def _generate_d3_graph(self, G: nx.DiGraph, central_file: str) -> str:
        """Generate interactive D3.js graph visualization."""
        # Convert graph to JSON-compatible format
        nodes = []
        for node in G.nodes:
            nodes.append({
                "id": node,
                "name": os.path.basename(node),
                "group": 1 if node == central_file else 2
            })
            
        links = []
        for source, target in G.edges:
            links.append({
                "source": source,
                "target": target,
                "value": 1
            })
            
        # Generate HTML with embedded D3.js visualization
        html = '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <script src="https://d3js.org/d3.v5.min.js"></script>
            <style>
                .links line {
                    stroke: #999;
                    stroke-opacity: 0.6;
                    stroke-width: 1.5px;
                    marker-end: url(#arrow);
                }
                
                .nodes circle {
                    stroke: #fff;
                    stroke-width: 1.5px;
                }
                
                .node-labels {
                    font-family: sans-serif;
                    font-size: 10px;
                }
                
                .node-central {
                    fill: #d62728;
                }
                
                .node-dependency {
                    fill: #1f77b4;
                }
                
                .node-dependent {
                    fill: #2ca02c;
                }
            </style>
        </head>
        <body>
            <svg width="100%" height="400"></svg>
            <script>
                const data = {
                    "nodes": ''' + str(nodes).replace("'", '"') + ''',
                    "links": ''' + str(links).replace("'", '"') + '''
                };
                
                // Replace single quotes with double quotes
                const jsonData = JSON.parse(JSON.stringify(data).replace(/'/g, '"'));
                
                const svg = d3.select("svg"),
                    width = svg.node().getBoundingClientRect().width,
                    height = svg.node().getBoundingClientRect().height;
                
                // Add arrow markers
                svg.append("defs").append("marker")
                    .attr("id", "arrow")
                    .attr("viewBox", "0 -5 10 10")
                    .attr("refX", 15)
                    .attr("refY", 0)
                    .attr("markerWidth", 6)
                    .attr("markerHeight", 6)
                    .attr("orient", "auto")
                    .append("path")
                    .attr("d", "M0,-5L10,0L0,5")
                    .attr("fill", "#999");
                
                // Create simulation
                const simulation = d3.forceSimulation()
                    .force("link", d3.forceLink().id(d => d.id).distance(100))
                    .force("charge", d3.forceManyBody().strength(-200))
                    .force("center", d3.forceCenter(width / 2, height / 2));
                
                // Create links
                const link = svg.append("g")
                    .attr("class", "links")
                    .selectAll("line")
                    .data(jsonData.links)
                    .enter().append("line");
                
                // Create nodes
                const node = svg.append("g")
                    .attr("class", "nodes")
                    .selectAll("circle")
                    .data(jsonData.nodes)
                    .enter().append("circle")
                    .attr("r", 10)
                    .attr("class", d => {
                        if (d.id === "''' + central_file + '''") {
                            return "node-central";
                        } else {
                            // Check if this is a dependency or dependent
                            const isDependent = jsonData.links.some(link => 
                                link.source === d.id && link.target === "''' + central_file + '''");
                            return isDependent ? "node-dependent" : "node-dependency";
                        }
                    })
                    .call(d3.drag()
                        .on("start", dragstarted)
                        .on("drag", dragged)
                        .on("end", dragended));
                
                // Add labels
                const label = svg.append("g")
                    .attr("class", "node-labels")
                    .selectAll("text")
                    .data(jsonData.nodes)
                    .enter().append("text")
                    .text(d => d.name)
                    .attr("x", 12)
                    .attr("y", 3);
                
                // Add tooltips
                node.append("title")
                    .text(d => d.id);
                
                // Update positions on simulation tick
                simulation
                    .nodes(jsonData.nodes)
                    .on("tick", ticked);
                
                simulation.force("link")
                    .links(jsonData.links);
                
                function ticked() {
                    link
                        .attr("x1", d => d.source.x)
                        .attr("y1", d => d.source.y)
                        .attr("x2", d => d.target.x)
                        .attr("y2", d => d.target.y);
                
                    node
                        .attr("cx", d => d.x)
                        .attr("cy", d => d.y);
                
                    label
                        .attr("x", d => d.x + 12)
                        .attr("y", d => d.y + 3);
                }
                
                function dragstarted(d) {
                    if (!d3.event.active) simulation.alphaTarget(0.3).restart();
                    d.fx = d.x;
                    d.fy = d.y;
                }
                
                function dragged(d) {
                    d.fx = d3.event.x;
                    d.fy = d3.event.y;
                }
                
                function dragended(d) {
                    if (!d3.event.active) simulation.alphaTarget(0);
                    d.fx = null;
                    d.fy = null;
                }
            </script>
        </body>
        </html>
        '''
        
        return html
