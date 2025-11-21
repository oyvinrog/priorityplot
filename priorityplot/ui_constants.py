"""
UI Constants for PriPlot Application

Centralized constants for colors, sizes, and styling tokens to maintain
consistency and make theme changes easier.
"""

# ============================================================================
# COLOR PALETTE - Dark Theme Design System
# ============================================================================

class ColorPalette:
    """Centralized color scheme for the application"""
    
    # Primary Background Colors
    BG_PRIMARY = '#181A1F'
    BG_SECONDARY = '#1F2228'
    BG_TERTIARY = '#252830'
    BG_DARK = '#0F1117'
    BG_DARKER = '#111317'
    BG_LIGHT = '#2D3139'
    BG_ALT = '#1F2937'
    
    # Text Colors
    TEXT_PRIMARY = '#E5E7EB'
    TEXT_SECONDARY = '#F3F4F6'
    TEXT_MUTED = '#9CA3AF'
    TEXT_DISABLED = '#6B7280'
    TEXT_DARK = '#374151'
    TEXT_BLACK = '#000000'
    TEXT_WHITE = '#FFFFFF'
    
    # Accent Colors
    ACCENT_PURPLE = '#4F46E5'
    ACCENT_PURPLE_LIGHT = '#6366F1'
    ACCENT_PURPLE_LIGHTER = '#818CF8'
    ACCENT_PURPLE_DARK = '#4338CA'
    ACCENT_PURPLE_DARKER = '#3730A3'
    ACCENT_PURPLE_ALT = '#8B5CF6'
    ACCENT_PURPLE_ALT_LIGHT = '#A78BFA'
    ACCENT_PURPLE_ALT_DARK = '#7C3AED'
    ACCENT_PURPLE_ALT_DARKER = '#6D28D9'
    
    # Status Colors
    SUCCESS = '#10B981'
    SUCCESS_LIGHT = '#34D399'
    SUCCESS_DARK = '#059669'
    SUCCESS_DARKER = '#047857'
    
    ERROR = '#EF4444'
    ERROR_LIGHT = '#F87171'
    ERROR_DARK = '#DC2626'
    ERROR_DARKER = '#B91C1C'
    
    WARNING = '#F59E0B'
    WARNING_LIGHT = '#FBBF24'
    
    INFO = '#3B82F6'
    INFO_LIGHT = '#60A5FA'
    INFO_DARK = '#2563EB'
    INFO_DARKER = '#1D4ED8'
    
    # Task State Colors
    TASK_MOVED = '#2a82da'
    TASK_ORIGINAL = '#e74c3c'
    TASK_NEW = '#00FF7F'
    
    # Highlight Colors
    HIGHLIGHT_GOLD = '#FFD700'
    HIGHLIGHT_GOLD_ALT = '#FF6B35'
    HIGHLIGHT_CYAN = '#00FFFF'
    HIGHLIGHT_GREEN = '#00FF7F'
    HIGHLIGHT_GREEN_DARK = '#00CC66'
    HIGHLIGHT_GREEN_DARKER = '#00CC66'
    
    # Medal Colors (for top 3 rankings)
    MEDAL_GOLD = '#FFD700'
    MEDAL_SILVER = '#C0C0C0'
    MEDAL_BRONZE = '#CD7F32'
    
    # Border Colors
    BORDER_PRIMARY = '#2D3139'
    BORDER_ACCENT = '#4F46E5'
    BORDER_LIGHT = '#3F4451'
    BORDER_SUCCESS = '#10B981'
    
    # Grid Colors
    GRID_LINE = '#3F4451'
    
    # Special Colors
    PLOT_BG = '#181A1F'
    TOOLTIP_BG = '#2a82da'
    DRAG_PREVIEW_BG = '#FFD700'
    EXTERNAL_DRAG_BG = '#00FF7F'

# ============================================================================
# SIZE CONSTANTS
# ============================================================================

class SizeConstants:
    """Size and spacing constants"""
    
    # Padding
    PADDING_SMALL = 8
    PADDING_MEDIUM = 10
    PADDING_LARGE = 12
    PADDING_XLARGE = 14
    PADDING_XXLARGE = 16
    PADDING_XXXLARGE = 20
    
    # Border Radius
    RADIUS_SMALL = 6
    RADIUS_MEDIUM = 8
    RADIUS_LARGE = 10
    RADIUS_XLARGE = 12
    
    # Font Sizes
    FONT_SMALL = 9
    FONT_NORMAL = 10
    FONT_MEDIUM = 11
    FONT_LARGE = 12
    FONT_XLARGE = 13
    FONT_XXLARGE = 14
    FONT_XXXLARGE = 15
    FONT_HEADER = 17
    FONT_TITLE = 20
    
    # Scatter Plot Sizes
    SCATTER_NORMAL = 100
    SCATTER_TOP_RANK = 20
    SCATTER_HIGHLIGHT = 400
    SCATTER_PULSE = 500
    SCATTER_DRAG = 600
    
    # Column Widths
    COLUMN_RANK = 60
    COLUMN_VALUE = 90
    COLUMN_SCORE = 90
    COLUMN_DELETE = 60
    COLUMN_ACTION = 80
    
    # Row Heights
    ROW_HEIGHT_DEFAULT = 35
    
    # Button Sizes
    BUTTON_MIN_WIDTH = 90
    BUTTON_MIN_WIDTH_LARGE = 100
    BUTTON_MIN_WIDTH_XLARGE = 110
    
    # Widget Sizes
    INPUT_TABLE_MAX_HEIGHT = 200
    RESULTS_MIN_HEIGHT = 300
    RESULTS_MAX_HEIGHT = 500
    
    # Window Sizes
    WINDOW_MIN_WIDTH = 800
    WINDOW_MIN_HEIGHT = 600
    WINDOW_DEFAULT_WIDTH = 1000
    WINDOW_DEFAULT_HEIGHT = 700
    WINDOW_MAX_WIDTH = 1600
    WINDOW_MAX_HEIGHT = 1200
    
    # Icon Sizes
    ICON_SPACE = 30
    ICON_SPACE_LARGE = 35
    
    # Drag Pixmap Sizes
    DRAG_PIXMAP_MIN_WIDTH = 200
    DRAG_PIXMAP_MIN_WIDTH_LARGE = 220
    
    # Line Widths
    LINE_WIDTH_THIN = 0.5
    LINE_WIDTH_NORMAL = 0.8
    LINE_WIDTH_MEDIUM = 1.5
    LINE_WIDTH_THICK = 2
    LINE_WIDTH_EXTRA_THICK = 4
    LINE_WIDTH_VERY_THICK = 6

