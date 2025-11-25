"""
Test Favorites Manager
"""
import sys
import io

# Fix encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from shared_state import FavoritesManager

# Test saving a favorite
test_code = '''
import gradio as gr

def create_dashboard():
    with gr.Blocks() as demo:
        gr.Markdown("# Test Dashboard")
        gr.Button("Click me!")
    return demo

if __name__ == "__main__":
    demo = create_dashboard()
    demo.launch()
'''

print("Testing Favorites Manager...")
print("=" * 60)

# Save a favorite
print("\n1. Saving favorite 'Test Dashboard'...")
result = FavoritesManager.save_favorite(
    name="Test Dashboard",
    code=test_code,
    prompt="create a simple dashboard with a button",
    tags=["test", "simple"]
)
print(f"   Result: {'✅ Success' if result else '❌ Failed'}")

# List favorites
print("\n2. Listing favorites...")
favorites = FavoritesManager.list_favorites()
print(f"   Found {len(favorites)} favorites:")
for fav in favorites:
    print(f"   - {fav}")

# Get a specific favorite
print("\n3. Loading 'Test Dashboard'...")
favorite_data = FavoritesManager.get_favorite("Test Dashboard")
if favorite_data:
    print(f"   ✅ Loaded!")
    print(f"   Code length: {favorite_data['code_length']} chars")
    print(f"   Prompt: {favorite_data['prompt']}")
    print(f"   Tags: {favorite_data['tags']}")
    print(f"   Saved: {favorite_data['saved_at']}")
else:
    print(f"   ❌ Not found")

# Save another favorite
print("\n4. Saving another favorite 'Complex Dashboard'...")
result = FavoritesManager.save_favorite(
    name="Complex Dashboard",
    code=test_code * 3,  # Longer code
    prompt="create a complex multi-panel dashboard"
)
print(f"   Result: {'✅ Success' if result else '❌ Failed'}")

# List again
print("\n5. Listing all favorites...")
favorites = FavoritesManager.list_favorites()
print(f"   Found {len(favorites)} favorites:")
for fav in favorites:
    print(f"   - {fav}")

# Delete a favorite
print("\n6. Deleting 'Test Dashboard'...")
result = FavoritesManager.delete_favorite("Test Dashboard")
print(f"   Result: {'✅ Deleted' if result else '❌ Failed'}")

# List final
print("\n7. Final favorites list...")
favorites = FavoritesManager.list_favorites()
print(f"   Found {len(favorites)} favorites:")
for fav in favorites:
    print(f"   - {fav}")

print("\n" + "=" * 60)
print("Test complete!")
print(f"Favorites stored in: {FavoritesManager.FAVORITES_FILE}")
