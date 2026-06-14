"""
Tests for background image features (Items A+B):
- Scaling modes (stretch/cover/contain)
- Zoom integration
- Viewport calculation helper
- Transparent cells alignment
"""
import pytest
from PyQt6.QtGui import QPixmap, QColor
from PyQt6.QtCore import Qt
from mainClasses.SGSGE import SGModel


@pytest.fixture
def model_with_bg_grid(qt_app):
    """Model with grid that has a background image"""
    m = SGModel(600, 600)
    # Create a simple test image (100x100 red pixmap)
    pixmap = QPixmap(100, 100)
    pixmap.fill(Qt.red)

    cell_def = m.newCellsOnGrid(5, 5, "square", size=50, gap=5,
                                backgroundImage=pixmap)
    yield m, cell_def
    m.close()


@pytest.fixture
def model_with_transparent_cells(qt_app):
    """Model with grid containing transparent cells (for alignment testing)"""
    m = SGModel(600, 600)
    # Create test image
    pixmap = QPixmap(100, 100)
    pixmap.fill(Qt.red)

    cell_def = m.newCellsOnGrid(6, 6, "square", size=40, gap=10,
                                backgroundImage=pixmap)

    # Set up transparent cells (like checkerboard pattern)
    cell_def.setEntities("type", "terrain")
    for x in range(1, 7):
        for y in range(1, 7):
            if (x + y) % 2 == 0:
                cell_def.getEntity(x, y).setValue("type", "vide")

    # POV: terrain opaque, vide transparent
    cell_def.newPov("vue", "type", {
        "terrain": Qt.green,
        "vide": Qt.transparent,
    })

    yield m, cell_def
    m.close()


# ---------------------------------------------------------------------------
# Background Image Modes
# ---------------------------------------------------------------------------

class TestBackgroundImageModes:
    """Test the three background image scaling modes"""

    def test_stretch_mode_default(self, model_with_bg_grid):
        """Stretch should be the default mode"""
        m, cell_def = model_with_bg_grid
        grid = cell_def.grid
        assert grid.gs_aspect.background_image_mode == 'stretch'

    def test_set_stretch_mode(self, model_with_bg_grid):
        """Test explicitly setting stretch mode"""
        m, cell_def = model_with_bg_grid
        grid = cell_def.grid
        grid.setStyle({'background_image_mode': 'stretch'})
        assert grid.gs_aspect.background_image_mode == 'stretch'

    def test_set_cover_mode(self, model_with_bg_grid):
        """Test setting cover mode via setStyle"""
        m, cell_def = model_with_bg_grid
        grid = cell_def.grid
        grid.setStyle({'background_image_mode': 'cover'})
        assert grid.gs_aspect.background_image_mode == 'cover'

    def test_set_contain_mode(self, model_with_bg_grid):
        """Test setting contain mode via setStyle"""
        m, cell_def = model_with_bg_grid
        grid = cell_def.grid
        grid.setStyle({'background_image_mode': 'contain'})
        assert grid.gs_aspect.background_image_mode == 'contain'

    def test_mode_persists_after_set(self, model_with_bg_grid):
        """Mode should persist across multiple calls"""
        m, cell_def = model_with_bg_grid
        grid = cell_def.grid
        grid.setStyle({'background_image_mode': 'cover'})
        grid.setStyle({'border_color': Qt.black})  # Other style change
        assert grid.gs_aspect.background_image_mode == 'cover'


# ---------------------------------------------------------------------------
# Background Image Zoom
# ---------------------------------------------------------------------------

