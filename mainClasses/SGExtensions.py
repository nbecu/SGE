"""
SGExtensions.py
This file groups all general utility methods, as well as class extensions (Qt or not) used in the project.
Example: methods dynamically added to QPainter, QWidget, list, dict, etc.
"""

import sys
from pathlib import Path
from PyQt6.QtGui import QFontMetrics, QFont, QPainter, QPixmap, QColor, QTextOption, QRegion, QPalette
from PyQt6.QtCore import QRectF, Qt
from PyQt6.QtWidgets import QDialog, QAbstractItemView, QSizePolicy, QTextEdit, QMessageBox, QHeaderView, QStandardItem

__all__ = [
    "SGColors",
    "drawTextAutoSized",
    "fillTransparentAreas",
    "first_value",
    "first_key",
    "first_item",
    "execute_callable_with_entity",
    "normalize_type_name",
    "generate_color_gradient",
    "serialize_any_object",
    "mapAlignmentStringToQtFlags",
    "position_dialog_to_right",
    "getResourceBasePath",
    "getResourcePath",
    "listImagePaths",
    "copyValue",
]

def drawTextAutoSized(self, aleft, atop, text, font=None, align=0, padding_width=0, padding_height=0):
    """
    Draws the given text at position (aleft, atop) inside a rectangle automatically sized to fit the text.
    - Computes the required width and height using QFontMetrics.
    - Applies the specified font and alignment.
    - Optionally adds horizontal and vertical padding.

    :param self: QPainter instance
    :param aleft: x position (left) of the rectangle
    :param atop: y position (top) of the rectangle
    :param text: text to draw
    :param font: QFont to use (optional, default Verdana 8)
    :param align: Qt alignment flag (e.g., Qt.AlignLeft)
    :param padding_width: extra width to add (in pixels)
    :param padding_height: extra height to add (in pixels)
    :return: (width, height) of the rectangle used
    """
    if font is None:
        font = QFont("Verdana", 8)
    self.setFont(font)
    metrics = QFontMetrics(font)
    width = metrics.horizontalAdvance(text) + padding_width
    height = metrics.height() + padding_height
    rect = QRectF(aleft, atop, width, height)
    self.drawText(rect, align, text)
    return width, height

# Attach the method to QPainter for direct usage everywhere in the project
QPainter.drawTextAutoSized = drawTextAutoSized

