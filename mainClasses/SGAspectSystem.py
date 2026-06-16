"""
SGAspectSystem - Hierarchical symbology system for entities.

This module provides a unified visual representation framework for all entities:
- Unified SGAspect for all visual properties (color, border, text, opacity, etc.)
- Symbologies with category, gradient, interval, and rule-based support
- Hierarchical resolution (Entity instance → Type-specific → Default)
- Grouping of symbologies across entity types (automatic or manual)

Class hierarchy:
- SGSymbology: Complete visual symbology (maps values or rules to SGAspect)
- SGSymbologyGroup: Unified group of symbologies (auto or manual modes)
- SGAspectResolver: Hierarchical resolution engine
"""

from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt


class SGSymbology:
    """
    Represents a complete visual symbology for entities.

    A symbology maps entity attribute values (or computed rules) to complete visual styles (SGAspect).
    Supports three patterns:
    1. Category: {value: SGAspect} for discrete mappings
    2. Rule-based: rule_function(entity) → SGAspect for complex logic
    3. Gradient/Interval: (handled via mapping with interpolation/classification)
    """

    def __init__(self, name, mapping=None, rule_function=None):
        """
        Args:
            name (str): Symbology name (e.g., 'Health', 'Owner', 'Status')
            mapping (dict, optional): {value: SGAspect} for category/gradient/interval types
            rule_function (callable, optional): function(entity) → SGAspect for rule-based
        """
        self.name = name
        self.mapping = mapping or {}  # {value: SGAspect}
        self.rule_function = rule_function  # callable(entity) → SGAspect
        self.interpolation = None  # 'linear', 'log', 'exp', 'sigmoid' (for gradients, Phase 3)
        self.classification_method = None  # 'quantile', 'equidistant', 'jenks', 'manual' (Phase 3)

    def resolve_aspect(self, entity=None, attribute_value=None):
        """
        Resolve which SGAspect applies to this entity/value.

        Args:
            entity (optional): Entity instance (required for rule_function)
            attribute_value (optional): Attribute value (for category/gradient lookup)

        Returns:
            SGAspect or None
        """
        # Pattern 1: Rule-based symbology (highest priority)
        if self.rule_function and entity:
            try:
                return self.rule_function(entity)
            except Exception:
                return None

        # Pattern 2: Category/Gradient/Interval (value lookup)
        if attribute_value is not None:
            # Check if any aspect has apply_if condition
            has_apply_if = entity and any(
                hasattr(aspect, 'apply_if') and aspect.apply_if
                for aspect in self.mapping.values()
                if isinstance(aspect, dict) is False
            )

            # Exact match: check if applies based on apply_if conditions
            if attribute_value in self.mapping:
                matched_aspect = self.mapping[attribute_value]
                # If no apply_if conditions, return exact match immediately
                if not has_apply_if:
                    return matched_aspect
                # If has apply_if and this aspect applies, return it
                if hasattr(matched_aspect, 'is_applicable') and matched_aspect.is_applicable(entity):
                    return matched_aspect
                # If exact match exists but doesn't apply, continue to search all applying aspects

            # If no exact match and interpolation is enabled, interpolate
            if self.interpolation and len(self.mapping) > 0 and not has_apply_if:
                try:
                    return self._interpolate_aspect(attribute_value)
                except Exception:
                    pass

            # For classifications (discrete classes), map value to appropriate class boundary
            # Find the largest key <= the value (with small tolerance for floating point)
            if getattr(self, 'is_classification', False) and len(self.mapping) > 0 and not has_apply_if:
                try:
                    numeric_keys = sorted([k for k in self.mapping.keys() if isinstance(k, (int, float))])
                    if numeric_keys:
                        # Find largest key that is <= attribute_value (or very close)
                        tolerance = 1e-6
                        for key in reversed(numeric_keys):
                            if key <= attribute_value + tolerance:
                                return self.mapping[key]
                        # If value is below all keys, use the first key
                        return self.mapping[numeric_keys[0]]
                except Exception:
                    pass

            # For nominal symbologies with apply_if conditions, search for first applying aspect
            # This handles cases where aspects have conditional application based on entity attributes
            if has_apply_if:
                for aspect in self.mapping.values():
                    # Filter out special keys like __max_value__
                    if isinstance(aspect, dict) or not hasattr(aspect, 'is_applicable'):
                        continue
                    # Return first aspect that applies (apply_if condition is true)
                    if aspect.is_applicable(entity):
                        return aspect

        return None

    def _interpolate_aspect(self, value):
        """
        Interpolate an SGAspect for a value between two mapping points.

        Supports: 'linear', 'log', 'exp', 'sigmoid'

        Returns:
            SGAspect with interpolated properties
        """
        # Get sorted mapping keys (must be numeric)
        try:
            keys = sorted([k for k in self.mapping.keys() if isinstance(k, (int, float))])
        except Exception:
            return None

        if len(keys) < 2:
            return None

        # Find the two points to interpolate between
        lower_key = None
        upper_key = None

        for i, key in enumerate(keys):
            if key <= value:
                lower_key = key
            if key > value and upper_key is None:
                upper_key = key
                break

        if lower_key is None or upper_key is None:
            # Value is outside the range, return nearest
            if value < keys[0]:
                return self.mapping[keys[0]]
            if value > keys[-1]:
                return self.mapping[keys[-1]]
            return None

        # Calculate interpolation factor (0-1)
        lower_aspect = self.mapping[lower_key]
        upper_aspect = self.mapping[upper_key]

        # Linear interpolation
        if self.interpolation == 'linear' or self.interpolation is None:
            t = (value - lower_key) / (upper_key - lower_key)
        # Log interpolation
        elif self.interpolation == 'log':
            t = (value - lower_key) / (upper_key - lower_key)
            t = t ** 0.5  # Square root for log-like behavior
        # Exp interpolation
        elif self.interpolation == 'exp':
            t = (value - lower_key) / (upper_key - lower_key)
            t = t ** 2  # Square for exponential-like behavior
        else:
            t = (value - lower_key) / (upper_key - lower_key)

        t = max(0, min(1, t))  # Clamp to 0-1

        return self._blend_aspects(lower_aspect, upper_aspect, t)

    def _blend_aspects(self, aspect_a, aspect_b, t):
        """
        Blend two aspects with interpolation factor t (0-1).

        Returns a new SGAspect with blended properties.
        """
        from mainClasses.SGAspect import SGAspect

        blended = SGAspect()

        # Blend colors
        if aspect_a.background_color and aspect_b.background_color:
            color_a = QColor(aspect_a.background_color) if isinstance(aspect_a.background_color, str) else aspect_a.background_color
            color_b = QColor(aspect_b.background_color) if isinstance(aspect_b.background_color, str) else aspect_b.background_color
            blended_color = self._blend_colors(color_a, color_b, t)
            blended.background_color = blended_color
        else:
            blended.background_color = aspect_a.background_color or aspect_b.background_color

        # Blend borders
        if aspect_a.border_color and aspect_b.border_color:
            border_a = QColor(aspect_a.border_color) if isinstance(aspect_a.border_color, str) else aspect_a.border_color
            border_b = QColor(aspect_b.border_color) if isinstance(aspect_b.border_color, str) else aspect_b.border_color
            blended_border = self._blend_colors(border_a, border_b, t)
            blended.border_color = blended_border
        else:
            blended.border_color = aspect_a.border_color or aspect_b.border_color

        # Copy other properties from aspect_a (could be extended to interpolate size, etc.)
        blended.border_size = aspect_a.border_size or aspect_b.border_size
        blended.text_content = aspect_a.text_content or aspect_b.text_content
        blended.text_color = aspect_a.text_color or aspect_b.text_color

        return blended

    @staticmethod
    def _blend_colors(color_a, color_b, t):
        """Blend two QColor objects with interpolation factor t (0-1)."""
        r = int(color_a.red() * (1 - t) + color_b.red() * t)
        g = int(color_a.green() * (1 - t) + color_b.green() * t)
        b = int(color_a.blue() * (1 - t) + color_b.blue() * t)
        a = int(color_a.alpha() * (1 - t) + color_b.alpha() * t)
        return QColor(r, g, b, a)

    def __repr__(self):
        pattern = "rule-based" if self.rule_function else "category"
        return f"SGSymbology({self.name}, {pattern}, {len(self.mapping)} entries)"


