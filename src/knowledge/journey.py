import os
import json
import logging
import random
from collections import defaultdict

logger = logging.getLogger(__name__)

class LearningJourneyGenerator:
    """Generate personalized learning journeys from knowledge maps"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def generate_journey(self, knowledge_map, start_concept, user_preferences=None):
        """
        Generate a personalized learning journey starting from a specific concept
        
        Args:
            knowledge_map: Dict containing the knowledge map structure
            start_concept: ID of the starting concept
            user_preferences: Dict containing user preferences for personalization
            
        Returns:
            dict: Learning journey structure
        """
        if not knowledge_map or not start_concept:
            return {
                'start_concept': start_concept,
                'path': [],
                'content': {},
                'metadata': {
                    'pattern_focus': 'medium',
                    'complexity': 'medium',
                    'journey_type': 'default'
                }
            }
        
        # Get nodes and links from knowledge map
        nodes = {node['id']: node for node in knowledge_map.get('nodes', [])}
        
        # Create a graph representation for path finding
        graph = defaultdict(list)
        for link in knowledge_map.get('links', []):
            source = link['source']
            target = link['target']
            weight = link.get('weight', 1)
            
            # Add bidirectional connections
            graph[source].append((target, weight))
            graph[target].append((source, weight))
        
        # Check if start concept exists
        if start_concept not in nodes:
            self.logger.error(f"Start concept {start_concept} not found in knowledge map")
            return {
                'start_concept': start_concept,
                'path': [],
                'content': {},
                'metadata': {
                    'pattern_focus': 'medium',
                    'complexity': 'medium',
                    'journey_type': 'default'
                }
            }
        
        # Determine journey type based on user preferences or concept properties
        journey_type = self._determine_journey_type(start_concept, nodes, user_preferences)
        
        # Generate path based on journey type
        if journey_type == 'pattern_based':
            path = self._generate_pattern_based_path(start_concept, nodes, graph, knowledge_map)
        elif journey_type == 'hierarchical':
            path = self._generate_hierarchical_path(start_concept, nodes, knowledge_map)
        elif journey_type == 'associative':
            path = self._generate_associative_path(start_concept, nodes, graph)
        else:  # default
            path = self._generate_default_path(start_concept, nodes, graph)
        
        # Generate content for each concept in the path
        content = {}
        for concept_id in path:
            content[concept_id] = self._generate_concept_content(concept_id, nodes, knowledge_map)
        
        # Determine pattern focus and complexity
        pattern_focus = self._determine_pattern_focus(path, knowledge_map)
        complexity = self._determine_complexity(path, nodes)
        
        return {
            'start_concept': start_concept,
            'path': path,
            'content': content,
            'metadata': {
                'pattern_focus': pattern_focus,
                'complexity': complexity,
                'journey_type': journey_type
            }
        }
    
    def _determine_journey_type(self, start_concept, nodes, user_preferences):
        """Determine the type of journey based on concept and preferences"""
        # Default journey types
        journey_types = ['pattern_based', 'hierarchical', 'associative']
        
        # If user preferences are provided, use them to influence the journey type
        if user_preferences:
            if user_preferences.get('preferred_journey_type') in journey_types:
                return user_preferences.get('preferred_journey_type')
            
            # Use cognitive style preferences
            if user_preferences.get('pattern_seeking_level') == 'high':
                return 'pattern_based'
            elif user_preferences.get('hierarchical_preference') == 'high':
                return 'hierarchical'
            elif user_preferences.get('associative_preference') == 'high':
                return 'associative'
        
        # If no preferences or not decisive, use concept properties
        concept = nodes.get(start_concept, {})
        concept_type = concept.get('type', '')
        
        if concept_type in ['noun_phrase', 'key_term']:
            return 'pattern_based'
        elif concept_type in ['ORG', 'PERSON', 'GPE']:
            return 'hierarchical'
        else:
            return 'associative'
    
    def _generate_pattern_based_path(self, start_concept, nodes, graph, knowledge_map):
        """Generate a path that emphasizes patterns and connections"""
        path = [start_concept]
        visited = set([start_concept])
        
        # Find clusters that contain the start concept
        start_clusters = []
        for cluster in knowledge_map.get('clusters', []):
            if start_concept in cluster.get('concepts', []):
                start_clusters.append(cluster)
        
        # If no clusters found, fall back to default path
        if not start_clusters:
            return self._generate_default_path(start_concept, nodes, graph)
        
        # Select a primary cluster
        primary_cluster = max(start_clusters, key=lambda c: c.get('size', 0))
        
        # Add concepts from the same cluster that have strong connections
        cluster_concepts = primary_cluster.get('concepts', [])
        
        # Sort cluster concepts by connection strength to start concept
        connected_concepts = []
        for concept in cluster_concepts:
            if concept != start_concept and concept in nodes:
                # Check direct connection strength
                connection_strength = 0
                for neighbor, weight in graph.get(start_concept, []):
                    if neighbor == concept:
                        connection_strength = weight
                        break
                
                connected_concepts.append((concept, connection_strength))
        
        # Sort by connection strength
        connected_concepts.sort(key=lambda x: x[1], reverse=True)
        
        # Add top connected concepts to path
        for concept, _ in connected_concepts[:3]:
            if concept not in visited:
                path.append(concept)
                visited.add(concept)
        
        # Find concepts from other clusters that form interesting patterns
        # Look for concepts that connect to multiple concepts in our path
        pattern_candidates = []
        for node_id in nodes:
            if node_id not in visited:
                connections_to_path = 0
                for path_concept in path:
                    for neighbor, _ in graph.get(path_concept, []):
                        if neighbor == node_id:
                            connections_to_path += 1
                            break
                
                if connections_to_path >= 2:
                    pattern_candidates.append((node_id, connections_to_path))
        
        # Sort by number of connections to path
        pattern_candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Add top pattern-forming concepts
        for concept, _ in pattern_candidates[:2]:
            if concept not in visited:
                path.append(concept)
                visited.add(concept)
        
        # Ensure we have a reasonable path length
        if len(path) < 5:
            # Add more concepts from the primary cluster
            for concept in cluster_concepts:
                if concept not in visited and len(path) < 5:
                    path.append(concept)
                    visited.add(concept)
        
        return path
    
    def _generate_hierarchical_path(self, start_concept, nodes, knowledge_map):
        """Generate a path that follows hierarchical relationships"""
        path = [start_concept]
        visited = set([start_concept])
        
        # Get hierarchy from knowledge map
        hierarchy = knowledge_map.get('hierarchy', {})
        tree = hierarchy.get('tree', {})
        
        # Check if start concept is a root
        if start_concept in hierarchy.get('roots', []):
            # Add children
            children = self._get_children_from_tree(start_concept, tree)
            for child in children[:4]:  # Limit to 4 children
                if child not in visited:
                    path.append(child)
                    visited.add(child)
        else:
            # Find parent
            parent = None
            for root in hierarchy.get('roots', []):
                if self._is_descendant(start_concept, root, tree):
                    parent = root
                    break
            
            # Add parent if found
            if parent and parent not in visited:
                path.insert(0, parent)  # Add parent at the beginning
                visited.add(parent)
            
            # Add siblings (concepts with the same parent)
            siblings = []
            if parent:
                siblings = self._get_children_from_tree(parent, tree)
            
            for sibling in siblings:
                if sibling != start_concept and sibling not in visited and len(path) < 4:
                    path.append(sibling)
                    visited.add(sibling)
            
            # Add children
            children = self._get_children_from_tree(start_concept, tree)
            for child in children:
                if child not in visited and len(path) < 6:
                    path.append(child)
                    visited.add(child)
        
        # If path is still too short, add some related concepts
        if len(path) < 5:
            # Find concepts with similar importance
            start_importance = nodes.get(start_concept, {}).get('importance', 0.5)
            similar_concepts = []
            
            for node_id, node in nodes.items():
                if node_id not in visited:
                    importance_diff = abs(node.get('importance', 0) - start_importance)
                    if importance_diff < 0.2:  # Similar importance
                        similar_concepts.append(node_id)
            
            # Add some similar concepts
            for concept in random.sample(similar_concepts, min(3, len(similar_concepts))):
                if len(path) < 5:
                    path.append(concept)
                    visited.add(concept)
        
        return path
    
    def _generate_associative_path(self, start_concept, nodes, graph):
        """Generate a path that follows associative relationships"""
        path = [start_concept]
        visited = set([start_concept])
        
        # Current concept to explore from
        current = start_concept
        
        # Add concepts through associative jumps
        for _ in range(5):  # Aim for a path of about 6 concepts
            # Get neighbors
            neighbors = graph.get(current, [])
            
            if not neighbors:
                break
            
            # Sort by weight
            neighbors.sort(key=lambda x: x[1], reverse=True)
            
            # Find an unvisited neighbor
            next_concept = None
            for neighbor, _ in neighbors:
                if neighbor not in visited:
                    next_concept = neighbor
                    break
            
            if not next_concept:
                # If all neighbors visited, try a random jump to an unvisited concept
                unvisited = [n for n in nodes if n not in visited]
                if unvisited:
                    next_concept = random.choice(unvisited)
            
            if next_concept:
                path.append(next_concept)
                visited.add(next_concept)
                current = next_concept
            else:
                break
        
        return path
    
    def _generate_default_path(self, start_concept, nodes, graph):
        """Generate a default path when other methods are not applicable"""
        path = [start_concept]
        visited = set([start_concept])
        
        # Add directly connected concepts first
        neighbors = graph.get(start_concept, [])
        neighbors.sort(key=lambda x: x[1], reverse=True)  # Sort by weight
        
        for neighbor, _ in neighbors[:3]:  # Add up to 3 direct neighbors
            if neighbor not in visited:
                path.append(neighbor)
                visited.add(neighbor)
        
        # If we need more concepts, add some with similar importance
        if len(path) < 5:
            start_importance = nodes.get(start_concept, {}).get('importance', 0.5)
            similar_concepts = []
            
            for node_id, node in nodes.items():
                if node_id not in visited:
                    importance_diff = abs(node.get('importance', 0) - start_importance)
                    if importance_diff < 0.2:  # Similar importance
                        similar_concepts.append(node_id)
            
            # Add some similar concepts
            for concept in random.sample(similar_concepts, min(3, len(similar_concepts))):
                if len(path) < 5:
                    path.append(concept)
                    visited.add(concept)
        
        return path
    
    def _generate_concept_content(self, concept_id, nodes, knowledge_map):
        """Generate content for a concept in the learning journey"""
        node = nodes.get(concept_id, {})
        
        # In a real implementation, this would generate or retrieve actual content
        # For this prototype, we'll create placeholder content
        
        # Find related concepts
        related_concepts = []
        for link in knowledge_map.get('links', []):
            if link['source'] == concept_id and link['target'] != concept_id:
                related_concepts.append({
                    'id': link['target'],
                    'relationship_type': link.get('type', 'related'),
                    'strength': link.get('weight', 1)
                })
            elif link['target'] == concept_id and link['source'] != concept_id:
                related_concepts.append({
                    'id': link['source'],
                    'relationship_type': link.get('type', 'related'),
                    'strength': link.get('weight', 1)
                })
        
        # Sort by relationship strength
        related_concepts.sort(key=lambda x: x['strength'], reverse=True)
        
        # Find the cluster this concept belongs to
        concept_cluster = None
        for cluster in knowledge_map.get('clusters', []):
            if concept_id in cluster.get('concepts', []):
                concept_cluster = cluster.get('name', '')
                break
        
        # Generate content structure
        content = {
            'title': node.get('label', concept_id),
            'type': node.get('type', 'concept'),
            'importance': node.get('importance', 0.5),
            'description': f"This is a detailed explanation of the concept '{node.get('label', concept_id)}'. In a full implementation, this would contain comprehensive information about the concept.",
            'pattern_insights': [
                "This concept forms part of a larger pattern in the knowledge domain.",
                f"It belongs to the cluster '{concept_cluster}' which represents a key area of knowledge.",
                "Understanding this concept helps reveal connections between seemingly disparate ideas."
            ],
            'examples': [
                "Example 1: Application in a real-world context",
                "Example 2: Illustration of the concept in practice",
                "Example 3: Case study demonstrating the concept's importance"
            ],
            'related_concepts': related_concepts[:5],  # Limit to top 5
            'visual_elements': [
                {
                    'type': 'diagram',
                    'description': "Conceptual diagram showing relationships to other concepts"
                },
                {
                    'type': 'image',
                    'description': "Visual representation of the concept"
                }
            ],
            'learning_activities': [
                {
                    'type': 'pattern_recognition',
                    'description': "Identify patterns related to this concept in different contexts"
                },
                {
                    'type': 'connection_mapping',
                    'description': "Map connections between this concept and previously learned concepts"
                },
                {
                    'type': 'application',
                    'description': "Apply this concept to solve a novel problem"
                }
            ]
        }
        
        return content
    
    def _determine_pattern_focus(self, path, knowledge_map):
        """Determine the pattern focus level of the journey"""
        # Count how many concepts in the path belong to the same cluster
        clusters = knowledge_map.get('clusters', [])
        
        # Count concepts per cluster
        cluster_counts = defaultdict(int)
        for cluster in clusters:
            cluster_id = cluster.get('id', '')
            for concept in path:
                if concept in cluster.get('concepts', []):
                    cluster_counts[cluster_id] += 1
        
        # If most concepts are from the same cluster, high pattern focus
        if cluster_counts and max(cluster_counts.values()) >= len(path) * 0.7:
            return 'high'
        # If concepts are from 2-3 clusters in balanced way, medium pattern focus
        elif len(cluster_counts) <= 3 and len(cluster_counts) > 0:
            return 'medium'
        # If concepts are scattered across many clusters, low pattern focus
        else:
            return 'low'
    
    def _determine_complexity(self, path, nodes):
        """Determine the complexity level of the journey"""
        # Use average importance as a proxy for complexity
        importances = [nodes.get(concept, {}).get('importance', 0.5) for concept in path]
        avg_importance = sum(importances) / len(importances) if importances else 0.5
        
        if avg_importance > 0.7:
            return 'high'
        elif avg_importance > 0.4:
            return 'medium'
        else:
            return 'low'
    
    def _get_children_from_tree(self, concept, tree):
        """Get children of a concept from the hierarchy tree"""
        children = []
        for child_data in tree.get(concept, []):
            children.append(child_data.get('concept', ''))
        return children
    
    def _is_descendant(self, concept, root, tree):
        """Check if a concept is a descendant of a root in the hierarchy tree"""
        if concept == root:
            return True
        
        for child_data in tree.get(root, []):
            child = child_data.get('concept', '')
            if concept == child or self._is_descendant(concept, child, tree):
                return True
        
        return False
    
    def save_journey(self, journey, output_path):
        """Save learning journey to JSON file"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(journey, f, indent=2)
        
        return output_path