class SGColors:
    """Named color constants as QColor objects.

    All SGColors attributes are also injected into the Qt namespace on import
    (e.g. Qt.orange, Qt.pink) for backward compatibility with existing models.
    New code should prefer SGColors.orange, SGColors.pink, etc.
    """
    # Basic
    pink             = QColor.fromRgb(255, 192, 203)
    orange           = QColor.fromRgb(255, 165, 0)
    cyan             = QColor.fromRgb(0, 255, 255)
    lime             = QColor.fromRgb(0, 255, 0)
    indigo           = QColor.fromRgb(75, 0, 130)
    violet           = QColor.fromRgb(238, 130, 238)
    teal             = QColor.fromRgb(0, 128, 128)
    amber            = QColor.fromRgb(255, 191, 0)
    brown            = QColor.fromRgb(165, 42, 42)
    grey             = QColor.fromRgb(128, 128, 128)
    gray             = QColor.fromRgb(128, 128, 128)
    lightsteelblue   = QColor.fromRgb(176, 196, 222)
    tomato           = QColor.fromRgb(255, 99, 71)
    darkgray         = QColor.fromRgb(169, 169, 169)
    mediumvioletred  = QColor.fromRgb(199, 21, 133)
    purple           = QColor.fromRgb(128, 0, 128)
    turquoise        = QColor.fromRgb(64, 224, 208)
    # Blues
    lightblue        = QColor.fromRgb(173, 216, 230);  lightBlue        = lightblue
    darkblue         = QColor.fromRgb(0, 0, 139);      darkBlue         = darkblue
    navy             = QColor.fromRgb(0, 0, 128)
    royalblue        = QColor.fromRgb(65, 105, 225);   royalBlue        = royalblue
    skyblue          = QColor.fromRgb(135, 206, 235);  skyBlue          = skyblue
    powderblue       = QColor.fromRgb(176, 224, 230);  powderBlue       = powderblue
    steelblue        = QColor.fromRgb(70, 130, 180);   steelBlue        = steelblue
    midnightblue     = QColor.fromRgb(25, 25, 112);    midnightBlue     = midnightblue
    mediumblue       = QColor.fromRgb(0, 0, 205);      mediumBlue       = mediumblue
    cornflowerblue   = QColor.fromRgb(100, 149, 237);  cornflowerBlue   = cornflowerblue
    aliceblue        = QColor.fromRgb(240, 248, 255);  aliceBlue        = aliceblue
    # Reds
    crimson          = QColor.fromRgb(220, 20, 60)
    darkred          = QColor.fromRgb(139, 0, 0);      darkRed          = darkred
    lightcoral       = QColor.fromRgb(240, 128, 128);  lightCoral       = lightcoral
    firebrick        = QColor.fromRgb(178, 34, 34);    fireBrick        = firebrick
    indianred        = QColor.fromRgb(205, 92, 92);    indianRed        = indianred
    salmon           = QColor.fromRgb(250, 128, 114)
    rosybrown        = QColor.fromRgb(188, 143, 143);  rosyBrown        = rosybrown
    maroon           = QColor.fromRgb(128, 0, 0)
    orangered        = QColor.fromRgb(255, 69, 0);     orangeRed        = orangered
    coral            = QColor.fromRgb(255, 127, 80)
    lightsalmon      = QColor.fromRgb(255, 160, 122);  lightSalmon      = lightsalmon
    mistyrose        = QColor.fromRgb(255, 228, 225);  mistyRose        = mistyrose
    # Greens
    darkgreen        = QColor.fromRgb(0, 100, 0);      darkGreen        = darkgreen
    lightgreen       = QColor.fromRgb(144, 238, 144);  lightGreen       = lightgreen
    forestgreen      = QColor.fromRgb(34, 139, 34);    forestGreen      = forestgreen
    seagreen         = QColor.fromRgb(46, 139, 87);    seaGreen         = seagreen
    olive            = QColor.fromRgb(128, 128, 0)
    olivedrab        = QColor.fromRgb(107, 142, 35);   oliveDrab        = olivedrab
    springgreen      = QColor.fromRgb(0, 255, 127);    springGreen      = springgreen
    palegreen        = QColor.fromRgb(152, 251, 152);  paleGreen        = palegreen
    limegreen        = QColor.fromRgb(50, 205, 50);    limeGreen        = limegreen
    # Yellows / Oranges
    gold             = QColor.fromRgb(255, 215, 0)
    darkorange       = QColor.fromRgb(255, 140, 0);    darkOrange       = darkorange
    lightyellow      = QColor.fromRgb(255, 255, 224);  lightYellow      = lightyellow
    khaki            = QColor.fromRgb(240, 230, 140)
    peachpuff        = QColor.fromRgb(255, 218, 185);  peachPuff        = peachpuff
    moccasin         = QColor.fromRgb(255, 228, 181)
    papayawhip       = QColor.fromRgb(255, 239, 213);  papayaWhip       = papayawhip
    darkgoldenrod    = QColor.fromRgb(184, 134, 11);   darkGoldenrod    = darkgoldenrod
    goldenrod        = QColor.fromRgb(218, 165, 32)
    lemonchiffon     = QColor.fromRgb(255, 250, 205);  lemonChiffon     = lemonchiffon
    ivory            = QColor.fromRgb(255, 255, 240)
    # Violets / Purples
    darkviolet       = QColor.fromRgb(148, 0, 211);    darkViolet       = darkviolet
    plum             = QColor.fromRgb(221, 160, 221)
    lavender         = QColor.fromRgb(230, 230, 250)
    orchid           = QColor.fromRgb(218, 112, 214)
    thistle          = QColor.fromRgb(216, 191, 216)
    mediumorchid     = QColor.fromRgb(186, 85, 211);   mediumOrchid     = mediumorchid
    mediumpurple     = QColor.fromRgb(147, 112, 219);  mediumPurple     = mediumpurple
    hotpink          = QColor.fromRgb(255, 105, 180);  hotPink          = hotpink
    # Grays
    lightgray        = QColor.fromRgb(211, 211, 211);  lightGray        = lightgray
    silver           = QColor.fromRgb(192, 192, 192)
    slategray        = QColor.fromRgb(112, 128, 144);  slateGray        = slategray
    dimgray          = QColor.fromRgb(105, 105, 105);  dimGray          = dimgray
    gainsboro        = QColor.fromRgb(220, 220, 220)
    whitesmoke       = QColor.fromRgb(245, 245, 245);  whiteSmoke       = whitesmoke
    darkslategray    = QColor.fromRgb(47, 79, 79);     darkSlateGray    = darkslategray
    # Browns
    saddlebrown      = QColor.fromRgb(139, 69, 19);    saddleBrown      = saddlebrown
    sienna           = QColor.fromRgb(160, 82, 45)
    chocolate        = QColor.fromRgb(210, 105, 30)
    peru             = QColor.fromRgb(205, 133, 63)
    burlywood        = QColor.fromRgb(222, 184, 135);  burlyWood        = burlywood
    tan              = QColor.fromRgb(210, 180, 140)
    wheat            = QColor.fromRgb(245, 222, 179)
    cornsilk         = QColor.fromRgb(255, 248, 220);  cornSilk         = cornsilk


