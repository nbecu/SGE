# Symbology System Specification — Complete

**Date:** 2026-06-15  
**Version:** 1.0  
**Status:** SPECIFICATION (implementation Phase 1 Extended + Phase 3+)

---

## 1. Overview

The Symbology System provides a unified visual representation framework for entities in simulation games. It replaces the legacy POV (Point of View) system with a more flexible, feature-rich approach that supports:

- **Discrete mappings** (categories)
- **Continuous gradients** (interpolated colors/styles)
- **Interval classification** (natural breaks, quantiles, etc.)
- **Custom rules** (conditional expressions)
- **Multi-aspect rendering** (color, border, text, image, all together)

---

## 2. Entity Types & Visual Properties

### 2.1 Cells (Grid Elements)

**Definition:** Static grid cells that form the base environment.

**Visual Elements:**

#### Background
- **Visibility:** Display on/off toggle
- **Type:** 
  - Color (hex or RGBA)
  - Texture (predefined pattern)
  - Image (URL or file path)
- **Opacity:** 0 (transparent) to 1 (opaque)
  - Separate from color (RGBA can embed alpha)
  - Allows independent control of transparency

#### Border
- **Visibility:** Display on/off toggle
- **Color:** Hex or RGBA
- **Thickness:** Numeric value (pixels)
- **Style:** Solid, dotted, dashed
- **Opacity:** 0 to 1 (separate from color)
- **Radius:** Corner rounding (pixels)

#### Text/Label
- **Visibility:** Display on/off toggle
- **Content:** 
  - Static text (fixed string)
  - Dynamic (reference to attribute: `{temperature}`, `{name}`)
  - Computed (expressions: `health / 100`)
- **Font:**
  - Family (Arial, Georgia, etc.)
  - Size (pt or px)
  - Color (hex or RGBA)
  - Weight (normal, bold, 100-900)
  - Style (normal, italic, oblique)
- **Layout:**
  - Alignment (left, center, right)
  - Text decoration (none, underline, strikethrough, overline)
  - Opacity (0 to 1)
  - Wrapping behavior

---

### 2.2 Agents (Dynamic Entities)

**Definition:** Moving/interactive entities positioned on cells.

**Visual Elements:**

#### Shape
- **Type:**
  - Circle (diameter)
  - Rectangle (width, height)
  - Polygon (custom coordinates)
  - Icon/SVG (URL or file path)
- **Size:**
  - Width/height (pixels or relative units)
  - Scaling relative to cell

#### Fill (Background)
- **Color, texture, or image** (same as cells)
- **Opacity:** 0 to 1

#### Border
- **Color, thickness, style, opacity** (same as cells)
- **Radius:** Corner rounding

#### Text
- **Content, font, layout** (same as cells)
- Example: Agent name, health value, status indicator

#### Position
- **Relative to cell:** Defined by `SGAgentType.locationInEntity`
- **Offset:** X, Y coordinates within cell bounds

#### Rotation
- **Angle:** Degrees (0-360)
- **Use case:** Direction indicators (arrow pointing to destination)

#### Visibility
- **Boolean or conditional:**
  - Always visible
  - Visible if condition met (e.g., `energy > 0`)
  - Visible for specific players/roles

#### Animation (Future)
- Blinking, color pulsing
- Movement animation
- State-change effects

---

### 2.3 Tiles (Overlay Elements)

**Definition:** Static overlay elements with dual states (e.g., front/back, active/inactive).

**Visual Elements:**

#### Shape
- Rectangle, polygon, icon (same as agents)
- Usually predefined (e.g., square for terrain)

#### Size & Position
- Defined by `SGTileType.positionOnCell` and `SGTileType.defaultsize`
- Fixed or scalable

#### Dual Faces (Recto/Verso)
- **Face 1 (Recto):** Default appearance
- **Face 2 (Verso):** Alternative appearance (toggle-able)
- Each face has: fill, border, text

#### Fill, Border, Text
- Same properties as cells (color, opacity, font, etc.)
- Applied to each face independently

---

## 3. Symbology Types

### 3.1 Category Symbology (Discrete)

**Definition:** Direct mapping of discrete attribute values to visual styles.

**Use Case:**
```
Attribute: land_type
Values: "forest", "water", "city", "agriculture"

Symbology:
  "forest" → green background, dark border
  "water" → blue background, light border
  "city" → gray background, thick black border
  "agriculture" → brown background, thin border
```