class SGSymbologyGroup:
    """
    Unified group for organizing symbologies in two modes:

    MODE 1 - AUTOMATIC (cross-entity): Same-named symbologies across types
        When multiple entity types define symbology with same name,
        automatically creates a group to activate them together.
        Example:
            Cell.newSymbology("health", {...})
            Agent.newSymbology("health", {...})
            → Auto-creates SGSymbologyGroup("Health")

    MODE 2 - MANUAL (thematic): User-defined groups with different names
        Modeler explicitly groups symbologies with different names
        to create visualization themes.
        Example:
            model.newSymbologyGroup("EconomyView", ["Wealth", "Trade", "Production"])
            → Creates group combining multiple symbologies

    Both modes activate the same way: group.activate(model)
    """

    def __init__(self, name, symbology_names=None, is_manual=False):
        """
        Args:
            name (str): Group name (e.g., 'Health', 'EconomyView')
            symbology_names (list, optional): Symbology names for manual mode
            is_manual (bool): True for manual thematic groups, False for auto cross-entity
        """
        self.name = name
        self.is_manual = is_manual
        self.symbology_names = symbology_names or []  # For manual mode
        self.symbologies_by_type = {}  # For automatic cross-entity mode

    def add_symbology(self, entity_type_name, symbology):
        """Add a symbology to this group.

        Args:
            entity_type_name (str): Name of the entity type (e.g., 'Cell', 'Agent')
            symbology (SGSymbology): The symbology to add
        """
        self.symbologies_by_type[entity_type_name] = symbology

    def get_symbology_for_type(self, entity_type_name):
        """Get the symbology for a specific entity type.

        Args:
            entity_type_name (str): Name of the entity type

        Returns:
            SGSymbology or None
        """
        return self.symbologies_by_type.get(entity_type_name)

    def get_all_entity_types(self):
        """Get all entity types in this group.

        Returns:
            List[str]: Entity type names
        """
        return list(self.symbologies_by_type.keys())

    def get_all_symbologies(self):
        """Get all symbologies in this group.

        Returns:
            List[SGSymbology]
        """
        return list(self.symbologies_by_type.values())

    def activate(self, model):
        """Activate this group on the model.

        MODE 1 (automatic): Activates all cross-entity symbologies for their types
        MODE 2 (manual): Activates all named symbologies globally

        Args:
            model (SGModel): The model to activate on
        """
        if self.is_manual:
            # Manual mode: activate symbologies by name across all types that have them
            for symbology_name in self.symbology_names:
                if hasattr(model, 'active_symbologies_by_type'):
                    for entity_type in model.getAllEntityTypes():
                        if symbology_name in entity_type.symbologies:
                            model.active_symbologies_by_type[entity_type.name] = symbology_name
                            entity_type.displaySymbology(symbology_name)
        else:
            # Automatic mode: activate by type
            for entity_type_name, symbology in self.symbologies_by_type.items():
                if hasattr(model, 'active_symbologies_by_type'):
                    model.active_symbologies_by_type[entity_type_name] = symbology.name

    def __repr__(self):
        if self.is_manual:
            return f"SGSymbologyGroup({self.name}, manual, symbologies={self.symbology_names})"
        else:
            types = ', '.join(self.get_all_entity_types())
            return f"SGSymbologyGroup({self.name}, cross-entity, types=[{types}])"