def _extend_qt_colors():
    """Restore PyQt5-style Qt.* shortcuts removed in PyQt6's strict-enum system.

    PyQt6 moved every Qt enum value under a qualified enum class
    (e.g. Qt.AlignCenter → Qt.AlignmentFlag.AlignCenter). This function
    re-injects the old unqualified shortcuts on the Qt, QPainter, QFont,
    QDialog, QAbstractItemView and QSizePolicy objects so that all existing
    model code continues to work without modification.

    It also injects custom SGColors constants (Qt.orange, Qt.lightGreen, …).

    Called once at import time of SGExtensions, which is imported early in every
    mainClasses file, before any class default-parameter expressions are evaluated.
    """
    def _patch(obj, enum_class, names):
        for n in names:
            if hasattr(enum_class, n):
                setattr(obj, n, getattr(enum_class, n))

    # ── Qt.GlobalColor shortcuts (Qt.black, Qt.white, …) ─────────────────────
    _patch(Qt, Qt.GlobalColor, [
        'color0', 'color1', 'black', 'white',
        'darkGray', 'gray', 'lightGray',
        'red', 'green', 'blue', 'cyan', 'magenta', 'yellow',
        'darkRed', 'darkGreen', 'darkBlue',
        'darkCyan', 'darkMagenta', 'darkYellow',
        'transparent',
    ])

    # ── Qt.AlignmentFlag ──────────────────────────────────────────────────────
    _patch(Qt, Qt.AlignmentFlag, [
        'AlignLeft', 'AlignRight', 'AlignHCenter', 'AlignVCenter',
        'AlignTop', 'AlignBottom', 'AlignCenter', 'AlignJustify',
        'AlignAbsolute', 'AlignLeading', 'AlignTrailing', 'AlignBaseline',
    ])

    # ── Qt.BrushStyle / Qt.PenStyle ───────────────────────────────────────────
    _patch(Qt, Qt.BrushStyle, [
        'NoBrush', 'SolidPattern', 'Dense1Pattern', 'Dense2Pattern',
        'Dense3Pattern', 'Dense4Pattern', 'Dense5Pattern', 'Dense6Pattern',
        'Dense7Pattern', 'HorPattern', 'VerPattern', 'CrossPattern',
        'BDiagPattern', 'FDiagPattern', 'DiagCrossPattern',
        'LinearGradientPattern', 'RadialGradientPattern',
        'ConicalGradientPattern', 'TexturePattern',
    ])
    _patch(Qt, Qt.PenStyle, [
        'NoPen', 'SolidLine', 'DashLine', 'DotLine',
        'DashDotLine', 'DashDotDotLine', 'CustomDashLine',
    ])

    # ── Qt.ContextMenuPolicy ──────────────────────────────────────────────────
    _patch(Qt, Qt.ContextMenuPolicy, [
        'NoContextMenu', 'DefaultContextMenu', 'ActionsContextMenu',
        'CustomContextMenu', 'PreventContextMenu',
    ])

    # ── Qt.Orientation ────────────────────────────────────────────────────────
    _patch(Qt, Qt.Orientation, ['Horizontal', 'Vertical'])

    # ── Qt.AspectRatioMode / Qt.TransformationMode ────────────────────────────
    _patch(Qt, Qt.AspectRatioMode, [
        'IgnoreAspectRatio', 'KeepAspectRatio', 'KeepAspectRatioByExpanding',
    ])
    _patch(Qt, Qt.TransformationMode, ['FastTransformation', 'SmoothTransformation'])

    # ── Qt.MouseButton ────────────────────────────────────────────────────────
    _patch(Qt, Qt.MouseButton, [
        'NoButton', 'LeftButton', 'RightButton', 'MiddleButton',
        'BackButton', 'ForwardButton', 'AllButtons',
    ])

    # ── Qt.KeyboardModifier ───────────────────────────────────────────────────
    _patch(Qt, Qt.KeyboardModifier, [
        'NoModifier', 'ShiftModifier', 'ControlModifier', 'AltModifier',
        'MetaModifier', 'KeypadModifier', 'GroupSwitchModifier',
    ])

    # ── Qt.ItemFlag ───────────────────────────────────────────────────────────
    _patch(Qt, Qt.ItemFlag, [
        'NoItemFlags', 'ItemIsSelectable', 'ItemIsEditable',
        'ItemIsDragEnabled', 'ItemIsDropEnabled', 'ItemIsUserCheckable',
        'ItemIsEnabled', 'ItemIsAutoTristate', 'ItemNeverHasChildren',
        'ItemIsUserTristate',
    ])

    # ── Qt.CheckState ─────────────────────────────────────────────────────────
    _patch(Qt, Qt.CheckState, ['Unchecked', 'PartiallyChecked', 'Checked'])

    # ── Qt.ItemDataRole ───────────────────────────────────────────────────────
    _patch(Qt, Qt.ItemDataRole, [
        'DisplayRole', 'DecorationRole', 'EditRole', 'ToolTipRole',
        'StatusTipRole', 'WhatsThisRole', 'SizeHintRole', 'FontRole',
        'TextAlignmentRole', 'BackgroundRole', 'ForegroundRole',
        'CheckStateRole', 'UserRole',
    ])

    # ── Qt.DockWidgetArea ─────────────────────────────────────────────────────
    _patch(Qt, Qt.DockWidgetArea, [
        'LeftDockWidgetArea', 'RightDockWidgetArea',
        'TopDockWidgetArea', 'BottomDockWidgetArea',
        'AllDockWidgetAreas', 'NoDockWidgetArea',
    ])

    # ── Qt.ConnectionType ─────────────────────────────────────────────────────
    _patch(Qt, Qt.ConnectionType, [
        'AutoConnection', 'DirectConnection', 'QueuedConnection',
        'BlockingQueuedConnection', 'UniqueConnection',
    ])

    # ── Qt.WindowType ─────────────────────────────────────────────────────────
    _patch(Qt, Qt.WindowType, [
        'Widget', 'Window', 'Dialog', 'Sheet', 'Drawer', 'Popup',
        'Tool', 'SplashScreen', 'Desktop', 'SubWindow',
        'FramelessWindowHint', 'WindowTitleHint', 'WindowSystemMenuHint',
        'WindowMinimizeButtonHint', 'WindowMaximizeButtonHint',
        'WindowMinMaxButtonsHint', 'WindowCloseButtonHint',
        'WindowContextHelpButtonHint', 'WindowStaysOnTopHint',
        'WindowStaysOnBottomHint', 'CustomizeWindowHint',
        'WindowTransparentForInput',
    ])

    # ── Qt.ScrollBarPolicy ────────────────────────────────────────────────────
    _patch(Qt, Qt.ScrollBarPolicy, [
        'ScrollBarAsNeeded', 'ScrollBarAlwaysOff', 'ScrollBarAlwaysOn',
    ])

    # ── Qt.CursorShape ────────────────────────────────────────────────────────
    _patch(Qt, Qt.CursorShape, [
        'ArrowCursor', 'UpArrowCursor', 'CrossCursor', 'WaitCursor',
        'IBeamCursor', 'SizeVerCursor', 'SizeHorCursor', 'SizeBDiagCursor',
        'SizeFDiagCursor', 'SizeAllCursor', 'BlankCursor', 'SplitVCursor',
        'SplitHCursor', 'PointingHandCursor', 'ForbiddenCursor',
        'OpenHandCursor', 'ClosedHandCursor', 'WhatsThisCursor', 'BusyCursor',
        'DragMoveCursor', 'DragCopyCursor', 'DragLinkCursor',
    ])

    # ── Qt.WidgetAttribute (Qt.WA_*) ──────────────────────────────────────────
    _patch(Qt, Qt.WidgetAttribute, [
        'WA_TranslucentBackground', 'WA_NoSystemBackground',
        'WA_OpaquePaintEvent', 'WA_TransparentForMouseEvents',
        'WA_DeleteOnClose', 'WA_Hover', 'WA_MouseTracking',
        'WA_ShowWithoutActivating', 'WA_StyledBackground',
        'WA_AcceptTouchEvents',
    ])

    # ── QPainter: RenderHint and CompositionMode shortcuts ────────────────────
    _patch(QPainter, QPainter.RenderHint, [
        'Antialiasing', 'TextAntialiasing', 'SmoothPixmapTransform',
        'VerticalSubpixelPositioning', 'LosslessImageRendering',
    ])
    _patch(QPainter, QPainter.CompositionMode, [
        'CompositionMode_SourceOver', 'CompositionMode_DestinationOver',
        'CompositionMode_Clear', 'CompositionMode_Source',
        'CompositionMode_Destination', 'CompositionMode_SourceIn',
        'CompositionMode_DestinationIn', 'CompositionMode_SourceOut',
        'CompositionMode_DestinationOut', 'CompositionMode_SourceAtop',
        'CompositionMode_DestinationAtop', 'CompositionMode_Xor',
        'CompositionMode_Plus', 'CompositionMode_Multiply',
        'CompositionMode_Screen', 'CompositionMode_Overlay',
        'CompositionMode_Darken', 'CompositionMode_Lighten',
        'CompositionMode_ColorDodge', 'CompositionMode_ColorBurn',
        'CompositionMode_HardLight', 'CompositionMode_SoftLight',
        'CompositionMode_Difference', 'CompositionMode_Exclusion',
        'RasterOp_SourceOrDestination',
    ])

    # ── QFont: Weight shortcuts ───────────────────────────────────────────────
    _patch(QFont, QFont.Weight, [
        'Thin', 'ExtraLight', 'Light', 'Normal', 'Medium',
        'DemiBold', 'Bold', 'ExtraBold', 'Black',
    ])

    # ── QDialog: DialogCode shortcuts ─────────────────────────────────────────
    _patch(QDialog, QDialog.DialogCode, ['Accepted', 'Rejected'])

    # ── QAbstractItemView: SelectionMode and SelectionBehavior shortcuts ──────
    _patch(QAbstractItemView, QAbstractItemView.SelectionMode, [
        'NoSelection', 'SingleSelection', 'MultiSelection',
        'ExtendedSelection', 'ContiguousSelection',
    ])
    _patch(QAbstractItemView, QAbstractItemView.SelectionBehavior, [
        'SelectItems', 'SelectRows', 'SelectColumns',
    ])

    # ── QSizePolicy: Policy shortcuts ─────────────────────────────────────────
    _patch(QSizePolicy, QSizePolicy.Policy, [
        'Fixed', 'Minimum', 'Maximum', 'Preferred', 'Expanding',
        'MinimumExpanding', 'Ignored',
    ])

    # ── QPalette: ColorRole shortcuts ─────────────────────────────────────────
    _patch(QPalette, QPalette.ColorRole, [
        'Window', 'WindowText', 'Base', 'AlternateBase', 'Text',
        'Button', 'ButtonText', 'BrightText', 'Highlight', 'HighlightedText',
        'Link', 'LinkVisited', 'Light', 'Midlight', 'Dark', 'Mid', 'Shadow',
        'ToolTipBase', 'ToolTipText', 'PlaceholderText', 'Accent',
    ])
    # QPalette.Background was deprecated in Qt5 and removed in Qt6 → alias to Window
    setattr(QPalette, 'Background', QPalette.ColorRole.Window)
    setattr(QPalette, 'Foreground', QPalette.ColorRole.WindowText)

    # ── QRegion: RegionType shortcuts ─────────────────────────────────────────
    _patch(QRegion, QRegion.RegionType, ['Rectangle', 'Ellipse'])

    # ── QTextEdit: LineWrapMode shortcuts ─────────────────────────────────────
    _patch(QTextEdit, QTextEdit.LineWrapMode, [
        'NoWrap', 'WidgetWidth', 'FixedPixelWidth', 'FixedColumnWidth',
    ])

    # ── QTextOption: WrapMode shortcuts ───────────────────────────────────────
    _patch(QTextOption, QTextOption.WrapMode, [
        'NoWrap', 'WordWrap', 'ManualWrap', 'WrapAnywhere',
        'WrapAtWordBoundaryOrAnywhere',
    ])

    # ── Qt.DropAction shortcuts ────────────────────────────────────────────────
    _patch(Qt, Qt.DropAction, [
        'CopyAction', 'MoveAction', 'LinkAction', 'ActionMask', 'IgnoreAction',
    ])

    # ── QMessageBox.Icon shortcuts ─────────────────────────────────────────────
    _patch(QMessageBox, QMessageBox.Icon, [
        'NoIcon', 'Information', 'Warning', 'Critical', 'Question',
    ])

    # ── QMessageBox.StandardButton shortcuts ───────────────────────────────────
    _patch(QMessageBox, QMessageBox.StandardButton, [
        'Ok', 'Cancel', 'Save', 'Discard', 'Yes', 'No', 'Retry', 'Ignore',
        'SaveAll', 'NoButton', 'Help', 'Open', 'Apply', 'Close', 'Abort', 'RestoreDefaults',
    ])

    # ── Qt.FocusPolicy shortcuts ───────────────────────────────────────────────
    _patch(Qt, Qt.FocusPolicy, [
        'NoFocus', 'TabFocus', 'ClickFocus', 'StrongFocus', 'WheelFocus',
    ])

    # ── Qt.TextInteractionFlag shortcuts ───────────────────────────────────────
    _patch(Qt, Qt.TextInteractionFlag, [
        'NoTextInteraction', 'TextSelectableByMouse', 'TextSelectableByKeyboard',
        'LinksAccessibleByMouse', 'LinksAccessibleByKeyboard', 'TextEditable',
    ])

    # ── Qt.Corner shortcuts ────────────────────────────────────────────────────
    _patch(Qt, Qt.Corner, [
        'TopLeftCorner', 'TopRightCorner', 'BottomLeftCorner', 'BottomRightCorner',
    ])

    # ── QHeaderView.ResizeMode shortcuts ───────────────────────────────────────
    _patch(QHeaderView, QHeaderView.ResizeMode, [
        'Interactive', 'Stretch', 'ResizeToContents', 'Fixed',
    ])

    # ── QStandardItem.ItemType shortcuts ───────────────────────────────────────
    _patch(QStandardItem, QStandardItem.ItemType, [
        'Type', 'UserType',
    ])

    # ── Custom SGColors (Qt.orange, Qt.lightGreen, Qt.pink, …) ───────────────
    for name, value in vars(SGColors).items():
        if not name.startswith('_') and isinstance(value, QColor):
            setattr(Qt, name, value)