class TestBackgroundImageZoom:
    """Test background image zoom integration"""

    def test_zoom_enabled_by_default(self, model_with_bg_grid):
        """Background image zoom should be enabled by default"""
        m, cell_def = model_with_bg_grid
        grid = cell_def.grid
        assert grid.gs_aspect.background_image_zoom_enabled == True

    def test_disable_background_zoom(self, model_with_bg_grid):
        """Test disabling background image zoom"""
        m, cell_def = model_with_bg_grid
        grid = cell_def.grid
        grid.setBackgroundImageZoom(False)
        assert grid.gs_aspect.background_image_zoom_enabled == False

    def test_enable_background_zoom(self, model_with_bg_grid):
        """Test enabling background image zoom"""
        m, cell_def = model_with_bg_grid
        grid = cell_def.grid
        grid.setBackgroundImageZoom(False)
        grid.setBackgroundImageZoom(True)
        assert grid.gs_aspect.background_image_zoom_enabled == True

    def test_set_zoom_via_style(self, model_with_bg_grid):
        """Test setting zoom enabled via setStyle"""
        m, cell_def = model_with_bg_grid
        grid = cell_def.grid
        grid.setStyle({'background_image_zoom_enabled': False})
        assert grid.gs_aspect.background_image_zoom_enabled == False


# ---------------------------------------------------------------------------
# Viewport Calculation Helper
# ---------------------------------------------------------------------------

class TestViewportCalculation:
    """Test the _calculateBackgroundImageViewport() helper"""

    def test_viewport_stretch_mode_no_zoom(self, model_with_bg_grid):
        """Viewport in stretch mode at zoom=1.0 should be full image"""
        m, cell_def = model_with_bg_grid
        grid = cell_def.grid
        pixmap = grid.getBackgroundImagePixmap()

        src_x, src_y, src_w, src_h = grid._calculateBackgroundImageViewport(
            pixmap, grid.width(), grid.height(), 'stretch', zoom=1.0
        )

        # In stretch mode at zoom=1.0, should show full image
        assert src_x == 0
        assert src_y == 0
        assert src_w == pixmap.width()
        assert src_h == pixmap.height()

    def test_viewport_stretch_mode_with_zoom(self, model_with_bg_grid):
        """Viewport in stretch mode with zoom should scale proportionally"""
        m, cell_def = model_with_bg_grid
        grid = cell_def.grid
        pixmap = grid.getBackgroundImagePixmap()

        src_1_0_w = pixmap.width()
        src_x, src_y, src_w, src_h = grid._calculateBackgroundImageViewport(
            pixmap, grid.width(), grid.height(), 'stretch', zoom=1.5,
            viewportX=0, viewportY=0
        )

        # With zoom=1.5, visible width should be smaller
        assert src_w < src_1_0_w

    def test_viewport_cover_mode_no_zoom(self, model_with_bg_grid):
        """Viewport in cover mode should have offset due to centering"""
        m, cell_def = model_with_bg_grid
        grid = cell_def.grid
        pixmap = grid.getBackgroundImagePixmap()

        src_x, src_y, src_w, src_h = grid._calculateBackgroundImageViewport(
            pixmap, grid.width(), grid.height(), 'cover', zoom=1.0
        )

        # Cover mode crops from center, so offsets should exist
        # (actual values depend on aspect ratio)
        assert src_x >= 0
        assert src_y >= 0
        assert src_w > 0
        assert src_h > 0

    def test_viewport_contain_mode_no_zoom(self, model_with_bg_grid):
        """Viewport in contain mode should show full image"""
        m, cell_def = model_with_bg_grid
        grid = cell_def.grid
        pixmap = grid.getBackgroundImagePixmap()

        src_x, src_y, src_w, src_h = grid._calculateBackgroundImageViewport(
            pixmap, grid.width(), grid.height(), 'contain', zoom=1.0
        )

        # Contain mode shows full image
        assert src_x == 0
        assert src_y == 0
        assert src_w == pixmap.width()
        assert src_h == pixmap.height()

    def test_viewport_zoom_changes_region(self, model_with_bg_grid):
        """Zooming should change the viewport region"""
        m, cell_def = model_with_bg_grid
        grid = cell_def.grid
        pixmap = grid.getBackgroundImagePixmap()

        # Get viewport at zoom=1.0
        src_1_0_x, src_1_0_y, src_1_0_w, src_1_0_h = grid._calculateBackgroundImageViewport(
            pixmap, grid.width(), grid.height(), 'stretch', zoom=1.0,
            viewportX=0, viewportY=0
        )

        # Get viewport at zoom=1.5 (simulating zoom in)
        src_1_5_x, src_1_5_y, src_1_5_w, src_1_5_h = grid._calculateBackgroundImageViewport(
            pixmap, grid.width(), grid.height(), 'stretch', zoom=1.5,
            viewportX=0, viewportY=0
        )

        # Width/height should decrease when zooming in (showing less of image)
        assert src_1_5_w < src_1_0_w
        assert src_1_5_h < src_1_0_h

    def test_viewport_respects_bounds(self, model_with_bg_grid):
        """Viewport should never exceed image bounds"""
        m, cell_def = model_with_bg_grid
        grid = cell_def.grid
        pixmap = grid.getBackgroundImagePixmap()

        for zoom in [0.8, 1.0, 1.2, 1.5, 2.0]:
            for mode in ['stretch', 'cover', 'contain']:
                src_x, src_y, src_w, src_h = grid._calculateBackgroundImageViewport(
                    pixmap, grid.width(), grid.height(), mode, zoom=zoom
                )

                # Should never exceed image bounds
                assert src_x >= 0, f"Mode {mode}, zoom {zoom}: src_x={src_x}"
                assert src_y >= 0, f"Mode {mode}, zoom {zoom}: src_y={src_y}"
                assert src_x + src_w <= pixmap.width(), \
                    f"Mode {mode}, zoom {zoom}: src_x + src_w = {src_x + src_w} > {pixmap.width()}"
                assert src_y + src_h <= pixmap.height(), \
                    f"Mode {mode}, zoom {zoom}: src_y + src_h = {src_y + src_h} > {pixmap.height()}"