# ============================================================================
# OPACITY/ALPHA CONSTANTS
# ============================================================================

class OpacityConstants:
    """Alpha/opacity values for various UI elements"""
    
    ALPHA_HIDDEN = 0
    ALPHA_SUBTLE = 0.2
    ALPHA_LIGHT = 0.5
    ALPHA_MEDIUM = 0.7
    ALPHA_HIGH = 0.8
    ALPHA_VERY_HIGH = 0.9
    ALPHA_FULL = 1.0
    
    # Specific use cases
    ALPHA_GRID = 0.2
    ALPHA_SCATTER = 0.7
    ALPHA_HIGHLIGHT = 0.9
    ALPHA_TOOLTIP = 0.9
    ALPHA_DRAG = 0.8
    ALPHA_TOP_RANK = 150  # For QColor alpha (0-255)
    ALPHA_MEDAL = 150
    ALPHA_TABLE_BG = 200
    ALPHA_PIXMAP_BG = 220
    ALPHA_PIXMAP_BORDER = 255

# ============================================================================
# INTERACTION CONSTANTS
# ============================================================================

class InteractionConstants:
    """Constants for user interaction behavior"""
    
    # Drag thresholds
    DRAG_THRESHOLD_PIXELS = 5
    
    # Timers (milliseconds)
    AUTO_UPDATE_DELAY_MS = 100
    PLACEHOLDER_RESET_DELAY_MS = 2000
    ASYNC_DRAG_DELAY_MS = 0
    
    # Font weights
    FONT_WEIGHT_NORMAL = 600
    FONT_WEIGHT_BOLD = 700
    FONT_WEIGHT_EXTRA_BOLD = 900

# ============================================================================
# LAYOUT CONSTANTS
# ============================================================================

class LayoutConstants:
    """Layout and positioning constants"""
    
    # Margins
    MARGIN_NONE = 0
    MARGIN_SMALL = 5
    MARGIN_MEDIUM = 8
    
    # Spacing
    SPACING_SMALL = 2
    
    # Figure adjustments (matplotlib)
    FIG_LEFT = 0.12
    FIG_BOTTOM = 0.12
    FIG_RIGHT = 0.95
    FIG_TOP = 0.92
    
    # Splitter sizes
    SPLITTER_PLOT_SIZE = 300
    SPLITTER_RESULTS_SIZE = 350
    
    # Text offsets
    TEXT_OFFSET_X = 10
    TEXT_OFFSET_Y = 10
    TEXT_OFFSET_Y_LARGE = 30
    
    # Label padding
    LABEL_PAD = 10
    LABEL_PAD_LARGE = 15

# ============================================================================
# TEXT CONSTANTS
# ============================================================================

class TextConstants:
    """Text-related constants"""
    
    # Truncation
    TASK_NAME_MAX_SHORT = 15
    TASK_NAME_MAX_MEDIUM = 20
    TASK_NAME_MAX_LONG = 25
    ELLIPSIS = "..."
    
    # Letter spacing
    LETTER_SPACING_SMALL = 0.3
    LETTER_SPACING_MEDIUM = 0.5
    LETTER_SPACING_LARGE = 1.0
    
    # Emojis
    EMOJI_TROPHY = '🏆'
    EMOJI_STAR = '⭐'
    EMOJI_FIRE = '🔥'
    EMOJI_LIGHTNING = '⚡'
    EMOJI_BULB = '💡'
    EMOJI_MEDAL_GOLD = '🥇'
    EMOJI_MEDAL_SILVER = '🥈'
    EMOJI_MEDAL_BRONZE = '🥉'
    EMOJI_TARGET = '🎯'
    EMOJI_CLIPBOARD = '📋'
    EMOJI_NEW = '🆕'
    
    # Context lines for code review
    MIN_CONTEXT_LINES = 3

# ============================================================================
# MATPLOTLIB FIGURE CONSTANTS
# ============================================================================

class FigureConstants:
    """Matplotlib figure configuration"""
    
    FIG_WIDTH = 8
    FIG_HEIGHT = 5
    FIG_DPI = 100