# Initialize the color extensions
_extend_qt_colors()

# Utilities

def getResourceBasePath(base_path=None):
    """
    Return a base path for reading resources.
    - If base_path is provided, it is used as-is.
    - In PyInstaller mode, use sys._MEIPASS.
    - Otherwise, use the project root (parent of mainClasses).
    """
    if base_path is not None:
        return Path(base_path)
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS)
    return Path(__file__).resolve().parent.parent

# @CATEGORY: GET
def getResourcePath(relative_path=None, base_path=None):
    """
    Resolve a resource path that works in dev and exported exe.
    
    Args:
        relative_path (str, optional): Path relative to the project root (or base_path).
            Example: "examples/syntax_examples/images".
        base_path (str or Path, optional): Custom base path override.
    
    Returns:
        Path: Absolute path to the resource folder or file.

    Example:
        # Get a path that works in dev or exe
        images_dir = getResourcePath("examples/syntax_examples/images")
    """
    base = getResourceBasePath(base_path)
    if relative_path in (None, ""):
        return base
    rel = Path(relative_path)
    if rel.is_absolute():
        return rel
    return base / rel

# @CATEGORY: GET
def listImagePaths(paths, extensions=None, base_path=None):
    """
    Collect image paths from one or more directories.

    Args:
        paths (str | Path | list[str | Path]): Directory or list of directories to scan.
        extensions (tuple[str], optional): Glob patterns. Defaults to common image extensions.
        base_path (str | Path, optional): Base path for relative dirs (uses getResourceBasePath by default).

    Returns:
        list[Path]: List of matching image paths (may be empty).
    """
    if extensions is None:
        extensions = ("*.png", "*.jpg", "*.jpeg", "*.gif", "*.webp", "*.svg")
    if isinstance(paths, (str, Path)):
        paths = [paths]

    results = []
    for p in paths:
        if isinstance(p, str):
            dir_path = getResourcePath(p, base_path=base_path)
        else:
            dir_path = Path(p)

        if not dir_path.exists():
            continue

        for ext in extensions:
            results.extend(dir_path.glob(ext))

    return results

