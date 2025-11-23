"""
Material Design 3 Theme System for Gradio UIs

This module provides a comprehensive Material Design 3 (M3) theme that all
generated UIs can inherit. It includes:
- M3 color tokens (light theme)
- Elevation system (shadows)
- Typography scale
- Component styling (cards, buttons, navigation, tables)
- Animations and transitions

Architecture Compliance:
- One-time creation cost
- Zero runtime token cost
- All patterns inherit beautiful styling automatically
"""

# Material Design 3 Color Tokens (Light Theme - Professional Data/Business palette)
# Based on Material Design 3 spec with business/data-focused colors
M3_COLORS = {
    # Primary colors - Professional Blue (inspired by data dashboards like Stripe, Linear)
    'primary': '#1E88E5',  # Professional blue
    'on_primary': '#FFFFFF',
    'primary_container': '#E3F2FD',  # Light blue container
    'on_primary_container': '#0D47A1',  # Dark blue text

    # Secondary colors - Neutral grays for supporting content
    'secondary': '#546E7A',  # Professional gray-blue
    'on_secondary': '#FFFFFF',
    'secondary_container': '#ECEFF1',  # Light gray container
    'on_secondary_container': '#263238',  # Dark gray text

    # Tertiary colors - Accent teal for highlights
    'tertiary': '#00897B',  # Teal accent
    'on_tertiary': '#FFFFFF',
    'tertiary_container': '#E0F2F1',  # Light teal container
    'on_tertiary_container': '#004D40',  # Dark teal text

    # Error colors
    'error': '#D32F2F',  # Clear red for errors
    'on_error': '#FFFFFF',
    'error_container': '#FFEBEE',
    'on_error_container': '#B71C1C',

    # Surface colors - Clean whites and light grays
    'surface': '#FFFFFF',  # Pure white for main surface
    'on_surface': '#212121',  # Dark gray text
    'surface_variant': '#F5F5F5',  # Very light gray for cards
    'on_surface_variant': '#616161',  # Medium gray text

    # Outline colors
    'outline': '#9E9E9E',  # Medium gray borders
    'outline_variant': '#E0E0E0',  # Light gray borders

    # Status colors (custom extensions)
    'success': '#10B981',  # Modern green (Tailwind-inspired)
    'success_container': '#E8F5E8',
    'warning': '#F59E0B',  # Modern amber
    'warning_container': '#FFF3E0',
    'info': '#3B82F6',  # Modern blue
    'info_container': '#E3F2FD',
}

# Material Design 3 Elevation Levels
# https://m3.material.io/styles/elevation/overview
M3_ELEVATIONS = {
    'level_0': 'none',
    'level_1': '0 1px 2px rgba(0,0,0,0.3), 0 1px 3px 1px rgba(0,0,0,0.15)',
    'level_2': '0 1px 2px rgba(0,0,0,0.3), 0 2px 6px 2px rgba(0,0,0,0.15)',
    'level_3': '0 4px 8px 3px rgba(0,0,0,0.15), 0 1px 3px rgba(0,0,0,0.3)',
    'level_4': '0 6px 10px 4px rgba(0,0,0,0.15), 0 2px 3px rgba(0,0,0,0.3)',
    'level_5': '0 8px 12px 6px rgba(0,0,0,0.15), 0 4px 4px rgba(0,0,0,0.3)',
}

