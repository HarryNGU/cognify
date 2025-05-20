import os
import json
import logging
import networkx as nx
from collections import defaultdict

logger = logging.getLogger(__name__)

class KnowledgeMapper:
    """Generate knowledge maps from extracted concepts and relationships"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def generate_knowledge_map(self, extracted_knowledge):
        """
        Generate a knowledge map from extracted knowledge
        
        Args:
            extracted_knowledge: Dict containing concepts, relationships, hierarchy, and clusters
            
        Returns:
            dict: Knowledge map structure for visualization
        """
        concepts = extracted_knowledge.get('concepts', [])
        relationships = extracted_knowledge.get('relationships', [])
        hierarchy = extracted_knowledge.get('hierarchy', {})
        clusters = extracted_knowledge.get('clusters', [])
        
        if not concepts:
            return {
                'nodes': [],
                'links': [],
                'clusters': [],
                'hierarchy': {},
                'metadata': {
                    'total_nodes': 0,
                    'total_links': 0,
                    'total_clusters': 0
                }
            }
        
        # Create graph representation
        G = nx.Graph()
        
        # Add concepts as nodes
        for concept in concepts:
            G.add_node(
                concept['text'],
                type=concept.get('type', 'concept'),
                importance=concept.get('importance', 0.5),
                frequency=concept.get('frequency', 1)
            )
        
        # Add relationships as edges
        for rel in relationships:
            G.add_edge(
                rel['source'],
                rel['target'],
                weight=rel.get('weight', 1),
                type=rel.get('type', 'related'),
                subtypes=rel.get('subtypes', [])
            )
        
        # Calculate node positions using force-directed layout
        try:
            # Use networkx's spring layout
            positions = nx.spring_layout(G, k=0.3, iterations=50)
        except Exception as e:
            self.logger.error(f"Error calculating node positions: {str(e)}")
            # Fallback to random positions
            positions = {node: [random.random(), random.random()] for node in G.nodes()}
        
        # Normalize positions to 0-1 range
        min_x = min(pos[0] for pos in positions.values())
        max_x = max(pos[0] for pos in positions.values())
        min_y = min(pos[1] for pos in positions.values())
        max_y = max(pos[1] for pos in positions.values())
        
        x_range = max_x - min_x if max_x > min_x else 1
        y_range = max_y - min_y if max_y > min_y else 1
        
        normalized_positions = {}
        for node, pos in positions.items():
            normalized_positions[node] = [
                (pos[0] - min_x) / x_range,
                (pos[1] - min_y) / y_range
            ]
        
        # Calculate node sizes based on importance
        node_sizes = {}
        importance_values = [G.nodes[node]['importance'] for node in G.nodes()]
        min_importance = min(importance_values) if importance_values else 0
        max_importance = max(importance_values) if importance_values else 1
        importance_range = max_importance - min_importance if max_importance > min_importance else 1
        
        for node in G.nodes():
            importance = G.nodes[node]['importance']
            # Scale size from 5 to 20 based on importance
            node_sizes[node] = 5 + ((importance - min_importance) / importance_range) * 15
        
        # Prepare nodes for visualization
        nodes = []
        for node in G.nodes():
            node_data = G.nodes[node]
            nodes.append({
                'id': node,
                'label': node,
                'type': node_data.get('type', 'concept'),
                'importance': node_data.get('importance', 0.5),
                'frequency': node_data.get('frequency', 1),
                'x': normalized_positions[node][0],
                'y': normalized_positions[node][1],
                'size': node_sizes[node]
            })
        
        # Prepare links for visualization
        links = []
        for source, target, data in G.edges(data=True):
            links.append({
                'source': source,
                'target': target,
                'weight': data.get('weight', 1),
                'type': data.get('type', 'related'),
                'subtypes': data.get('subtypes', [])
            })
        
        # Prepare clusters for visualization
        cluster_data = []
        for cluster in clusters:
            # Calculate cluster center
            cluster_nodes = [n for n in nodes if n['id'] in cluster['concepts']]
            if cluster_nodes:
                x_coords = [n['x'] for n in cluster_nodes]
                y_coords = [n['y'] for n in cluster_nodes]
                center_x = sum(x_coords) / len(x_coords)
                center_y = sum(y_coords) / len(y_coords)
                
                cluster_data.append({
                    'id': cluster['id'],
                    'name': cluster.get('name', f"Cluster {cluster['id']}"),
                    'concepts': cluster['concepts'],
                    'center': [center_x, center_y],
                    'size': len(cluster['concepts'])
                })
        
        # Prepare hierarchy for visualization
        hierarchy_data = hierarchy
        
        # Create knowledge map
        knowledge_map = {
            'nodes': nodes,
            'links': links,
            'clusters': cluster_data,
            'hierarchy': hierarchy_data,
            'metadata': {
                'total_nodes': len(nodes),
                'total_links': len(links),
                'total_clusters': len(cluster_data)
            }
        }
        
        return knowledge_map
    
    def save_knowledge_map(self, knowledge_map, output_path):
        """Save knowledge map to JSON file"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(knowledge_map, f, indent=2)
        
        return output_path
