import os
import json
import logging
import spacy
import networkx as nx
from collections import Counter
import re

logger = logging.getLogger(__name__)

class KnowledgeExtractor:
    """Extract knowledge concepts and relationships from processed content"""
    
    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        # Load spaCy model - in production, use a larger model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # If model not found, download it
            self.logger.info("Downloading spaCy model...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=True)
            self.nlp = spacy.load("en_core_web_sm")
    
    def extract_knowledge(self, processed_content):
        """
        Extract knowledge from processed content
        
        Args:
            processed_content: Dict containing processed content from file processors
            
        Returns:
            dict: Extracted knowledge structure
        """
        text = processed_content.get('content', '')
        
        if not text:
            return {
                'concepts': [],
                'relationships': [],
                'hierarchy': {},
                'clusters': []
            }
        
        # Extract concepts
        concepts = self._extract_concepts(text)
        
        # Extract relationships
        relationships = self._extract_relationships(text, concepts)
        
        # Generate hierarchy
        hierarchy = self._generate_hierarchy(concepts, relationships)
        
        # Generate concept clusters
        clusters = self._generate_clusters(concepts, relationships)
        
        return {
            'concepts': concepts,
            'relationships': relationships,
            'hierarchy': hierarchy,
            'clusters': clusters
        }
    
    def _extract_concepts(self, text):
        """Extract key concepts from text"""
        # Process text with spaCy
        doc = self.nlp(text)
        
        # Extract noun phrases as potential concepts
        noun_phrases = []
        for chunk in doc.noun_chunks:
            # Clean and normalize the noun phrase
            clean_phrase = re.sub(r'\s+', ' ', chunk.text.strip().lower())
            if clean_phrase and len(clean_phrase.split()) <= 5:  # Limit to 5 words max
                noun_phrases.append(clean_phrase)
        
        # Count frequency of noun phrases
        phrase_counter = Counter(noun_phrases)
        
        # Extract named entities
        entities = []
        for ent in doc.ents:
            if ent.label_ in ['ORG', 'PERSON', 'GPE', 'LOC', 'PRODUCT', 'EVENT', 'WORK_OF_ART', 'LAW']:
                clean_entity = re.sub(r'\s+', ' ', ent.text.strip())
                entities.append({
                    'text': clean_entity,
                    'type': ent.label_
                })
        
        # Extract key terms (nouns, proper nouns, adjectives)
        key_terms = []
        for token in doc:
            if token.pos_ in ['NOUN', 'PROPN'] and not token.is_stop and len(token.text) > 2:
                key_terms.append(token.text.lower())
        
        term_counter = Counter(key_terms)
        
        # Combine and rank concepts
        concepts = []
        
        # Add frequent noun phrases
        for phrase, count in phrase_counter.most_common(50):
            if count >= 2:  # Minimum frequency threshold
                concepts.append({
                    'text': phrase,
                    'type': 'noun_phrase',
                    'frequency': count,
                    'importance': count / len(doc)
                })
        
        # Add named entities
        for entity in entities:
            # Check if entity is already in concepts
            if not any(c['text'].lower() == entity['text'].lower() for c in concepts):
                concepts.append({
                    'text': entity['text'],
                    'type': entity['type'],
                    'frequency': 1,
                    'importance': 0.8  # Entities are usually important
                })
        
        # Add frequent key terms
        for term, count in term_counter.most_common(30):
            if count >= 3 and not any(term in c['text'].lower().split() for c in concepts):
                concepts.append({
                    'text': term,
                    'type': 'key_term',
                    'frequency': count,
                    'importance': count / len(doc)
                })
        
        # Sort by importance
        concepts.sort(key=lambda x: x['importance'], reverse=True)
        
        # Limit to top concepts
        return concepts[:100]
    
    def _extract_relationships(self, text, concepts):
        """Extract relationships between concepts"""
        relationships = []
        
        # Create a graph
        G = nx.Graph()
        
        # Add concepts as nodes
        for concept in concepts:
            G.add_node(concept['text'])
        
        # Process text with spaCy
        doc = self.nlp(text)
        
        # Find co-occurrence relationships
        window_size = 10  # Words to consider for co-occurrence
        
        # Create a mapping of concept text to lowercase for case-insensitive matching
        concept_map = {c['text'].lower(): c['text'] for c in concepts}
        
        # Analyze co-occurrences in sentences
        for sent in doc.sents:
            sent_text = sent.text.lower()
            
            # Check which concepts appear in this sentence
            sentence_concepts = []
            for concept_lower, concept_original in concept_map.items():
                if concept_lower in sent_text:
                    sentence_concepts.append(concept_original)
            
            # Create relationships between concepts in the same sentence
            for i in range(len(sentence_concepts)):
                for j in range(i+1, len(sentence_concepts)):
                    concept1 = sentence_concepts[i]
                    concept2 = sentence_concepts[j]
                    
                    # Add edge or increment weight if it exists
                    if G.has_edge(concept1, concept2):
                        G[concept1][concept2]['weight'] += 1
                    else:
                        G.add_edge(concept1, concept2, weight=1, type='co-occurrence')
        
        # Extract syntactic relationships
        for sent in doc.sents:
            for token in sent:
                if token.dep_ in ['nsubj', 'dobj', 'pobj']:
                    # Get the head (usually a verb or preposition)
                    head = token.head
                    
                    # Check if token and head's text are in our concepts
                    token_text = token.text.lower()
                    head_text = head.text.lower()
                    
                    token_concept = None
                    head_concept = None
                    
                    # Find matching concepts (allowing for partial matches)
                    for concept in concepts:
                        concept_lower = concept['text'].lower()
                        if token_text in concept_lower or concept_lower in token_text:
                            token_concept = concept['text']
                        if head_text in concept_lower or concept_lower in head_text:
                            head_concept = concept['text']
                    
                    # If both are found, add relationship
                    if token_concept and head_concept and token_concept != head_concept:
                        rel_type = 'subject_of' if token.dep_ == 'nsubj' else 'object_of'
                        
                        # Add edge or increment weight if it exists
                        if G.has_edge(token_concept, head_concept):
                            G[token_concept][head_concept]['weight'] += 1
                            if rel_type not in G[token_concept][head_concept]['types']:
                                G[token_concept][head_concept]['types'].append(rel_type)
                        else:
                            G.add_edge(token_concept, head_concept, weight=1, type='syntactic', types=[rel_type])
        
        # Convert graph to relationships list
        for u, v, data in G.edges(data=True):
            relationships.append({
                'source': u,
                'target': v,
                'weight': data['weight'],
                'type': data.get('type', 'co-occurrence'),
                'subtypes': data.get('types', [])
            })
        
        # Sort by weight
        relationships.sort(key=lambda x: x['weight'], reverse=True)
        
        return relationships
    
    def _generate_hierarchy(self, concepts, relationships):
        """Generate concept hierarchy"""
        # Create a directed graph for hierarchy
        G = nx.DiGraph()
        
        # Add all concepts as nodes
        for concept in concepts:
            G.add_node(concept['text'], importance=concept['importance'])
        
        # Identify potential hierarchical relationships
        for concept1 in concepts:
            for concept2 in concepts:
                if concept1['text'] != concept2['text']:
                    # Check if one concept is contained within another
                    if concept1['text'].lower() in concept2['text'].lower():
                        # concept2 is more specific than concept1
                        G.add_edge(concept1['text'], concept2['text'], type='contains')
                    elif concept2['text'].lower() in concept1['text'].lower():
                        # concept1 is more specific than concept2
                        G.add_edge(concept2['text'], concept1['text'], type='contains')
        
        # Find root nodes (concepts with no parents or highest importance)
        root_candidates = [n for n in G.nodes() if G.in_degree(n) == 0]
        
        if not root_candidates:
            # If no clear roots, use most important concepts
            root_candidates = sorted(G.nodes(), key=lambda n: G.nodes[n]['importance'], reverse=True)[:5]
        
        # Build hierarchy tree
        hierarchy = {
            'roots': root_candidates[:5],  # Limit to top 5 roots
            'tree': {}
        }
        
        # For each root, build its subtree
        for root in hierarchy['roots']:
            hierarchy['tree'][root] = self._build_subtree(G, root)
        
        return hierarchy
    
    def _build_subtree(self, G, node):
        """Recursively build subtree for hierarchy"""
        children = list(G.successors(node))
        
        if not children:
            return []
        
        subtree = []
        for child in children:
            child_data = {
                'concept': child,
                'children': self._build_subtree(G, child)
            }
            subtree.append(child_data)
        
        return subtree
    
    def _generate_clusters(self, concepts, relationships):
        """Generate concept clusters based on relationship strength"""
        # Create a graph from relationships
        G = nx.Graph()
        
        # Add concepts as nodes
        for concept in concepts:
            G.add_node(concept['text'], importance=concept['importance'])
        
        # Add relationships as edges
        for rel in relationships:
            G.add_edge(rel['source'], rel['target'], weight=rel['weight'])
        
        # Use community detection to find clusters
        try:
            # Try Louvain method first (requires community module)
            import community
            partition = community.best_partition(G)
            clusters = {}
            
            for node, cluster_id in partition.items():
                if cluster_id not in clusters:
                    clusters[cluster_id] = []
                clusters[cluster_id].append(node)
            
            # Convert to list of clusters
            cluster_list = [{'id': i, 'concepts': concepts} for i, concepts in clusters.items()]
            
        except ImportError:
            # Fall back to connected components
            self.logger.warning("Community detection module not available, using connected components")
            connected_components = list(nx.connected_components(G))
            
            cluster_list = [
                {'id': i, 'concepts': list(component)}
                for i, component in enumerate(connected_components)
            ]
        
        # Sort clusters by size
        cluster_list.sort(key=lambda x: len(x['concepts']), reverse=True)
        
        # Generate cluster names based on most important concepts
        for cluster in cluster_list:
            # Find most important concept in cluster
            cluster_concepts = [c for c in concepts if c['text'] in cluster['concepts']]
            if cluster_concepts:
                most_important = max(cluster_concepts, key=lambda x: x['importance'])
                cluster['name'] = most_important['text']
            else:
                cluster['name'] = f"Cluster {cluster['id']}"
        
        return cluster_list
