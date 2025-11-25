# Favorites Feature

## Overview

Added a favorites system to Agent Studio so you can save and reload your favorite UI iterations.

## Features

### Save Favorites
- Enter a name for your current UI (e.g., "Pipeline Dashboard v1")
- Click **⭐ Save as Favorite**
- The system saves:
  - Complete generated code
  - Original prompt used
  - Timestamp
  - Code length

### Load Favorites
- Select a favorite from the dropdown
- Click **📥 Load Favorite**
- The code is loaded into your current session
- You can immediately launch or edit it

### Delete Favorites
- Select a favorite from the dropdown
- Click **🗑️ Delete** to remove it

## Storage

Favorites are stored in: `C:\Users\irina\.apex_eor\favorites.json`

This persists across sessions - your favorites are always available.

## Usage in Agent Studio

1. **Generate a UI** you like
2. **Enter a name** in the "Save current UI as favorite" field
3. **Click "Save as Favorite"**
4. Later, **select from dropdown** and click "Load Favorite"
5. **Launch** or **modify** the loaded code

## Benefits

- **Iterate faster**: Quickly return to designs you like
- **Version control**: Save multiple variations with descriptive names
- **Learn patterns**: Review what worked in past iterations
- **Share**: Favorites file can be shared with team members

## Example Workflow

```
1. Generate dashboard with prompt: "create a pipeline dashboard"
   → Save as "Pipeline Dashboard - Clean"

2. Request changes: "make cards bigger, add more spacing"
   → Save as "Pipeline Dashboard - Spacious"

3. Try different approach: "use a table instead of cards"
   → Save as "Pipeline Dashboard - Table View"

4. Compare by loading each favorite and launching
```

## Technical Details

### FavoritesManager Class
Location: `shared_state.py`

Methods:
- `save_favorite(name, code, prompt, tags)` - Save a new favorite
- `load_favorites()` - Get all favorites
- `get_favorite(name)` - Get specific favorite
- `delete_favorite(name)` - Remove a favorite
- `list_favorites()` - Get sorted list of names

### UI Integration
Location: `src/ui/agent_studio.py` (lines 596-676)

Added below the Save/Launch buttons with:
- Text input for favorite name
- Save button (disabled if no name)
- Dropdown selector
- Load and Delete buttons
- Success/error messages

## Future Enhancements

Potential additions:
- **Tags/Categories**: Organize favorites by type (dashboard, form, chart, etc.)
- **Export/Import**: Share favorites as files
- **Thumbnails**: Screenshot preview of each favorite
- **Search**: Filter favorites by name or prompt
- **Diff View**: Compare two favorites side-by-side
