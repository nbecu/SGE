"""
Tests for SGE grid neighborhood logic — square and hexagonal grids.
These tests validate that neighbor counts are correct for all boundary/neighborhood combinations.
"""
import pytest
from mainClasses.SGSGE import SGModel


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def square_open(qt_app):
    model = SGModel(400, 300)
    cell_def = model.newCellsOnGrid(8, 7, "square", gap=0, size=40,
                                    neighborhood="moore", boundaries="open")
    yield cell_def
    model.close()


@pytest.fixture
def square_closed(qt_app):
    model = SGModel(400, 300)
    cell_def = model.newCellsOnGrid(8, 7, "square", gap=0, size=40,
                                    neighborhood="moore", boundaries="closed")
    yield cell_def
    model.close()


@pytest.fixture
def square_neumann(qt_app):
    model = SGModel(400, 300)
    cell_def = model.newCellsOnGrid(8, 7, "square", gap=0, size=40,
                                    neighborhood="neumann", boundaries="open")
    yield cell_def
    model.close()


@pytest.fixture
def hex_open(qt_app):
    model = SGModel(400, 300)
    cell_def = model.newCellsOnGrid(8, 7, "hexagonal", gap=0, size=40,
                                    neighborhood="moore", boundaries="open")
    yield cell_def
    model.close()


@pytest.fixture
def hex_closed(qt_app):
    model = SGModel(400, 300)
    cell_def = model.newCellsOnGrid(8, 7, "hexagonal", gap=0, size=40,
                                    neighborhood="moore", boundaries="closed")
    yield cell_def
    model.close()


# ---------------------------------------------------------------------------
# Square grid — open boundaries (toroidal Moore: 8 neighbors everywhere)
# ---------------------------------------------------------------------------

def test_square_open_all_cells_have_8_neighbors(square_open):
    for cell in square_open.entities:
        count = len(cell.getNeighborCells())
        assert count == 8, f"Cell ({cell.xCoord},{cell.yCoord}) has {count} neighbors, expected 8"


def test_square_open_id_consistency(square_open):
    for x, y in [(3, 3), (5, 5), (7, 6)]:
        cell = square_open.getCell(x, y)
        assert cell.getId() == square_open.cellIdFromCoords(x, y), \
            f"ID mismatch at ({x},{y}): getId={cell.getId()}, cellIdFromCoords={square_open.cellIdFromCoords(x, y)}"


# ---------------------------------------------------------------------------
# Square grid — closed boundaries (finite Moore)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("x,y,expected,description", [
    (4, 4, 8, "center"),
    (1, 1, 3, "top-left corner"),
    (8, 1, 3, "top-right corner"),
    (1, 7, 3, "bottom-left corner"),
    (8, 7, 3, "bottom-right corner"),
    (4, 1, 5, "top edge"),
    (4, 7, 5, "bottom edge"),
    (1, 4, 5, "left edge"),
    (8, 4, 5, "right edge"),
])
def test_square_closed_neighbor_counts(square_closed, x, y, expected, description):
    cell = square_closed.getCell(x, y)
    count = len(cell.getNeighborCells())
    assert count == expected, \
        f"{description} ({x},{y}): expected {expected} neighbors, got {count}"


# ---------------------------------------------------------------------------
# Square grid — Neumann (4 neighbors, open boundaries)
# ---------------------------------------------------------------------------

def test_square_neumann_all_cells_have_4_neighbors(square_neumann):
    for cell in square_neumann.entities:
        count = len(cell.getNeighborCells())
        assert count == 4, f"Cell ({cell.xCoord},{cell.yCoord}) has {count} neighbors, expected 4"


# ---------------------------------------------------------------------------
# Hexagonal grid — open boundaries (toroidal: 6 neighbors everywhere)
# ---------------------------------------------------------------------------

def test_hex_open_all_cells_have_6_neighbors(hex_open):
    for cell in hex_open.entities:
        count = len(cell.getNeighborCells())
        assert count == 6, f"Cell ({cell.xCoord},{cell.yCoord}) has {count} neighbors, expected 6"


def test_hex_open_id_consistency(hex_open):
    for x, y in [(3, 3), (5, 5), (7, 6)]:
        cell = hex_open.getCell(x, y)
        assert cell.getId() == hex_open.cellIdFromCoords(x, y), \
            f"ID mismatch at ({x},{y})"


# ---------------------------------------------------------------------------
# Hexagonal grid — closed boundaries (pointy-top, even-r offset)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("x,y,expected,description", [
    (4, 4, 6, "center"),
    (1, 1, 2, "top-left corner"),
    (8, 1, 3, "top-right corner"),
    (1, 7, 2, "bottom-left corner"),
    (8, 7, 3, "bottom-right corner"),
    (4, 1, 4, "top edge"),
    (4, 7, 4, "bottom edge"),
    (1, 4, 5, "left edge"),
    (8, 4, 3, "right edge"),
])
def test_hex_closed_neighbor_counts(hex_closed, x, y, expected, description):
    cell = hex_closed.getCell(x, y)
    count = len(cell.getNeighborCells())
    assert count == expected, \
        f"{description} ({x},{y}): expected {expected} neighbors, got {count}"