# Material Design 3 Typography Scale
# https://m3.material.io/styles/typography/overview
M3_TYPOGRAPHY = """
/* Display - Large headlines */
.m3-display-large {
    font-size: 57px;
    line-height: 64px;
    font-weight: 400;
    letter-spacing: -0.25px;
}

.m3-display-medium {
    font-size: 45px;
    line-height: 52px;
    font-weight: 400;
}

.m3-display-small {
    font-size: 36px;
    line-height: 44px;
    font-weight: 400;
}

/* Headline - Page titles */
.m3-headline-large {
    font-size: 32px;
    line-height: 40px;
    font-weight: 400;
}

.m3-headline-medium {
    font-size: 28px;
    line-height: 36px;
    font-weight: 400;
}

.m3-headline-small {
    font-size: 24px;
    line-height: 32px;
    font-weight: 400;
}

/* Title - Section headers */
.m3-title-large {
    font-size: 22px;
    line-height: 28px;
    font-weight: 500;
}

.m3-title-medium {
    font-size: 16px;
    line-height: 24px;
    font-weight: 600;
    letter-spacing: 0.15px;
}

.m3-title-small {
    font-size: 14px;
    line-height: 20px;
    font-weight: 600;
    letter-spacing: 0.1px;
}

/* Body - Main content */
.m3-body-large {
    font-size: 16px;
    line-height: 24px;
    font-weight: 400;
    letter-spacing: 0.5px;
}

.m3-body-medium {
    font-size: 14px;
    line-height: 20px;
    font-weight: 400;
    letter-spacing: 0.25px;
}

.m3-body-small {
    font-size: 12px;
    line-height: 16px;
    font-weight: 400;
    letter-spacing: 0.4px;
}

/* Label - Buttons, tabs */
.m3-label-large {
    font-size: 14px;
    line-height: 20px;
    font-weight: 500;
    letter-spacing: 0.1px;
}

.m3-label-medium {
    font-size: 12px;
    line-height: 16px;
    font-weight: 500;
    letter-spacing: 0.5px;
}

.m3-label-small {
    font-size: 11px;
    line-height: 16px;
    font-weight: 500;
    letter-spacing: 0.5px;
}
"""