# ---------------------------------------------------------------------------
# Transparent Cells Alignment
# ---------------------------------------------------------------------------

class TestTransparentCellsAlignment:
    """Test that transparent cells align with grid background during zoom"""

    def test_transparent_cells_exist(self, model_with_transparent_cells):
        """Verify test fixture creates transparent cells"""
        m, cell_def = model_with_transparent_cells
        grid = cell_def.grid

        # Check that we have both transparent and opaque cells (based on type attribute)
        transparent_count = 0
        opaque_count = 0
        for cell in cell_def.entities:
            cell_type = cell.getValue("type")
            if cell_type == "vide":
                transparent_count += 1
            elif cell_type == "terrain":
                opaque_count += 1

        assert transparent_count > 0, "Should have transparent cells (type='vide')"
        assert opaque_count > 0, "Should have opaque cells (type='terrain')"

    def test_grid_has_background_image(self, model_with_transparent_cells):
        """Verify grid has background image loaded"""
        m, cell_def = model_with_transparent_cells
        grid = cell_def.grid
        assert grid.getBackgroundImagePixmap() is not None

    def test_background_image_mode_can_be_set_with_transparent_cells(self, model_with_transparent_cells):
        """Test that background image mode works with transparent cells"""
        m, cell_def = model_with_transparent_cells
        grid = cell_def.grid

        for mode in ['stretch', 'cover', 'contain']:
            grid.setStyle({'background_image_mode': mode})
            assert grid.gs_aspect.background_image_mode == mode

    def test_viewport_calculation_with_transparent_cells(self, model_with_transparent_cells):
        """Test viewport calculation works with grid containing transparent cells"""
        m, cell_def = model_with_transparent_cells
        grid = cell_def.grid
        pixmap = grid.getBackgroundImagePixmap()

        # Should not raise any exceptions
        src_x, src_y, src_w, src_h = grid._calculateBackgroundImageViewport(
            pixmap, grid.width(), grid.height(), 'stretch', zoom=1.0
        )

        assert src_w > 0
        assert src_h > 0
