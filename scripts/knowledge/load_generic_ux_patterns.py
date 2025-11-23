"""
Load GENERIC, SCALABLE UX Navigation Patterns into Pinecone
Following Opus's guidance: NO hardcoded paths, discover structure dynamically

Key Principle: Pinecone stores PATTERNS, not data-specific logic
"""
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.knowledge.design_kb_pinecone import DesignKnowledgeBasePinecone


# Generic Folder Navigation Pattern (Opus's Version)
generic_navigation_pattern = {
    "id": "generic-hierarchical-navigation-complete",
    "title": "Complete Hierarchical Folder Navigation (Generic - Works for ANY structure)",
    "category": "pattern",
    "content": """
NAVIGATION PRINCIPLES (Generic - NO hardcoded paths):

1. GOING DOWN (View/Click into folder):
   - Use filesystem inspection to determine what's inside
   - Works for ANY folder, not specific paths
   - Discovers structure dynamically at runtime

```python
def handle_view_click(base_path, relative_path=""):
    '''Generic navigation - works for any folder structure'''
    full_path = Path(base_path) / relative_path

    if not full_path.exists():
        return f"Path not found: {full_path}"

    if full_path.is_dir():
        # It's a folder - show contents
        return show_folder_contents(full_path, relative_path)
    else:
        # It's a file - show file info
        return show_file_info(full_path)

def show_folder_contents(folder_path, relative_path):
    '''Dynamically list folder contents - NO hardcoding'''
    html = f'<div class="breadcrumb">{create_breadcrumb(relative_path)}</div>'
    html += '<div class="items">'

    # Discover what's in this folder at runtime
    for item in sorted(folder_path.iterdir()):
        item_type = "folder" if item.is_dir() else "file"
        icon = "📁" if item_type == "folder" else "📄"

        # Build path for clicking
        item_relative = str(Path(relative_path) / item.name) if relative_path else item.name

        html += f'''
        <div class="nav-item" onclick="navigateTo('{item_relative}')">
            {icon} {item.name}
        </div>
        '''

    html += '</div>'
    return html
```

2. GOING UP (Breadcrumb navigation):
   - Each breadcrumb segment is clickable
   - Navigate to any parent level
   - Dynamic - works for any depth

```python
def create_breadcrumb(current_relative_path):
    '''Create clickable breadcrumb from ANY path'''
    if not current_relative_path:
        return '<span class="breadcrumb-root">Root</span>'

    parts = current_relative_path.split('/')
    breadcrumb_html = '<a onclick="navigateTo(\\'\\')">Root</a> > '

    for i, part in enumerate(parts):
        path_to_here = '/'.join(parts[:i+1])
        if i == len(parts) - 1:
            # Current location (not clickable)
            breadcrumb_html += f'<span class="current">{part}</span>'
        else:
            # Parent (clickable)
            breadcrumb_html += f'<a onclick="navigateTo(\\'{path_to_here}\\')">{part}</a> > '

    return breadcrumb_html

def go_up(current_relative_path):
    '''Navigate up one level - works for ANY path'''
    if not current_relative_path:
        return "Already at root"

    parent_path = str(Path(current_relative_path).parent)
    if parent_path == '.':
        parent_path = ""

    return navigate_to(parent_path)
```

3. STATE MANAGEMENT (Track location):

```python
class GenericNavigator:
    '''Navigator that works for ANY folder structure'''

    def __init__(self, base_path="data/raw"):
        self.base_path = Path(base_path)
        self.current_relative_path = ""  # Relative to base_path

    def navigate_to(self, relative_path):
        '''Navigate to any path (up or down) - GENERIC'''
        self.current_relative_path = relative_path
        full_path = self.base_path / relative_path

        if not full_path.exists():
            return f'<div class="error">Path not found: {relative_path}</div>'

        if full_path.is_dir():
            return self.render_folder(full_path, relative_path)
        else:
            return self.render_file(full_path, relative_path)

    def render_folder(self, folder_path, relative_path):
        '''Render any folder - discovers contents dynamically'''
        html = '<div class="folder-view">'

        # Breadcrumb for navigation up
        html += '<div class="breadcrumb">'
        html += self.create_breadcrumb(relative_path)
        html += ' <button onclick="goUp()">↑ Up</button>'
        html += '</div>'

        # List contents (discovered at runtime)
        html += '<div class="folder-contents">'
        items = []

        for item in sorted(folder_path.iterdir()):
            if item.name.startswith('.'):
                continue  # Skip hidden files

            item_rel = str(Path(relative_path) / item.name) if relative_path else item.name

            if item.is_dir():
                # Count items in folder
                try:
                    count = len(list(item.iterdir()))
                    items.append(f'''
                        <div class="folder-item" onclick="navigateTo('{item_rel}')">
                            📁 {item.name}
                            <span class="count">{count} items</span>
                        </div>
                    ''')
                except:
                    items.append(f'''
                        <div class="folder-item" onclick="navigateTo('{item_rel}')">
                            📁 {item.name}
                        </div>
                    ''')
            else:
                # File with size
                size_mb = item.stat().st_size / (1024 * 1024)
                items.append(f'''
                    <div class="file-item" onclick="navigateTo('{item_rel}')">
                        📄 {item.name}
                        <span class="size">{size_mb:.2f} MB</span>
                    </div>
                ''')

        html += ''.join(items)
        html += '</div></div>'
        return html
```

KEY INSIGHTS from Opus:
- DON'T hardcode "if path == 'rrc/completions'..."
- DO use os.listdir() / path.iterdir() to discover dynamically
- DON'T put data-specific paths in Pinecone
- DO put generic navigation principles in Pinecone

WHAT MAKES THIS SCALABLE:
1. Works for ANY folder structure (petroleum, medical, finance, etc.)
2. Discovers contents at runtime (no hardcoded paths)
3. Breadcrumb navigation works at any depth
4. Single navigate_to() function handles up and down
5. Can be applied to any project
"""
}