# Complete Material Design 3 CSS
MATERIAL_DESIGN_3_CSS = f"""
/* ============================================================================
   MATERIAL DESIGN 3 THEME SYSTEM
   ============================================================================ */

/* Import Material Symbols (Google's official icon font) */
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');

/* Material Symbols Usage:
   <span class="material-symbols-rounded">check_circle</span>
   <span class="material-symbols-rounded">database</span>
   <span class="material-symbols-rounded">done</span>

   Common icons for status: check_circle, done, cancel, error, warning, info
   Common icons for data: database, storage, folder, description
   All icons: https://fonts.google.com/icons
*/

.material-symbols-rounded {{
    font-family: 'Material Symbols Rounded';
    font-weight: normal;
    font-style: normal;
    font-size: 24px;
    line-height: 1;
    letter-spacing: normal;
    text-transform: none;
    display: inline-block;
    white-space: nowrap;
    word-wrap: normal;
    direction: ltr;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    text-rendering: optimizeLegibility;
    font-feature-settings: 'liga';
}}

/* Size variants for Material Symbols */
.material-symbols-rounded.md-18 {{ font-size: 18px; }}
.material-symbols-rounded.md-24 {{ font-size: 24px; }}
.material-symbols-rounded.md-36 {{ font-size: 36px; }}
.material-symbols-rounded.md-48 {{ font-size: 48px; }}
.material-symbols-rounded.md-64 {{ font-size: 64px; }}
.material-symbols-rounded.md-80 {{ font-size: 80px; }}

/* Color Tokens */
:root {{
    /* Primary */
    --md-primary: {M3_COLORS['primary']};
    --md-on-primary: {M3_COLORS['on_primary']};
    --md-primary-container: {M3_COLORS['primary_container']};
    --md-on-primary-container: {M3_COLORS['on_primary_container']};

    /* Secondary */
    --md-secondary: {M3_COLORS['secondary']};
    --md-on-secondary: {M3_COLORS['on_secondary']};
    --md-secondary-container: {M3_COLORS['secondary_container']};
    --md-on-secondary-container: {M3_COLORS['on_secondary_container']};

    /* Tertiary */
    --md-tertiary: {M3_COLORS['tertiary']};
    --md-on-tertiary: {M3_COLORS['on_tertiary']};
    --md-tertiary-container: {M3_COLORS['tertiary_container']};
    --md-on-tertiary-container: {M3_COLORS['on_tertiary_container']};

    /* Error */
    --md-error: {M3_COLORS['error']};
    --md-on-error: {M3_COLORS['on_error']};
    --md-error-container: {M3_COLORS['error_container']};
    --md-on-error-container: {M3_COLORS['on_error_container']};

    /* Surface */
    --md-surface: {M3_COLORS['surface']};
    --md-on-surface: {M3_COLORS['on_surface']};
    --md-surface-variant: {M3_COLORS['surface_variant']};
    --md-on-surface-variant: {M3_COLORS['on_surface_variant']};

    /* Outline */
    --md-outline: {M3_COLORS['outline']};
    --md-outline-variant: {M3_COLORS['outline_variant']};

    /* Status (custom) */
    --md-success: {M3_COLORS['success']};
    --md-success-container: {M3_COLORS['success_container']};
    --md-warning: {M3_COLORS['warning']};
    --md-warning-container: {M3_COLORS['warning_container']};
    --md-info: {M3_COLORS['info']};
    --md-info-container: {M3_COLORS['info_container']};

    /* Elevation Shadows */
    --md-elevation-0: {M3_ELEVATIONS['level_0']};
    --md-elevation-1: {M3_ELEVATIONS['level_1']};
    --md-elevation-2: {M3_ELEVATIONS['level_2']};
    --md-elevation-3: {M3_ELEVATIONS['level_3']};
    --md-elevation-4: {M3_ELEVATIONS['level_4']};
    --md-elevation-5: {M3_ELEVATIONS['level_5']};

    /* Timing Functions */
    --md-easing-standard: cubic-bezier(0.4, 0.0, 0.2, 1);
    --md-easing-decelerate: cubic-bezier(0.0, 0.0, 0.2, 1);
    --md-easing-accelerate: cubic-bezier(0.4, 0.0, 1, 1);

    /* Durations */
    --md-duration-short1: 50ms;
    --md-duration-short2: 100ms;
    --md-duration-short3: 150ms;
    --md-duration-short4: 200ms;
    --md-duration-medium1: 250ms;
    --md-duration-medium2: 300ms;
    --md-duration-medium3: 350ms;
    --md-duration-medium4: 400ms;
    --md-duration-long1: 450ms;
    --md-duration-long2: 500ms;

    /* ========================================================================
       M3 SPEC-COMPLIANT ALIASES (for LLM compatibility)
       The Material Design 3 specification uses --md-sys-color-* naming.
       Adding these as aliases so generated code works out of the box.
       ======================================================================== */

    /* Primary */
    --md-sys-color-primary: var(--md-primary);
    --md-sys-color-on-primary: var(--md-on-primary);
    --md-sys-color-primary-container: var(--md-primary-container);
    --md-sys-color-on-primary-container: var(--md-on-primary-container);

    /* Secondary */
    --md-sys-color-secondary: var(--md-secondary);
    --md-sys-color-on-secondary: var(--md-on-secondary);
    --md-sys-color-secondary-container: var(--md-secondary-container);
    --md-sys-color-on-secondary-container: var(--md-on-secondary-container);

    /* Tertiary */
    --md-sys-color-tertiary: var(--md-tertiary);
    --md-sys-color-on-tertiary: var(--md-on-tertiary);
    --md-sys-color-tertiary-container: var(--md-tertiary-container);
    --md-sys-color-on-tertiary-container: var(--md-on-tertiary-container);

    /* Error */
    --md-sys-color-error: var(--md-error);
    --md-sys-color-on-error: var(--md-on-error);
    --md-sys-color-error-container: var(--md-error-container);
    --md-sys-color-on-error-container: var(--md-on-error-container);

    /* Surface */
    --md-sys-color-surface: var(--md-surface);
    --md-sys-color-on-surface: var(--md-on-surface);
    --md-sys-color-surface-variant: var(--md-surface-variant);
    --md-sys-color-on-surface-variant: var(--md-on-surface-variant);

    /* Surface containers (M3 spec has these variations) */
    --md-sys-color-surface-container: var(--md-surface-variant);
    --md-sys-color-surface-container-high: var(--md-surface);
    --md-sys-color-surface-container-highest: var(--md-surface);
    --md-sys-color-surface-container-low: var(--md-surface-variant);
    --md-sys-color-surface-container-lowest: var(--md-surface-variant);

    /* Outline */
    --md-sys-color-outline: var(--md-outline);
    --md-sys-color-outline-variant: var(--md-outline-variant);
}}

/* Typography Scale */
{M3_TYPOGRAPHY}

/* ============================================================================
   COMPONENT STYLES
   ============================================================================ */

/* Cards */
.md-card {{
    background: var(--md-surface);
    border-radius: 12px;
    padding: 16px;
    box-shadow: var(--md-elevation-1);
    transition: box-shadow var(--md-duration-medium2) var(--md-easing-standard),
                transform var(--md-duration-short4) var(--md-easing-standard);
    border: 1px solid var(--md-outline-variant);
}}

.md-card:hover {{
    box-shadow: var(--md-elevation-2);
    transform: translateY(-2px);
}}

.md-card-elevated {{
    background: var(--md-surface);
    border-radius: 12px;
    padding: 16px;
    box-shadow: var(--md-elevation-2);
    border: none;
}}

.md-card-filled {{
    background: var(--md-surface-variant);
    border-radius: 12px;
    padding: 16px;
    box-shadow: none;
    border: none;
}}

.md-card-outlined {{
    background: var(--md-surface);
    border-radius: 12px;
    padding: 16px;
    box-shadow: none;
    border: 1px solid var(--md-outline);
}}

/* Status Cards */
.md-status-card {{
    padding: 20px;
    border-radius: 16px;
    text-align: center;
    transition: all var(--md-duration-medium2) var(--md-easing-standard);
}}

.md-status-card:hover {{
    transform: scale(1.02);
    box-shadow: var(--md-elevation-3);
}}

.md-status-card-success {{
    background: var(--md-success-container);
    border: 1px solid var(--md-success);
}}

.md-status-card-warning {{
    background: var(--md-warning-container);
    border: 1px solid var(--md-warning);
}}

.md-status-card-error {{
    background: var(--md-error-container);
    border: 1px solid var(--md-error);
}}

.md-status-card-info {{
    background: var(--md-info-container);
    border: 1px solid var(--md-info);
}}

/* Navigation Rail */
.md-nav-rail {{
    background: var(--md-surface-variant);
    width: 80px;
    min-width: 80px;
    padding: 12px 0;
    border-radius: 0 16px 16px 0;
    box-shadow: var(--md-elevation-0);
    transition: box-shadow var(--md-duration-medium2) var(--md-easing-standard);
}}

.md-nav-item {{
    width: 56px;
    height: 32px;
    margin: 4px auto;
    border-radius: 16px;
    border: none;
    background: transparent;
    color: var(--md-on-surface-variant);
    cursor: pointer;
    transition: all var(--md-duration-short4) var(--md-easing-standard);
    font-size: 12px;
    font-weight: 500;
}}

.md-nav-item:hover {{
    background: var(--md-secondary-container);
    color: var(--md-on-secondary-container);
}}

.md-nav-item-active {{
    background: var(--md-secondary-container);
    color: var(--md-on-secondary-container);
    font-weight: 600;
}}

/* Buttons */
.md-button-filled {{
    background: var(--md-primary);
    color: var(--md-on-primary);
    border: none;
    border-radius: 20px;
    padding: 10px 24px;
    font-weight: 500;
    font-size: 14px;
    cursor: pointer;
    box-shadow: var(--md-elevation-0);
    transition: all var(--md-duration-short4) var(--md-easing-standard);
}}

.md-button-filled:hover {{
    box-shadow: var(--md-elevation-1);
    background: color-mix(in srgb, var(--md-primary) 92%, white);
}}

.md-button-outlined {{
    background: transparent;
    color: var(--md-primary);
    border: 1px solid var(--md-outline);
    border-radius: 20px;
    padding: 10px 24px;
    font-weight: 500;
    font-size: 14px;
    cursor: pointer;
    transition: all var(--md-duration-short4) var(--md-easing-standard);
}}

.md-button-outlined:hover {{
    background: var(--md-primary-container);
    border-color: var(--md-primary);
}}

.md-button-text {{
    background: transparent;
    color: var(--md-primary);
    border: none;
    border-radius: 20px;
    padding: 10px 12px;
    font-weight: 500;
    font-size: 14px;
    cursor: pointer;
    transition: all var(--md-duration-short4) var(--md-easing-standard);
}}

.md-button-text:hover {{
    background: var(--md-primary-container);
}}

/* Data Tables */
.md-data-table {{
    background: var(--md-surface);
    border-radius: 8px;
    overflow: hidden;
    box-shadow: var(--md-elevation-1);
    border: 1px solid var(--md-outline-variant);
}}

.md-data-table thead {{
    background: var(--md-surface-variant);
    color: var(--md-on-surface-variant);
    font-weight: 600;
    font-size: 14px;
    letter-spacing: 0.1px;
}}

.md-data-table tbody tr {{
    border-bottom: 1px solid var(--md-outline-variant);
    transition: background var(--md-duration-short2) var(--md-easing-standard);
}}

.md-data-table tbody tr:hover {{
    background: var(--md-surface-variant);
}}

.md-data-table th,
.md-data-table td {{
    padding: 12px 16px;
    text-align: left;
}}

/* Headers */
.md-header-gradient {{
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    margin: -1rem -1rem 2rem -1rem;
    border-radius: 0 0 16px 16px;
    color: white;
    box-shadow: var(--md-elevation-2);
}}

.md-header-title {{
    font-size: 32px;
    font-weight: 300;
    margin: 0 0 8px 0;
    color: white;
}}

.md-header-subtitle {{
    font-size: 16px;
    opacity: 0.9;
    font-weight: 400;
    margin: 0;
}}

/* Badges */
.md-badge {{
    display: inline-flex;
    align-items: center;
    padding: 4px 12px;
    border-radius: 16px;
    font-size: 12px;
    font-weight: 500;
    letter-spacing: 0.5px;
}}

.md-badge-success {{
    background: var(--md-success-container);
    color: var(--md-success);
}}

.md-badge-warning {{
    background: var(--md-warning-container);
    color: var(--md-warning);
}}

.md-badge-error {{
    background: var(--md-error-container);
    color: var(--md-error);
}}

.md-badge-info {{
    background: var(--md-info-container);
    color: var(--md-info);
}}

/* Status Indicators */
.md-status-dot {{
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 8px;
}}

.md-status-dot-success {{ background: var(--md-success); }}
.md-status-dot-warning {{ background: var(--md-warning); }}
.md-status-dot-error {{ background: var(--md-error); }}
.md-status-dot-info {{ background: var(--md-info); }}

/* Large Circular Status Indicators (Lovable-style)
   RECOMMENDED: Use with Material Symbols for professional icons
   Usage: <div class="md-status-circle-complete"><span class="material-symbols-rounded md-48">check_circle</span></div>

   Or simple text: <div class="md-status-circle-complete">✓</div>
*/
.md-status-circle {{
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 80px !important;
    height: 80px !important;
    border-radius: 50% !important;
    font-size: 24px !important;
    font-weight: 600 !important;
    box-shadow: var(--md-elevation-2) !important;
    transition: transform var(--md-duration-short4) var(--md-easing-standard) !important;
}}

.md-status-circle:hover {{
    transform: scale(1.05);
}}

.md-status-circle-success {{
    background: var(--md-success);
    color: var(--md-on-primary);
}}

.md-status-circle-warning {{
    background: var(--md-warning);
    color: var(--md-on-primary);
}}

.md-status-circle-error {{
    background: var(--md-error);
    color: var(--md-on-error);
}}

.md-status-circle-info {{
    background: var(--md-info);
    color: var(--md-on-primary);
}}

.md-status-circle-complete {{
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 80px !important;
    height: 80px !important;
    border-radius: 50% !important;
    font-size: 24px !important;
    font-weight: 600 !important;
    box-shadow: var(--md-elevation-2) !important;
    transition: transform var(--md-duration-short4) var(--md-easing-standard) !important;
    background: #10b981 !important;
    color: white !important;
}}

/* Animations */
@keyframes md-fade-in {{
    from {{
        opacity: 0;
        transform: translateY(10px);
    }}
    to {{
        opacity: 1;
        transform: translateY(0);
    }}
}}

.md-fade-in {{
    animation: md-fade-in var(--md-duration-medium4) var(--md-easing-decelerate);
}}

@keyframes md-slide-in {{
    from {{
        transform: translateX(-20px);
        opacity: 0;
    }}
    to {{
        transform: translateX(0);
        opacity: 1;
    }}
}}

.md-slide-in {{
    animation: md-slide-in var(--md-duration-medium3) var(--md-easing-decelerate);
}}

/* DEPRECATED: Use Material Symbols instead
   Old emoji icons replaced with proper Material Symbols icon font
   Use: <span class="material-symbols-rounded">icon_name</span>

   Common icon mappings:
   - Database: <span class="material-symbols-rounded">database</span>
   - Check: <span class="material-symbols-rounded">check_circle</span>
   - Arrow: <span class="material-symbols-rounded">arrow_forward</span>
   - Settings: <span class="material-symbols-rounded">settings</span>
   - File: <span class="material-symbols-rounded">description</span>
*/

/* Utility Classes */
.md-text-primary {{ color: var(--md-primary); }}
.md-text-secondary {{ color: var(--md-secondary); }}
.md-text-error {{ color: var(--md-error); }}
.md-text-success {{ color: var(--md-success); }}
.md-text-warning {{ color: var(--md-warning); }}
.md-text-info {{ color: var(--md-info); }}

.md-bg-surface {{ background: var(--md-surface); }}
.md-bg-surface-variant {{ background: var(--md-surface-variant); }}
.md-bg-primary-container {{ background: var(--md-primary-container); }}

.md-rounded-sm {{ border-radius: 4px; }}
.md-rounded {{ border-radius: 8px; }}
.md-rounded-lg {{ border-radius: 12px; }}
.md-rounded-xl {{ border-radius: 16px; }}
.md-rounded-full {{ border-radius: 9999px; }}

.md-shadow-1 {{ box-shadow: var(--md-elevation-1); }}
.md-shadow-2 {{ box-shadow: var(--md-elevation-2); }}
.md-shadow-3 {{ box-shadow: var(--md-elevation-3); }}
"""


def get_m3_theme_css() -> str:
    """
    Get the complete Material Design 3 CSS theme

    Returns:
        Complete CSS string with all M3 styling
    """
    return MATERIAL_DESIGN_3_CSS


def get_m3_color(color_name: str) -> str:
    """
    Get a specific M3 color token

    Args:
        color_name: Name of the color token (e.g., 'primary', 'surface')

    Returns:
        Hex color value
    """
    return M3_COLORS.get(color_name, M3_COLORS['primary'])


def get_m3_elevation(level: int) -> str:
    """
    Get a specific M3 elevation level

    Args:
        level: Elevation level (0-5)

    Returns:
        CSS box-shadow value
    """
    key = f'level_{min(max(level, 0), 5)}'
    return M3_ELEVATIONS[key]
