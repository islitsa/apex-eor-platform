"""
Load Generic Action Ontology into Pinecone
Defines SEMANTIC MEANING of UI actions (View, Download, etc.)

This is what M3 doesn't provide - the behavioral/semantic layer!
M3 tells you HOW buttons look, this tells you WHAT they DO.
"""
import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from src.knowledge.design_kb_pinecone import DesignKnowledgeBasePinecone


# ============================================================================
# ACTION ONTOLOGY - Generic, Domain-Agnostic Patterns
# ============================================================================

action_patterns = [
    {
        "id": "action-view-master-detail",
        "title": "View Action: Master-Detail Navigation Pattern",
        "category": "interaction",
        "content": """
BUTTON LABEL: "View", "Open", "Show Details", "Explore"
SEMANTIC MEANING: Navigate from summary → detail view
PATTERN: Master-Detail Navigation

WHEN TO USE:
- User is looking at a LIST of items (master view)
- Clicking reveals DETAILS about ONE item (detail view)
- Maintains context (breadcrumbs show where you are)

GENERIC IMPLEMENTATION:

```python
def handle_view_action(item_id, item_context, available_data):
    '''
    Generic View handler that adapts to ANY domain

    Args:
        item_id: Identifier for the item being viewed
        item_context: Type/structure info about the item
        available_data: What data/metadata exists for this item
    '''

    # STEP 1: Determine what to show based on what's available
    detail_sections = []

    # Check for metadata
    if 'metadata' in available_data:
        detail_sections.append(render_metadata(item_id))

    # Check for children/sub-items
    if 'children' in available_data:
        detail_sections.append(render_children_list(item_id))

    # Check for preview data
    if 'data_files' in available_data:
        detail_sections.append(render_data_preview(item_id, limit=10))

    # Check for related items
    if 'relationships' in available_data:
        detail_sections.append(render_relationships(item_id))

    # STEP 2: Update navigation state
    update_breadcrumb(item_id)

    # STEP 3: Render detail view
    return {
        'view': 'detail',
        'item_id': item_id,
        'sections': detail_sections,
        'back_enabled': True
    }
```

DOMAIN ADAPTATIONS:
- **Data Pipeline**: View source → show datasets, metadata, sample data
- **File Browser**: View folder → show files inside, view file → show contents
- **E-commerce**: View product → show images, specs, reviews, price
- **CRM**: View contact → show profile, interactions, notes
- **Media Library**: View album → show tracks, view track → show waveform

KEY PRINCIPLE: "View" means "show me more information about this item"
"""
    },

    {
        "id": "action-download-export",
        "title": "Download Action: Export/Transfer Pattern",
        "category": "interaction",
        "content": """
BUTTON LABEL: "Download", "Export", "Save As"
SEMANTIC MEANING: Transfer data from system → user's device
PATTERN: Export/Transfer

WHEN TO USE:
- User wants to EXTRACT data from the application
- Data should leave the system in a portable format
- User needs data for external tools/analysis

GENERIC IMPLEMENTATION:

```python
def handle_download_action(item_id, item_context, available_formats):
    '''
    Generic Download handler that adapts to ANY domain

    Args:
        item_id: What to download
        item_context: Type/structure of the item
        available_formats: Possible export formats
    '''

    # STEP 1: Determine available export options
    export_options = []

    # Check what formats are possible
    if item_context['type'] == 'tabular_data':
        export_options = ['CSV', 'Excel', 'JSON', 'Parquet']
    elif item_context['type'] == 'document':
        export_options = ['PDF', 'DOCX', 'TXT']
    elif item_context['type'] == 'image':
        export_options = ['PNG', 'JPG', 'SVG']
    elif item_context['type'] == 'dataset':
        export_options = ['ZIP (all files)', 'Individual files']

    # STEP 2: If single obvious format, download immediately
    if len(export_options) == 1:
        return trigger_download(item_id, export_options[0])

    # STEP 3: If multiple formats, show selection dialog
    return {
        'action': 'show_download_dialog',
        'item_id': item_id,
        'formats': export_options,
        'estimated_size': calculate_size(item_id)
    }
```

DOMAIN ADAPTATIONS:
- **Data Pipeline**: Download → export dataset as CSV/Parquet/JSON
- **File Browser**: Download → transfer file to local machine
- **E-commerce**: Download → get invoice PDF, receipt
- **CRM**: Download → export contact list as CSV
- **Media Library**: Download → get audio/video file

KEY PRINCIPLE: "Download" means "give me a copy I can take with me"
"""
    },

    {
        "id": "action-rerun-execute",
        "title": "Re-run Action: Execute/Trigger Pattern",
        "category": "interaction",
        "content": """
BUTTON LABEL: "Re-run", "Execute", "Run", "Refresh", "Sync"
SEMANTIC MEANING: Trigger a process or operation
PATTERN: Execute/Trigger

WHEN TO USE:
- User wants to START or RESTART a process
- Action has side effects (computation, data transformation, API calls)
- Result may change from previous execution

GENERIC IMPLEMENTATION:

```python
def handle_rerun_action(item_id, item_context, execution_params):
    '''
    Generic Re-run handler that adapts to ANY domain

    Args:
        item_id: What process to execute
        item_context: Type of operation
        execution_params: Configuration/parameters
    '''

    # STEP 1: Determine what operation to execute
    operation_type = item_context.get('operation_type')

    # STEP 2: Check prerequisites
    can_execute, blocking_issues = check_prerequisites(item_id)

    if not can_execute:
        return {
            'action': 'show_error',
            'message': f"Cannot execute: {blocking_issues}"
        }

    # STEP 3: Show confirmation if destructive
    if item_context.get('is_destructive', False):
        return {
            'action': 'show_confirmation',
            'message': 'This will overwrite existing data. Continue?',
            'on_confirm': lambda: execute_operation(item_id, execution_params)
        }

    # STEP 4: Execute operation with progress tracking
    return {
        'action': 'start_operation',
        'operation_id': item_id,
        'show_progress': True,
        'estimated_duration': estimate_duration(item_id),
        'on_complete': lambda result: show_result_summary(result)
    }
```

DOMAIN ADAPTATIONS:
- **Data Pipeline**: Re-run → execute ETL pipeline stage again
- **File Browser**: Refresh → rescan directory for changes
- **E-commerce**: Sync → refresh inventory from warehouse system
- **CRM**: Re-run → execute automation workflow again
- **Media Library**: Refresh → scan for new media files

KEY PRINCIPLE: "Re-run" means "do that operation again, with current state"
"""
    },

    {
        "id": "action-edit-modify",
        "title": "Edit Action: Modify/Update Pattern",
        "category": "interaction",
        "content": """
BUTTON LABEL: "Edit", "Modify", "Update", "Change"
SEMANTIC MEANING: Enter edit mode to change data
PATTERN: Modify/Update

WHEN TO USE:
- User wants to CHANGE existing data
- Transition from read-only → editable state
- Changes should be validated and saved

GENERIC IMPLEMENTATION:

```python
def handle_edit_action(item_id, item_context, editable_fields):
    '''
    Generic Edit handler that adapts to ANY domain

    Args:
        item_id: What to edit
        item_context: Structure and constraints
        editable_fields: Which fields can be modified
    '''

    # STEP 1: Check permissions
    if not can_edit(item_id):
        return {
            'action': 'show_error',
            'message': 'You do not have permission to edit this item'
        }

    # STEP 2: Load current data
    current_data = load_item_data(item_id)

    # STEP 3: Generate edit form based on field types
    edit_form = []
    for field in editable_fields:
        field_widget = create_widget_for_type(
            field_name=field['name'],
            field_type=field['type'],
            current_value=current_data.get(field['name']),
            constraints=field.get('constraints', {})
        )
        edit_form.append(field_widget)

    # STEP 4: Return edit interface
    return {
        'view': 'edit_mode',
        'item_id': item_id,
        'form_fields': edit_form,
        'on_save': lambda new_data: save_and_validate(item_id, new_data),
        'on_cancel': lambda: return_to_view_mode(item_id)
    }
```

DOMAIN ADAPTATIONS:
- **Data Pipeline**: Edit → modify pipeline configuration
- **File Browser**: Edit → open text editor for file contents
- **E-commerce**: Edit → change product details, pricing
- **CRM**: Edit → update contact information
- **Media Library**: Edit → change metadata, tags

KEY PRINCIPLE: "Edit" means "let me change this data"
"""
    },

    {
        "id": "action-delete-remove",
        "title": "Delete Action: Remove/Destroy Pattern",
        "category": "interaction",
        "content": """
BUTTON LABEL: "Delete", "Remove", "Trash", "Discard"
SEMANTIC MEANING: Permanently or temporarily remove data
PATTERN: Remove/Destroy

WHEN TO USE:
- User wants to REMOVE data from the system
- Action is potentially destructive
- Confirmation should be required for important data

GENERIC IMPLEMENTATION:

```python
def handle_delete_action(item_id, item_context, delete_params):
    '''
    Generic Delete handler that adapts to ANY domain

    Args:
        item_id: What to delete
        item_context: Type, importance, dependencies
        delete_params: Soft vs hard delete, retention policy
    '''

    # STEP 1: Check for dependencies
    dependencies = check_dependencies(item_id)

    if dependencies:
        return {
            'action': 'show_warning',
            'message': f'This item is used by: {dependencies}',
            'options': ['Cancel', 'Delete anyway']
        }

    # STEP 2: Determine deletion strategy
    deletion_strategy = 'soft' if item_context.get('can_recover') else 'hard'

    # STEP 3: Show confirmation with consequences
    confirmation_message = f'''
    Are you sure you want to delete "{item_context['name']}"?

    This action will:
    - Remove {item_context['size']} of data
    - Affect {len(dependencies)} related items
    {'- Move to trash (recoverable for 30 days)' if deletion_strategy == 'soft' else '- PERMANENTLY delete (cannot be recovered)'}
    '''

    # STEP 4: Execute deletion with undo option (if soft)
    return {
        'action': 'confirm_delete',
        'message': confirmation_message,
        'on_confirm': lambda: execute_deletion(item_id, deletion_strategy),
        'show_undo': deletion_strategy == 'soft'
    }
```

DOMAIN ADAPTATIONS:
- **Data Pipeline**: Delete → remove dataset from pipeline
- **File Browser**: Delete → move to trash or permanently delete file
- **E-commerce**: Delete → remove product from catalog
- **CRM**: Delete → remove contact record
- **Media Library**: Delete → remove media file

KEY PRINCIPLE: "Delete" means "I don't want this anymore" (with safety checks!)
"""
    },

    {
        "id": "action-context-discovery",
        "title": "Context-Based Action Discovery Pattern",
        "category": "interaction",
        "content": """
PROBLEM: How does an agent know WHAT actions are possible for an item?

SOLUTION: Discover actions dynamically based on available data/capabilities

IMPLEMENTATION:

```python
def discover_available_actions(item_id, item_context):
    '''
    Dynamically determine what actions make sense for this item
    Based on what data/capabilities are available
    '''

    available_actions = []

    # Check filesystem/API to see what exists
    item_path = resolve_path(item_id)

    # VIEW: Always available if item has details
    if has_metadata(item_path) or has_children(item_path):
        available_actions.append({
            'name': 'View',
            'handler': 'handle_view_action',
            'variant': 'primary'
        })

    # DOWNLOAD: Available if item is exportable
    if is_file(item_path) or has_exportable_data(item_path):
        available_actions.append({
            'name': 'Download',
            'handler': 'handle_download_action',
            'variant': 'secondary'
        })

    # RE-RUN: Available if item is a process/pipeline
    if is_executable(item_path) or has_pipeline_config(item_path):
        available_actions.append({
            'name': 'Re-run',
            'handler': 'handle_rerun_action',
            'variant': 'secondary'
        })

    # EDIT: Available if item is mutable
    if is_editable(item_path) and has_write_permission(item_id):
        available_actions.append({
            'name': 'Edit',
            'handler': 'handle_edit_action',
            'variant': 'secondary'
        })

    # DELETE: Available if item is removable
    if is_deletable(item_path) and has_delete_permission(item_id):
        available_actions.append({
            'name': 'Delete',
            'handler': 'handle_delete_action',
            'variant': 'secondary',
            'destructive': True
        })

    return available_actions


def generate_action_buttons(item_id, item_context):
    '''
    Generate Gradio button components based on discovered actions
    '''
    actions = discover_available_actions(item_id, item_context)

    buttons = []
    handlers = []

    for action in actions:
        # Create Gradio button
        btn = gr.Button(
            action['name'],
            variant=action['variant'],
            size='sm'
        )
        buttons.append(btn)

        # Wire up handler
        handler_fn = globals()[action['handler']]
        btn.click(
            fn=lambda: handler_fn(item_id, item_context),
            outputs=[content_area, nav_state]
        )

    return buttons
```

KEY INSIGHT: Don't hardcode "fracfocus has View, Download, Re-run"
Instead: "Discover what fracfocus CAN do, generate appropriate buttons"

This makes the system truly GENERIC!
"""
    }
]


if __name__ == '__main__':
    print("="*70)
    print("LOADING GENERIC ACTION ONTOLOGY INTO PINECONE")
    print("="*70)
    print("\nThis defines WHAT buttons DO (not just how they look)")
    print("Complements M3's visual guidance with behavioral semantics\n")

    kb = DesignKnowledgeBasePinecone()

    for i, pattern in enumerate(action_patterns, 1):
        print(f"[{i}/{len(action_patterns)}] Loading: {pattern['title']}")

        kb.add_guideline(
            guideline_id=pattern['id'],
            title=pattern['title'],
            content=pattern['content'],
            category=pattern['category'],
            metadata={
                'domain': 'generic',
                'type': 'action_pattern',
                'semantic_layer': True
            }
        )

        print(f"  [OK] Loaded action pattern: {pattern['id']}")

    print("\n" + "="*70)
    print("ACTION ONTOLOGY LOADED SUCCESSFULLY!")
    print("="*70)
    print("\nAgents can now query:")
    print("  - 'What does a View button do?'")
    print("  - 'How do I implement Download action?'")
    print("  - 'What actions are appropriate for data sources?'")
    print("\nAnd get back GENERIC, DOMAIN-AGNOSTIC patterns!")