**Implementation:**
```python
land_type_map = {
    "forest": SGAspect(background_color="green", border_color="darkgreen", border_size=2),
    "water": SGAspect(background_color="blue", border_color="lightblue", border_size=1),
    "city": SGAspect(background_color="gray", border_color="black", border_size=3),
    "agriculture": SGAspect(background_color="brown", border_color="tan", border_size=1)
}

Land.newSymbology("land_type", land_type_map, name="LandCategory")
```

**Characteristics:**
- No interpolation
- All values must be explicitly defined
- Best for nominal (non-ordered) data

---

### 3.2 Gradient Symbology (Continuous)

**Definition:** Smooth color/style transition across a range of numeric values.

**Use Case:**
```
Attribute: temperature
Range: 0°C (blue) → 50°C (red)

At 0°C: blue (#0000ff)
At 25°C: purple (#8000ff) [interpolated]
At 50°C: red (#ff0000)
```

**Interpolation Methods:**
- **Linear:** Uniform color transition (default)
- **Logarithmic:** More variation in lower ranges
- **Exponential:** More variation in upper ranges
- **Sigmoid:** S-curve for smooth transition with plateaus

**Implementation:**
```python
temperature_gradient = {
    0: SGAspect(background_color="#0000ff"),
    50: SGAspect(background_color="#ff0000")
}

Cell.newSymbology(
    "temperature",
    temperature_gradient,
    name="TemperatureGradient",
    interpolation="linear"
)
```

**Characteristics:**
- Values between key points interpolated automatically
- Smooth visual progression
- Best for continuous numeric data (temperature, humidity, elevation)

---

### 3.3 Interval Symbology (Classification)

**Definition:** Group continuous values into intervals, each with its own style.

**Use Case:**
```
Attribute: pollution_level
Range: 0 to 100

Quantile classification (4 groups, each with ~25 entities):
  0-25:   Green (good)
  25-50:  Yellow (moderate)
  50-75:  Orange (high)
  75-100: Red (severe)
```

**Classification Methods:**

**Equidistant:** Equal-width intervals
```
0-25, 25-50, 50-75, 75-100
```

**Quantile:** Equal count (20% of data per bin)
```
Each interval contains same number of entities
(requires data analysis at runtime)
```

**Natural Breaks (Jenks):** Optimal visual grouping
```
Minimizes variance within groups, maximizes between groups
(computationally expensive, best pre-calculated)
```

**Manual:** User-defined thresholds
```
0-10, 10-30, 30-60, 60-100
(user specifies exact breakpoints)
```

**Implementation:**
```python
pollution_intervals = {
    (0, 25): SGAspect(background_color="green"),
    (25, 50): SGAspect(background_color="yellow"),
    (50, 75): SGAspect(background_color="orange"),
    (75, 100): SGAspect(background_color="red")
}

Cell.newSymbology(
    "pollution_level",
    pollution_intervals,
    name="PollutionIntervals",
    classification_method="quantile"  # or "equidistant", "jenks", "manual"
)
```

**Characteristics:**
- Bridges discrete and continuous
- Better than gradients for data with distinct regimes
- Requires method specification

---

### 3.4 Rule-Based Symbology (Custom Logic)

**Definition:** Complex visual logic using lambda functions or rule functions (similar to `SGSimulationVariable.calcValue()` pattern).

**Use Case 1: Simple Lambda**
```python
# Define style based on single attribute
Cell.newSymbology(
    "health",
    rule_function=lambda entity: SGAspect(
        background_color="green" if entity.getValue("health") > 50 else "red",
        border_size=3 if entity.getValue("health") < 20 else 1
    ),
    name="HealthRules"
)
```

**Use Case 2: Named Function (Multi-Attribute Logic)**
```python
def pollution_water_ratio_rule(entity):
    """Returns SGAspect based on entity's pollution/water ratio"""
    ratio = entity.getValue("pollution") / entity.getValue("water")
    
    if ratio < 0.3:
        return SGAspect(background_color="green", border_color="darkgreen", border_size=1)
    elif ratio < 0.7:
        return SGAspect(background_color="orange", border_color="darkorange", border_size=2)
    else:
        return SGAspect(background_color="red", border_color="darkred", border_size=3)

Cell.newSymbology(
    "environment",
    rule_function=pollution_water_ratio_rule,
    name="PollutionWaterRatio"
)
```

**Use Case 3: Multi-Attribute Conditional**
```python
# Temperature + Humidity determines style
Cell.newSymbology(
    "climate",
    rule_function=lambda e: (
        SGAspect(background_color="red", border_size=3)
        if e.getValue("temperature") > 30 and e.getValue("humidity") < 50
        else (
            SGAspect(background_color="orange", border_size=2)
            if e.getValue("temperature") > 30
            else SGAspect(background_color="blue", border_size=1)
        )
    ),
    name="ClimateRules"
)
```

