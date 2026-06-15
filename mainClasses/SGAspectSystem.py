"""
SGAspectSystem - Hierarchical symbology system for entities.

This module provides a unified visual representation framework for all entities:
- Unified SGAspect for all visual properties (color, border, text, opacity, etc.)
- Symbologies with category, gradient, interval, and rule-based support
- Hierarchical resolution (Entity instance → Type-specific → Default)
- Grouping of symbologies across entity types
- Aspect views for pre-configured visual representations

Class hierarchy:
- SGSymbology: Complete visual symbology (maps values or rules to SGAspect)
- SGSymbologyGroup: Collection of same-named symbologies from different entity types
- SGAspectView: Named group of symbologies to display together
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
        if attribute_value is not None and attribute_value in self.mapping:
            return self.mapping[attribute_value]

        return None

    def __repr__(self):
        pattern = "rule-based" if self.rule_function else "category"
        return f"SGSymbology({self.name}, {pattern}, {len(self.mapping)} entries)"


class SGSymbologyGroup:
    """
    Represents a group of symbologies with the same name across different entity types.

    When multiple entity types (Cell, Agent, Tile) define a symbology with the same name,
    they automatically form a group. This allows activating a visual representation
    globally across all entity types that have it.

    Example:
        Cell.newSymbology("health", {100: green, 50: red})
        Agent.newSymbology("health", {100: green, 50: red})
        → Automatically creates SGSymbologyGroup("Health")
        → Contains: Cell.Health and Agent.Health
    """

    def __init__(self, name):
        """
        Args:
            name (str): Group name (e.g., 'Health', 'Owner')
        """
        self.name = name
        self.symbologies_by_type = {}  # {entity_type_name: SGSymbology}

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

    def __repr__(self):
        types = ', '.join(self.get_all_entity_types())
        return f"SGSymbologyGroup({self.name}, types=[{types}])"


class SGAspectView:
    """
    Represents a view that groups multiple symbologies.

    A view allows users to toggle between different visual representations.
    For example: "HealthView" shows health symbology, "PlayerView" shows health+owner.
    """

    def __init__(self, name, symbologies=None):
        """
        Args:
            name (str): View name (e.g., 'DefaultView', 'PlayerView')
            symbologies (list): List of SGSymbology objects or symbology names
        """
        self.name = name
        self.symbologies = symbologies or []  # Can be SGSymbology objects or names
        self.is_active = True

    def add_symbology(self, symbology):
        """Add a symbology to this view.

        Args:
            symbology (SGSymbology): The symbology to add
        """
        if symbology not in self.symbologies:
            self.symbologies.append(symbology)

    def get_symbologies(self):
        """Get all symbologies in this view.

        Returns:
            List[SGSymbology]
        """
        return self.symbologies

    def __repr__(self):
        return f"SGAspectView({self.name}, {len(self.symbologies)} symbologies)"


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
    def get_active_view(entity_type):
        """Get the currently active aspect view for an entity type.

        Args:
            entity_type: The entity type to check

        Returns:
            SGAspectView or None
        """
        if hasattr(entity_type, 'active_aspect_view'):
            return entity_type.active_aspect_view
        return None

    @staticmethod
    def get_symbologies_for_view(entity_type, view_name):
        """Get all symbologies active in a specific view.

        Args:
            entity_type: The entity type
            view_name (str): Name of the view

        Returns:
            List[SGSymbology]
        """
        if hasattr(entity_type, 'aspect_views') and view_name in entity_type.aspect_views:
            return entity_type.aspect_views[view_name].get_symbologies()
        return []

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
