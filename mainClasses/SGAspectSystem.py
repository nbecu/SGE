"""
SGAspectSystem - Hierarchical aspect/symbology system for entities.

This module provides a structured way to manage visual representations (symbologies)
of entities with support for:
- Multiple visual properties (color, border, icon, pattern, transparency)
- Hierarchical resolution (Entity → EntityType → Default)
- Grouping of symbologies across entity types
- Grouping of symbologies into views
- Both color and border (color + width) representations

Class hierarchy:
- SGVisualAspect: Single visual property (color, border, icon, etc.)
- SGSymbology: Collection of aspects (managed at Model level)
- SGSymbologyGroup: Collection of same-named symbologies from different entity types
- SGAspectView: Named group of symbologies to display together
- SGAspectResolver: Hierarchical resolution engine
"""

from PyQt6.QtGui import QColor
from PyQt6.QtCore import Qt


class SGVisualAspect:
    """
    Represents a single visual property for entities.

    A visual aspect maps entity attribute values to visual symbols
    (e.g., health=100 → green, health=50 → yellow, health=0 → red).
    """

    def __init__(self, symbol_type, attribute, mapping):
        """
        Args:
            symbol_type (str): Type of symbol ('color', 'border', 'icon', 'pattern', 'transparency')
            attribute (str): Entity attribute name (e.g., 'health', 'owner')
            mapping (dict): Value-to-symbol mapping
                - For 'color': {value: QColor}
                - For 'border': {value: {color: QColor, width: int}}
                - For 'icon': {value: filepath}
        """
        self.symbol_type = symbol_type
        self.attribute = attribute
        self.mapping = mapping or {}

    def get_symbol(self, value, default=None):
        """Get the symbol for a given attribute value.

        Args:
            value: The attribute value to look up
            default: Default symbol if value not found

        Returns:
            The symbol (color, dict, icon, etc.) or default
        """
        return self.mapping.get(value, default)

    def __repr__(self):
        return f"SGVisualAspect({self.symbol_type}, {self.attribute})"


class SGSymbology:
    """
    Represents a complete visual representation (symbology) for an entity.

    A symbology is a named collection of visual aspects. For example,
    "Health" symbology might combine a color aspect and a border aspect.
    """

    def __init__(self, name):
        """
        Args:
            name (str): Symbology name (e.g., 'Health', 'Owner', 'Status')
        """
        self.name = name
        self.aspects = []  # List[SGVisualAspect]

    def add_aspect(self, aspect):
        """Add a visual aspect to this symbology.

        Args:
            aspect (SGVisualAspect): The aspect to add
        """
        self.aspects.append(aspect)

    def get_aspect_by_type(self, symbol_type):
        """Get the first aspect of a given type.

        Args:
            symbol_type (str): The type of aspect to find

        Returns:
            SGVisualAspect or None
        """
        for aspect in self.aspects:
            if aspect.symbol_type == symbol_type:
                return aspect
        return None

    def get_all_aspects_by_type(self, symbol_type):
        """Get all aspects of a given type.

        Args:
            symbol_type (str): The type of aspect to find

        Returns:
            List[SGVisualAspect]
        """
        return [a for a in self.aspects if a.symbol_type == symbol_type]

    def __repr__(self):
        return f"SGSymbology({self.name}, {len(self.aspects)} aspects)"


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
    Resolves visual aspects using hierarchical lookup.

    Resolution order:
    1. Entity instance aspects (highest priority)
    2. EntityType aspects
    3. Default aspect (lowest priority)

    This allows entities to override the symbology defined at their type level.
    """

    @staticmethod
    def resolve_color(entity, symbology_name, attribute, default_color=None):
        """Resolve a color from an entity's visual aspects.

        Uses hierarchical resolution: Entity → EntityType → Model → default

        Args:
            entity: The entity to resolve for (has .instance_aspects, .type, .model)
            symbology_name (str): Name of the symbology to look up
            attribute (str): Attribute name to resolve
            default_color: Color to return if not found

        Returns:
            QColor or None
        """
        value = entity.value(attribute) if hasattr(entity, 'value') else None

        # 1. Try entity instance aspects first
        if hasattr(entity, 'instance_aspects') and symbology_name in entity.instance_aspects:
            symbology = entity.instance_aspects[symbology_name]
            aspect = symbology.get_aspect_by_type('color')
            if aspect:
                color = aspect.get_symbol(value)
                if color is not None:
                    return color

        # 2. Try Model-level symbologies (now authoritative source)
        if hasattr(entity, 'model') and hasattr(entity.model, 'symbologies'):
            if symbology_name in entity.model.symbologies:
                symbology = entity.model.symbologies[symbology_name]
                aspect = symbology.get_aspect_by_type('color')
                if aspect:
                    color = aspect.get_symbol(value)
                    if color is not None:
                        return color

        # 3. Return default
        return default_color

    @staticmethod
    def resolve_border(entity, symbology_name, attribute, default_color=None, default_width=1):
        """Resolve a border (color + width) from an entity's visual aspects.

        Uses hierarchical resolution: Entity → Model → default

        Args:
            entity: The entity to resolve for
            symbology_name (str): Name of the symbology to look up
            attribute (str): Attribute name to resolve
            default_color: Color to return if not found
            default_width (int): Width to return if not found

        Returns:
            dict: {'color': QColor, 'width': int}
        """
        value = entity.value(attribute) if hasattr(entity, 'value') else None

        # 1. Try entity instance aspects first
        if hasattr(entity, 'instance_aspects') and symbology_name in entity.instance_aspects:
            symbology = entity.instance_aspects[symbology_name]
            aspect = symbology.get_aspect_by_type('border')
            if aspect:
                border_dict = aspect.get_symbol(value)
                if border_dict is not None:
                    return border_dict

        # 2. Try Model-level symbologies (now authoritative source)
        if hasattr(entity, 'model') and hasattr(entity.model, 'symbologies'):
            if symbology_name in entity.model.symbologies:
                symbology = entity.model.symbologies[symbology_name]
                aspect = symbology.get_aspect_by_type('border')
                if aspect:
                    border_dict = aspect.get_symbol(value)
                    if border_dict is not None:
                        return border_dict

        # 3. Return default
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