# @CATEGORY: DO
def copyValue(source_att, target_att):
    """
    Build a callable that copies an attribute value on an entity.
    
    Usage:
        Cells.newModelAction(copyValue("bufferState", "state"))
    """
    def _action(aEntity):
        aEntity.copyValue(source_att, target_att)
    return _action

# @CATEGORY: DO
def fillTransparentAreas(pixmap, fillColor):
    """
    Fill transparent areas of a QPixmap with a given color.
    
    This utility function creates a new pixmap with transparent areas filled
    with the specified color, useful for ensuring images have solid backgrounds.
    
    Args:
        pixmap: QPixmap image with potential transparent areas
        fillColor: QColor to fill transparent areas with
        
    Returns:
        QPixmap: New pixmap with transparent areas filled, or original pixmap if None/invalid
    """
    from PyQt6.QtGui import QPainter

    if pixmap is None or pixmap.isNull():
        return pixmap

    filled_pixmap = QPixmap(pixmap.size())
    filled_pixmap.fill(fillColor)

    painter = QPainter(filled_pixmap)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
    painter.drawPixmap(0, 0, pixmap)
    painter.end()
    
    return filled_pixmap

# @CATEGORY: GET
def first_value(d, default=None):
    """
    Return the first value of a dictionary according to insertion order.
    - Does not materialize a list (O(1) extra memory).
    - Returns `default` if the dictionary is empty.

    :param d: dictionary to read from
    :param default: value to return if dict is empty (default: None)
    :return: the first value or `default` if empty
    """
    return next(iter(d.values()), default)