class SGAspectResolver:
    """
    Resolves complete visual styling (SGAspect) using hierarchical lookup.

    Resolution order:
    1. Entity instance symbology override (highest priority)
    2. Type-specific symbology from group
    3. Base symbology (lowest priority)

    Returns complete SGAspect with all visual properties (color, border, text, etc.).
    """

    @staticmethod
    def resolve_aspect(entity, symbology_name, attribute):
        """
        Resolve the complete visual aspect (SGAspect) for an entity.

        Hierarchical resolution:
        1. Entity.instance_aspects[symbology_name] (instance override)
        2. Model.symbology_groups[symbology_name] for entity.type
        3. Model.symbologies[symbology_name] (base)
        4. None (no symbology found)

        Args:
            entity: Entity instance with .type, .model, .instance_aspects
            symbology_name (str): Name of symbology to resolve
            attribute (str): Attribute name (for value lookup in mapping)

        Returns:
            SGAspect or None
        """
        attr_value = entity.value(attribute) if hasattr(entity, 'value') else None

        # 1. Try entity instance override first
        if hasattr(entity, 'instance_aspects') and symbology_name in entity.instance_aspects:
            symbology = entity.instance_aspects[symbology_name]
            aspect = symbology.resolve_aspect(entity=entity, attribute_value=attr_value)
            if aspect:
                return aspect

        # 2. Try type-specific symbology from group
        if hasattr(entity, 'model') and hasattr(entity.model, 'symbology_groups'):
            if symbology_name in entity.model.symbology_groups:
                group = entity.model.symbology_groups[symbology_name]
                symbology = group.get_symbology_for_type(entity.type.name)
                if symbology:
                    aspect = symbology.resolve_aspect(entity=entity, attribute_value=attr_value)
                    if aspect:
                        return aspect

        # 3. Fallback to base symbology
        if hasattr(entity, 'model') and hasattr(entity.model, 'symbologies'):
            if symbology_name in entity.model.symbologies:
                symbology = entity.model.symbologies[symbology_name]
                aspect = symbology.resolve_aspect(entity=entity, attribute_value=attr_value)
                if aspect:
                    return aspect

        return None

    @staticmethod
    def resolve_color(entity, symbology_name, attribute, default_color=None):
        """
        Resolve color from a symbology (convenience method).

        Args:
            entity: Entity instance
            symbology_name (str): Symbology name
            attribute (str): Attribute name for value lookup
            default_color: Default color if not found

        Returns:
            QColor or None
        """
        aspect = SGAspectResolver.resolve_aspect(entity, symbology_name, attribute)
        if aspect and hasattr(aspect, 'background_color'):
            color_value = aspect.background_color
            if isinstance(color_value, QColor):
                return color_value
            elif color_value:
                return QColor(color_value)
        return default_color

    @staticmethod
    def resolve_border(entity, symbology_name, attribute, default_color=None, default_width=1):
        """
        Resolve border (color + width) from a symbology (convenience method).

        Args:
            entity: Entity instance
            symbology_name (str): Symbology name
            attribute (str): Attribute name for value lookup
            default_color: Default border color
            default_width (int): Default border width

        Returns:
            dict: {'color': QColor, 'width': int}
        """
        aspect = SGAspectResolver.resolve_aspect(entity, symbology_name, attribute)
        if aspect:
            color = aspect.border_color if hasattr(aspect, 'border_color') else default_color
            width = aspect.border_size if hasattr(aspect, 'border_size') else default_width
            if isinstance(color, QColor):
                return {'color': color, 'width': width}
            elif color:
                return {'color': QColor(color), 'width': width}
        return {'color': default_color, 'width': default_width}

    @staticmethod
    def get_symbology_group(model, group_name):
        """Get a symbology group by name.

        Args:
            model: The SGModel instance
            group_name (str): Name of the group to retrieve

        Returns:
            SGSymbologyGroup or None
        """
        if hasattr(model, 'symbology_groups') and group_name in model.symbology_groups:
            return model.symbology_groups[group_name]
        return None