**Implementation Pattern:**
```python
# Generic signature for rule functions
def rule_function(entity) -> SGAspect:
    """
    Args:
        entity: SGEntity instance with getValue(attribute) method
    
    Returns:
        SGAspect: Visual properties for this entity
    """
    # Your logic here
    return SGAspect(...)

# Register with symbology
Type.newSymbology(
    "attribute",
    rule_function=rule_function,
    name="SymbologyName"
)
```

**Characteristics:**
- Most flexible, most powerful
- Leverages existing `calcValue()` pattern
- Clean, Pythonic API (lambda or function)
- Supports arbitrary complexity
- Best for multi-attribute logic or non-linear mappings
- Dynamic: called at render time for each entity

---

## 4. Symbology Storage & Resolution

### 4.1 Model-Level Storage

```python
Model.symbologies = {
    "Health": SGSymbology(...),
    "Temperature": SGSymbology(...),
    "Status": SGSymbology(...)
}

Model.symbology_groups = {
    "Health": SGSymbologyGroup([Cell, Agent, Tile]),
    "Temperature": SGSymbologyGroup([Cell])
}
```

### 4.2 Hierarchical Resolution

When rendering entity E with active symbology S:

```
1. Check entity.instance_aspects[S]
   ├─ If found, use instance override
   └─ Return resolved SGAspect

2. Check Model.symbology_groups[S].get_symbology_for_type(E.type)
   ├─ Get symbology for this entity type
   ├─ Resolve based on E.attribute_value
   └─ Return resolved SGAspect

3. Check Model.symbologies[S]
   ├─ Fallback to base symbology
   ├─ Resolve based on E.attribute_value
   └─ Return resolved SGAspect

4. Return default SGAspect (transparent, no border)
```

---

## 5. Use Cases & Scenarios

### Scenario 1: Simple Cell Health Display

```python
# Setup
cells.newSymbologyWithBorder(
    "health",
    {
        100: SGAspect(background_color="green", border_size=3),
        50: SGAspect(background_color="orange", border_size=2),
        0: SGAspect(background_color="red", border_size=1)
    }
)

# User interaction
# Menu > GROUPS > Health ✓
# All entity types with "health" symbology activate it
# Cells display with colors matching their health value
```

### Scenario 2: Multi-Interpretation of Same Attribute

```python
# Cell can show health in different ways
cells.newSymbology(
    "health",
    {100: SGAspect(background_color="green"), ...},
    name="HealthColor"  # Explicit name required
)

cells.newSymbology(
    "health",
    {100: SGAspect(border_color="darkgreen", border_size=5), ...},
    name="HealthBorder"  # Different interpretation
)

# Menu now shows:
# > GROUPS
#   - Health (group with multiple types)
# > BY TYPE > Cell
#   - HealthColor (radio)
#   - HealthBorder (radio)
# User can switch between visual interpretations
```

### Scenario 3: Cross-Type Group

```python
# Both cell and agent types share health visualization
cells.newSymbology("health", {...})    # Creates "Health" group
agents.newSymbology("health", {...})   # Joins "Health" group

# Menu > GROUPS > Health activates health symbology for BOTH types
```

### Scenario 4: Dynamic Text with Attribute Reference

```python
cell_text_aspect = SGAspect(
    color="black",
    font="Arial",
    size=10,
    text_content="{health}"  # Dynamic: shows cell's health value
)

cells.newSymbology(
    "health",
    {
        100: SGAspect(background_color="green", text_aspect=cell_text_aspect),
        ...
    }
)

# Rendered cell shows:
# [GREEN BACKGROUND] [TEXT: "100"]
```

---

## 6. Advanced Features (Phase 3+)

### 6.1 Textures & Patterns
```python
wood_texture = SGAspect(
    background_image="textures/wood.png",
    background_image_mode="repeat"
)
```

### 6.2 Animations
```python
pulsing_aspect = SGAspect(
    background_color="red",
    animation="pulse",
    animation_duration=0.5  # seconds
)
```

### 6.3 Conditional Visibility
```python
visible_if_healthy = SGAspect(
    background_color="green",
    visible_if="health > 50"
)
```

### 6.4 Aspect Views (Pre-configured Sets)
```python
health_view = SGAspectView(
    symbologies=["Health", "Stamina", "Energy"],
    description="Shows all health-related attributes"
)

# Menu > Views > Health View
# Activates all 3 symbologies at once
```

---

## 7. API Reference (Phase 1 Extended)