# @CATEGORY: GET
def first_key(d, default=None):
    """
    Return the first key of a dictionary according to insertion order.
    - O(1) extra memory.
    - Returns `default` if the dictionary is empty.

    :param d: dictionary to read from
    :param default: value to return if dict is empty (default: None)
    :return: the first key or `default` if empty
    """
    return next(iter(d), default)


# @CATEGORY: GET
def first_item(d, default=None):
    """
    Return the first (key, value) pair of a dictionary according to insertion order.
    - O(1) extra memory.
    - Returns `default` if the dictionary is empty.

    :param d: dictionary to read from
    :param default: value to return if dict is empty (default: None)
    :return: the first (key, value) tuple or `default` if empty
    """
    return next(iter(d.items()), default)


# @CATEGORY: DO
def execute_callable_with_entity(callable_func, entity=None):
    """
    Execute a callable function with appropriate arguments based on its signature.
    - If callable has 0 arguments: execute with no arguments
    - If callable has 1 argument: execute with the provided entity
    - If callable has more than 1 argument: raise ValueError
    
    This utility method is used by SGModelAction and SGActivate to handle
    lambda functions with different argument counts.
    
    :param callable_func: The callable function to execute
    :param entity: The entity to pass as argument (if callable expects 1 argument)
    :raises ValueError: If callable has more than 1 argument
    """
    if not callable(callable_func):
        raise TypeError("First argument must be callable")
    
    # Count the number of arguments
    nbArguments = callable_func.__code__.co_argcount
    if nbArguments == 0:
        callable_func()  # Execute with no arguments
    elif nbArguments == 1:
        callable_func(entity)  # Execute with entity argument
    else:
        raise ValueError(f"Callable must have 0 or 1 arguments, got {nbArguments}")


def normalize_type_name(type_name):
    """
    Normalize a agent or cell type name to a string, handling both string and SGAgentType or SGCellType inputs.
    
    This utility method extracts the entity name from SGAgentType or SGCellType objects
    or returns the string as-is for string inputs.
    
    :param type_name: Either a string type name or an SGAgentType or SGCellType object
    :return: The normalized agent or cell type name as a string
    """
    from mainClasses.SGEntityType import SGAgentType, SGCellType
    if isinstance(type_name, SGAgentType) or isinstance(type_name, SGCellType):
        return type_name.name
    return type_name


