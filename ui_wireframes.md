# User Interface Wireframes

## Overview
The user interface for the Knowledge Map Program is designed to be intuitive, visually engaging, and supportive of pattern-seeking cognitive styles. The wireframes below outline the key screens and interactions.

## Main Screens

### 1. Upload Screen
- Clean, minimalist design with clear upload area
- Drag-and-drop functionality with visual feedback
- File type indicators showing supported formats
- Progress indicators for upload and processing
- Option to add multiple files in a single session
- Preview thumbnails of uploaded materials

### 2. Knowledge Map View
- Central visualization area with the interactive knowledge map
- Zoom and navigation controls in bottom right corner
- Filtering panel on left side (collapsible)
- Search bar at top
- View mode selector (network, hierarchical, clusters, etc.)
- Information panel for selected nodes (right side, collapsible)
- User preferences and settings access in top right

### 3. Learning Journey View
- Path visualization showing the learning journey
- Current position indicator
- Content display area for current concept
- Navigation controls for moving through the journey
- Related concepts sidebar
- Option to return to main knowledge map
- Progress indicator

## Key Components

### Upload Component
```
+-----------------------------------------------+
|                                               |
|  +-------------------------------------------+|
|  |                                           ||
|  |     Drag and Drop Learning Materials      ||
|  |                                           ||
|  |     Supported formats: PDF, TXT, PPTX     ||
|  |                                           ||
|  |     [ Select Files ]                      ||
|  |                                           ||
|  +-------------------------------------------+|
|                                               |
|  Previously Uploaded:                         |
|  +------------+  +------------+              |
|  | Material 1 |  | Material 2 |              |
|  +------------+  +------------+              |
|                                               |
|  [ Process Materials ]                        |
|                                               |
+-----------------------------------------------+
```

### Knowledge Map Component
```
+-----------------------------------------------+
| Search: [                    ]     [Settings] |
+-----------------------------------------------+
|                                               |
| +-------+                                     |
| |       |                                     |
| | F     |                                     |
| | I     |                                     |
| | L     |                                     |
| | T     |                                     |
| | E     |                                     |
| | R     |                                     |
| | S     |                                     |
| |       |                                     |
| +-------+                                     |
|                                               |
|                                               |
|                                               |
|                                               |
|              KNOWLEDGE MAP                    |
|              VISUALIZATION                    |
|                                               |
|                                               |
|                                               |
|                                               |
|                                               |
|                                               |
|                                               |
|                                               |
|                                               |
|                                               |
|                                      +------+ |
|                                      | INFO | |
|                                      |      | |
|                                      |      | |
|                                      |      | |
|                                      |      | |
|                                      +------+ |
|                                               |
| [Network] [Hierarchy] [Clusters]   [+] [-]   |
+-----------------------------------------------+
```

### Learning Journey Component
```
+-----------------------------------------------+
| < Back to Map                                 |
+-----------------------------------------------+
|                                               |
| +-------------------------------------------+ |
| |                                           | |
| |           LEARNING JOURNEY PATH           | |
| |                                           | |
| +-------------------------------------------+ |
|                                               |
| +-------+                           +-------+ |
| |       |                           |       | |
| | R     |                           | R     | |
| | E     |                           | E     | |
| | L     |                           | L     | |
| | A     |   CURRENT CONCEPT         | A     | |
| | T     |   CONTENT DISPLAY         | T     | |
| | E     |                           | E     | |
| | D     |                           | D     | |
| |       |                           |       | |
| | 1     |                           | 2     | |
| |       |                           |       | |
| +-------+                           +-------+ |
|                                               |
| +-------------------------------------------+ |
| |                                           | |
| |           INTERACTIVE ELEMENTS            | |
| |                                           | |
| +-------------------------------------------+ |
|                                               |
| [Previous]                        [Next]      |
+-----------------------------------------------+
```

## Interaction States

### Node Selection
- Default state: Nodes displayed at standard size and opacity
- Hover state: Node enlarges slightly, related nodes highlight
- Selected state: Node enlarges significantly, related nodes and connections highlight
- Expanded state: Node transforms to show detailed information

### Learning Journey Navigation
- Current node: Highlighted with distinct visual treatment
- Completed nodes: Visually marked as visited
- Available nodes: Clearly interactive
- Locked nodes: Visually distinct, indicating prerequisites needed

### Responsive Adaptations

#### Mobile View (Upload)
```
+-------------------+
|                   |
|  +-------------+  |
|  |             |  |
|  |  Drag/Drop  |  |
|  |     or      |  |
|  |  [Select]   |  |
|  |             |  |
|  +-------------+  |
|                   |
|  [Process Files]  |
|                   |
+-------------------+
```

#### Mobile View (Knowledge Map)
```
+-------------------+
| [≡] [Search...]   |
+-------------------+
|                   |
|                   |
|                   |
|                   |
|    KNOWLEDGE      |
|       MAP         |
|                   |
|                   |
|                   |
|                   |
+-------------------+
| [View] [Filter] ⊕ |
+-------------------+
```

#### Mobile View (Learning Journey)
```
+-------------------+
| < Map    Journey  |
+-------------------+
|                   |
|     CONCEPT       |
|     CONTENT       |
|                   |
|                   |
|                   |
|                   |
|                   |
|                   |
|                   |
+-------------------+
| ◀ Related    Next ▶|
+-------------------+
```

## Color Scheme and Visual Language

### Color Palette
- Primary: Deep blue (#1a73e8) - For primary actions and selections
- Secondary: Teal (#009688) - For secondary elements and highlights
- Accent: Amber (#ffc107) - For important callouts and alerts
- Background: Light gray (#f5f5f5) - For main background
- Surface: White (#ffffff) - For cards and content areas
- Text: Dark gray (#212121) - For primary text
- Subdued: Medium gray (#757575) - For secondary text

### Visual Hierarchy
- Primary elements: Larger size, higher contrast
- Secondary elements: Medium size, medium contrast
- Tertiary elements: Smaller size, lower contrast

### Iconography
- Consistent, simple icon set
- Meaningful visual metaphors for knowledge structures
- Clear interactive affordances
- Accessibility considerations in icon design