### 7.1 Creating Symbologies

```python
# Category symbology (discrete values)
Type.newSymbology(
    "attribute",
    {value: SGAspect(...), ...},
    name="SymbologyName"  # Required if multiple for same attribute
)

# With border (convenience method)
Type.newSymbologyWithBorder(
    "attribute",
    {value: SGAspect(...), ...},
    border_width=3,
    name="SymbologyName"
)

# Rule-based symbology (lambda or function)
# Pattern 1: Lambda (simple logic)
Type.newSymbology(
    "attribute",
    rule_function=lambda entity: SGAspect(...),
    name="SymbologyName"
)

# Pattern 2: Named function (complex logic)
def my_rule(entity):
    if entity.getValue("health") > 50:
        return SGAspect(background_color="green")
    else:
        return SGAspect(background_color="red")

Type.newSymbology(
    "attribute",
    rule_function=my_rule,
    name="SymbologyName"
)

# Advanced (Phase 3)
# Gradient symbology
Type.newSymbology(
    "attribute",
    {0: SGAspect(...), 100: SGAspect(...)},
    interpolation="linear"
)

# Interval symbology
Type.newSymbology(
    "attribute",
    {(0, 25): SGAspect(...), (25, 50): SGAspect(...), ...},
    classification_method="quantile"
)
```

### 7.2 Instance Overrides

```python
cell.setInstanceSymbology(
    "Health",
    "health",
    {100: SGAspect(background_color="gold")}  # Override for this cell only
)
```

### 7.3 Menu Activation

```python
# Programmatically (testing/automation)
Model.active_symbologies_by_type["Cell"] = "Health"

# Or via UI menu (user clicks)
# GROUPS > Health [✓]
# BY TYPE > Cell > Health [✓]
```

---

## 8. Implementation Roadmap

### Phase 1 Extended: Foundation
- ✅ Use SGAspect instead of SGVisualAspect
- ✅ Support category symbologies
- ✅ Hierarchical resolution
- ✅ Instance overrides
- ✅ Menu UI (already done in Phase 2)

### Phase 2: Complete
- ✅ Menu UI infrastructure
- ✅ Visual rendering
- ✅ Backward compatibility

### Phase 3: Advanced
- ⏭️ Gradient interpolation
- ⏭️ Interval classification (all methods)
- ⏭️ Rule-based symbologies
- ⏭️ Dynamic text content
- ⏭️ Textures & patterns

### Phase 4+: Enhancement
- ⏭️ Animations
- ⏭️ Conditional visibility
- ⏭️ Aspect views
- ⏭️ Export/import symbologies
- ⏭️ Symbology editor UI

---

## 9. Example: Complete Game Setup

```python
# Create game
Model = SGModel(...)
Cells = Model.newCellsOnGrid(10, 10)
Agents = Model.newAgentType("Animal")

# Define symbologies
# 1. Health (categorical)
health_colors = {
    100: SGAspect(background_color="green", border_size=2),
    50: SGAspect(background_color="orange", border_size=2),
    0: SGAspect(background_color="red", border_size=3)
}
Cells.newSymbology("health", health_colors)
Agents.newSymbology("health", health_colors)
# Creates cross-type "Health" group

# 2. Temperature (gradient, future)
temperature_gradient = {
    0: SGAspect(background_color="#0000ff"),
    100: SGAspect(background_color="#ff0000")
}
Cells.newSymbology("temperature", temperature_gradient, 
                   interpolation="linear")

# 3. Owner (category)
owner_map = {
    "Player1": SGAspect(border_color="blue", border_size=3),
    "Player2": SGAspect(border_color="red", border_size=3)
}
Agents.newSymbology("owner", owner_map, name="Owner")

# Menu now shows:
# GROUPS:
#   - Health (checkbox) → activates Health for all types
#   - Owner (checkbox) → activates Owner for Agent only
# 
# BY TYPE:
#   - Cell: Health, Temperature
#   - Agent: Health, Owner
```

---

## 10. Notes & Constraints

- **Opacity:** Can be defined in RGBA colors OR as separate opacity property (for flexibility)
- **Textures:** Require asset management (predefined library or URL references)
- **Dynamic content:** `{attribute_name}` syntax for text substitution
- **Performance:** Large gradients or complex rules may need caching
- **Backward compat:** Old `newPov()` API supported via adapter layer

---

## Status

- **Specification:** Complete ✓
- **Phase 1 Extended (foundation):** ⏭️ Ready to implement
- **Phase 3+ (advanced):** Documented, roadmap clear

For implementation details, see ASPECT_SYSTEM_REFACTORING.md