# @CATEGORY: DO
def generate_color_gradient(color1, color2=None, steps: int = 10, reverse_gradient=False, mapping=None, as_dict=False, as_ranges=False):
    """
    Generate a color gradient as a list of QColor objects, a dict (mapping mode), or a list of (start, end, color) ranges.

    Modes
    -----
    1) Basic mode (no mapping):
       - Two colors: gradient from color1 → color2 with `steps` samples.
       - Single color (color2 is None): gradient light → color1 → dark (never pure white/black).
         Extremes are trimmed to keep the reference hue visible.

    2) Mapping mode (with `mapping`):
       - mapping = {"values": [...], "value_min": x, "value_max": y}
       - If two colors: each value is mapped linearly between color1 and color2.
       - If single color: each value is mapped along light → color1 → dark.
       - reverse_gradient flips the mapping (i.e., t → 1-t).

    Output
    ------
    - Default: list[QColor]
    - as_dict=True: dict {value: QColor}  (mapping mode only)
    - as_ranges=True: list[(start, end, QColor)] with the last end = float('inf') (mapping mode only)
      Ranges are: [vmin, v1), [v1, v2), ..., [v_last, inf)

    Accepted color formats
    ----------------------
    QColor, color name ("red"), hex "#RRGGBB[AA]", (R,G,B) or (R,G,B,A), Qt.GlobalColor (e.g., Qt.red)

    Examples
    --------
    generate_color_gradient("green", steps=6)
    generate_color_gradient("red", "blue", steps=8)
    generate_color_gradient("red", "blue", mapping={"values":[0,50,100], "value_min":0, "value_max":100}, as_dict=True)
    generate_color_gradient("green", mapping={"values":[1,3,5], "value_min":0, "value_max":7}, as_ranges=True)
    """
    from PyQt6.QtGui import QColor
    from PyQt6.QtCore import Qt

    # --- robust converter ---
    def to_qcolor(value) -> QColor:
        if isinstance(value, QColor):
            return value
        if value is None:
            return None
        if isinstance(value, str):
            q = QColor(value)
            if q.isValid():
                return q
        if isinstance(value, (tuple, list)):
            return QColor(*value)

        # Qt.GlobalColor enum (e.g., Qt.red, Qt.GlobalColor.red) or QRgb int
        try:
            q = QColor(value)
            if q.isValid():
                return q
        except Exception:
            pass

        raise TypeError(f"Unsupported color type: {type(value)} ({value!r})")

    color1 = to_qcolor(color1)
    color2 = to_qcolor(color2) if color2 is not None else None

    # === MAPPING MODE ===
    if mapping is not None:
        values = mapping.get("values")
        vmin = mapping.get("value_min")
        vmax = mapping.get("value_max")

        if not isinstance(values, (list, tuple)):
            raise ValueError("mapping['values'] must be a list or tuple")
        if vmin is None or vmax is None:
            raise ValueError("mapping must contain 'value_min' and 'value_max'")
        if color2 is not None:
            colors = []
            for v in ([vmin]+values if as_ranges else values):
                val = max(min(v, vmax), vmin)  # clamp
                proportion = 0.0 if vmax == vmin else (val - vmin) / (vmax - vmin)
                r = color1.red()   + (color2.red()   - color1.red())   * proportion
                g = color1.green() + (color2.green() - color1.green()) * proportion
                b = color1.blue()  + (color2.blue()  - color1.blue())  * proportion
                colors.append(QColor(int(r), int(g), int(b)))
        else:
            # Add one color with mapping mode functionality
            # raise ValueError("one color with mapping mode yet to be implemented")
            # --- One color with mapping mode ---
            n = len(values)
            extra_steps = n + (3 if as_ranges else 2)
            mid_index = extra_steps // 2

            tmp_colors = []
            # white → color1
            for i in range(mid_index):
                r = 255 + (color1.red() - 255) * i / (mid_index - 1)
                g = 255 + (color1.green() - 255) * i / (mid_index - 1)
                b = 255 + (color1.blue() - 255) * i / (mid_index - 1)
                tmp_colors.append(QColor(int(r), int(g), int(b)))

            # color1 → black
            for i in range(mid_index, extra_steps):
                r = color1.red() * (1 - (i - mid_index) / (extra_steps - mid_index - 1))
                g = color1.green() * (1 - (i - mid_index) / (extra_steps - mid_index - 1))
                b = color1.blue() * (1 - (i - mid_index) / (extra_steps - mid_index - 1))
                tmp_colors.append(QColor(int(r), int(g), int(b)))

            # remove pure white and pure black
            colors = tmp_colors[1:-1]

        if reverse_gradient:
            colors.reverse()

        # return dict(zip(values, colors)) if as_dict else colors
        if as_dict:
            return dict(zip(values, colors))
        elif as_ranges:
            # Build len(values)+1 ranges: [vmin, v1), [v1, v2), ..., [v_last, inf)
            ranges = []
            # prev = vmin
            for i in range(len(values) + 1):
                start = values[i-1] if i > 0 else 0
                end = values[i] if i < len(values) else float('inf')
                ranges.append((start, end, colors[i]))
            return ranges
        else:
            return colors

    # === NORMAL MODE (le reste de ta version) ===
    if steps < 2:
        raise ValueError("Number of steps must be at least 2.")

    gradient = []
    if color2 is None:
        # Single color mode – attenuated extremes (white → color1 → black), then remove pure white/black
        extra_steps = steps + 2
        mid_index = extra_steps // 2

        # white → color1
        for i in range(mid_index):
            r = 255 + (color1.red() - 255) * i / (mid_index - 1)
            g = 255 + (color1.green() - 255) * i / (mid_index - 1)
            b = 255 + (color1.blue() - 255) * i / (mid_index - 1)
            gradient.append(QColor(int(r), int(g), int(b)))

        # color1 → black
        for i in range(mid_index, extra_steps):
            r = color1.red() * (1 - (i - mid_index) / (extra_steps - mid_index - 1))
            g = color1.green() * (1 - (i - mid_index) / (extra_steps - mid_index - 1))
            b = color1.blue() * (1 - (i - mid_index) / (extra_steps - mid_index - 1))
            gradient.append(QColor(int(r), int(g), int(b)))

        gradient = gradient[1:-1]  # remove pure white & pure black
    else:
        # color1 → color2
        for i in range(steps):
            t = i / (steps - 1)
            r = color1.red()   + (color2.red()   - color1.red())   * t
            g = color1.green() + (color2.green() - color1.green()) * t
            b = color1.blue()  + (color2.blue()  - color1.blue())  * t
            gradient.append(QColor(int(r), int(g), int(b)))

    if reverse_gradient:
        gradient.reverse()

    return gradient