# Breadcrumb Pattern (Opus's emphasis on going UP)
breadcrumb_pattern = {
    "id": "breadcrumb-navigation-any-depth",
    "title": "Breadcrumb Navigation Pattern (Works at ANY depth)",
    "category": "pattern",
    "content": """
BREADCRUMB NAVIGATION PRINCIPLES:

Purpose: Allow users to navigate UP the hierarchy from any level

Requirements:
1. Show current path as clickable segments
2. Each segment navigates to that level
3. Works at any depth (2 levels or 20 levels)
4. NO hardcoded paths

IMPLEMENTATION (Generic):

```python
def create_clickable_breadcrumb(current_path):
    '''
    Example paths this must handle:
    - "" (root)
    - "rrc" (1 level)
    - "rrc/completions_data" (2 levels)
    - "rrc/completions_data/downloads" (3 levels)
    - "any/deeply/nested/structure/works" (5+ levels)

    Returns clickable HTML breadcrumb
    '''
    if not current_path:
        return '<span class="at-root">📁 Root</span>'

    parts = current_path.split('/')
    breadcrumb = '<a class="breadcrumb-link" onclick="navigateTo(\\'\\')">📁 Root</a>'

    cumulative_path = ""
    for i, part in enumerate(parts):
        cumulative_path = f"{cumulative_path}/{part}" if cumulative_path else part

        if i == len(parts) - 1:
            # Current location (highlighted, not clickable)
            breadcrumb += f' > <span class="current-location">{part}</span>'
        else:
            # Parent location (clickable to go up)
            breadcrumb += f' > <a class="breadcrumb-link" onclick="navigateTo(\\'{cumulative_path}\\')">{part}</a>'

    return breadcrumb
```

GRADIO INTEGRATION:

```python
with gr.Blocks() as demo:
    current_path = gr.State("")
    nav_output = gr.HTML()

    def update_view(path):
        '''Update both content and breadcrumb'''
        content = render_folder_contents(path)
        return content, path

    # Hidden trigger for JavaScript navigation
    nav_trigger.click(
        fn=update_view,
        inputs=[current_path],
        outputs=[nav_output, current_path]
    )
```

This pattern ensures GOING UP is as easy as GOING DOWN!
"""
}


if __name__ == '__main__':
    print("Loading GENERIC, SCALABLE UX Patterns into Pinecone...")
    print("(Following Opus's guidance: NO hardcoded paths!)\n")

    kb = DesignKnowledgeBasePinecone()

    # Load generic navigation pattern
    print("[1/2] Loading Generic Hierarchical Navigation Pattern...")
    kb.add_guideline(
        guideline_id=generic_navigation_pattern['id'],
        title=generic_navigation_pattern['title'],
        content=generic_navigation_pattern['content'],
        category="pattern",
        metadata={"opus_approved": True, "scalable": True, "generic": True}
    )
    print(f"  [OK] Loaded: {generic_navigation_pattern['title']}")

    # Load breadcrumb pattern
    print("\n[2/2] Loading Breadcrumb Navigation Pattern...")
    kb.add_guideline(
        guideline_id=breadcrumb_pattern['id'],
        title=breadcrumb_pattern['title'],
        content=breadcrumb_pattern['content'],
        category="pattern",
        metadata={"opus_approved": True, "bidirectional": True}
    )
    print(f"  [OK] Loaded: {breadcrumb_pattern['title']}")

    print("\n[OK] All GENERIC patterns loaded into Pinecone!")
    print("\nKey improvement: These patterns work for ANY folder structure")
    print("  - NO hardcoded paths (rrc/completions, etc.)")
    print("  - Discovers structure dynamically at runtime")
    print("  - Bidirectional navigation (up and down)")
    print("  - Scalable to any depth")