def serialize_any_object(obj):
    """
    Serialize any object safely for JSON/CSV export.
    
    This function handles any object type by converting it to a string representation.
    
    :param obj: Object to serialize (can be any type)
    :return: Serialized representation of the object
    """
    if hasattr(obj, '__dict__'):
        # For SGE objects, use their own serialization method
        if hasattr(obj, 'getObjectIdentiferForExport'):
            return obj.getObjectIdentiferForExport()
        elif hasattr(obj, 'id'):
            # Fallback for objects with id but no getObjectIdentiferForExport method
            return f"{obj.__class__.__name__}_id_{obj.id}"
        else:
            return str(obj)
    elif isinstance(obj, (list, tuple)):
        return [serialize_any_object(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: serialize_any_object(value) for key, value in obj.items()}
    else:
        return str(obj)


def mapAlignmentStringToQtFlags(alignment_str):
    """
    Map alignment string to Qt alignment flags.
    
    This utility function converts alignment string values (e.g., 'left', 'center', 'right')
    to Qt alignment flag combinations suitable for use with QLabel, QTextEdit, etc.
    
    Args:
        alignment_str (str): Alignment string ('left', 'right', 'center', 'hcenter', 
                           'top', 'bottom', 'vcenter', 'justify')
    
    Returns:
        Qt.AlignmentFlag or None: Qt alignment flags combination, or None if invalid
    """
    if not isinstance(alignment_str, str):
        return None
    
    AF = Qt.AlignmentFlag
    a = alignment_str.lower()
    if a == 'left':
        return AF.AlignLeft | AF.AlignVCenter
    if a == 'right':
        return AF.AlignRight | AF.AlignVCenter
    if a in ('center', 'hcenter'):
        return AF.AlignHCenter | AF.AlignVCenter
    if a == 'top':
        return AF.AlignTop | AF.AlignHCenter
    if a == 'bottom':
        return AF.AlignBottom | AF.AlignHCenter
    if a == 'vcenter':
        return AF.AlignVCenter | AF.AlignHCenter
    if a == 'justify':
        return AF.AlignJustify
    return None


def position_dialog_to_right(dialog, parent=None):
    """
    Position a dialog to the right of a parent window.
    
    This utility function positions a dialog window to the right edge of a parent window,
    with automatic adjustment if the dialog would overflow the screen boundaries.
    
    :param dialog: The dialog widget to position (QDialog, QColorDialog, etc.)
    :param parent: The parent window to position relative to. If None, attempts to find parent
                   from dialog.parent() or dialog.model (if available). If still None, no positioning is done.
    """
    from PyQt6.QtWidgets import QWidget, QApplication

    try:
        if parent is None:
            parent = dialog.parent() if isinstance(dialog.parent(), QWidget) else None
        if parent is None and hasattr(dialog, 'model') and isinstance(dialog.model, QWidget):
            parent = dialog.model
        if parent is None:
            return

        pg = parent.frameGeometry() if hasattr(parent, 'frameGeometry') else parent.geometry()
        target_x = pg.right()
        target_y = pg.top()

        # Qt6: QApplication.desktop() removed — use screenAt() / primaryScreen()
        screen = QApplication.screenAt(parent.mapToGlobal(parent.rect().topLeft()))
        if screen is None:
            screen = QApplication.primaryScreen()
        available = screen.availableGeometry()

        w = dialog.width()
        h = dialog.height()

        if target_x + w > available.right():
            target_x = max(available.left(), available.right() - w)
        if target_y + h > available.bottom():
            target_y = max(available.top(), available.bottom() - h)

        dialog.move(target_x, target_y)
    except Exception:
        pass