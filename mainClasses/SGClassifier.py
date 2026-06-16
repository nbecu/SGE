"""
SGClassifier - Automatic classification of continuous data into intervals.

Supports multiple classification methods:
- equidistant: Equal-width intervals
- quantile: Equal-count intervals (n-tile)
- manual: User-defined thresholds
"""

from mainClasses.SGAspect import SGAspect
from PyQt6.QtGui import QColor


class SGClassifier:
    """Helper class for classifying continuous attribute values into discrete intervals."""

    @staticmethod
    def classify_equidistant(entities, attribute, num_classes=4, colors=None):
        """
        Classify entities into equal-width intervals.

        Args:
            entities (list): List of SGEntity objects
            attribute (str): Attribute name to classify
            num_classes (int): Number of classes (default 4)
            colors (list, optional): List of QColor objects for each class

        Returns:
            dict: {interval_tuple: SGAspect} mapping for symbology
        """
        values = [entity.value(attribute) for entity in entities if entity.value(attribute) is not None]

        if not values:
            return {}

        min_val = min(values)
        max_val = max(values)

        # Generate colors if not provided
        if not colors:
            colors = SGClassifier._generate_colors(num_classes)

        # Create equal-width intervals
        mapping = {}
        interval_width = (max_val - min_val) / num_classes

        for i in range(num_classes):
            lower = min_val + i * interval_width
            upper = lower + interval_width

            # Create interval key (as tuple or as representative value)
            interval_key = lower + interval_width / 2  # Use midpoint as key

            aspect = SGAspect(background_color=colors[i % len(colors)])
            mapping[interval_key] = aspect

        return mapping

    @staticmethod
    def classify_quantile(entities, attribute, num_classes=4, colors=None):
        """
        Classify entities into equal-count intervals (quantiles/n-tiles).

        Args:
            entities (list): List of SGEntity objects
            attribute (str): Attribute name to classify
            num_classes (int): Number of classes (default 4 for quartiles)
            colors (list, optional): List of QColor objects for each class

        Returns:
            dict: {value: SGAspect} mapping for symbology
        """
        values = [entity.value(attribute) for entity in entities if entity.value(attribute) is not None]

        if not values:
            return {}

        # Sort values
        sorted_values = sorted(values)

        # Generate colors if not provided
        if not colors:
            colors = SGClassifier._generate_colors(num_classes)

        # Calculate quantile thresholds
        mapping = {}
        entities_per_class = len(sorted_values) / num_classes

        for i in range(num_classes):
            # Find the value at the quantile boundary
            index = min(int(i * entities_per_class), len(sorted_values) - 1)
            quantile_value = sorted_values[index]

            aspect = SGAspect(background_color=colors[i % len(colors)])
            mapping[quantile_value] = aspect

        return mapping

    @staticmethod
    def classify_manual(thresholds, colors):
        """
        Create a classification with manual thresholds.

        Args:
            thresholds (list): List of threshold values (e.g., [0, 25, 50, 75, 100])
            colors (list): List of QColor objects (length = len(thresholds) - 1)

        Returns:
            dict: {threshold: SGAspect} mapping for symbology

        Example:
            mapping = SGClassifier.classify_manual(
                thresholds=[0, 33, 66, 100],
                colors=[QColor("red"), QColor("yellow"), QColor("green")]
            )
        """
        if len(colors) != len(thresholds) - 1:
            raise ValueError(f"Expected {len(thresholds) - 1} colors for {len(thresholds)} thresholds")

        mapping = {}
        for i, threshold in enumerate(thresholds[:-1]):
            aspect = SGAspect(background_color=colors[i])
            mapping[threshold] = aspect

        return mapping

    @staticmethod
    def _generate_colors(num_classes):
        """Generate a sequence of colors from cool to warm."""
        colors = []

        # Simple gradient: blue → cyan → green → yellow → orange → red
        base_colors = [
            QColor("blue"),
            QColor("cyan"),
            QColor("green"),
            QColor("yellow"),
            QColor("orange"),
            QColor("red"),
        ]

        if num_classes <= len(base_colors):
            # Take evenly spaced colors from the palette
            step = len(base_colors) / num_classes
            for i in range(num_classes):
                index = int(i * step)
                colors.append(base_colors[min(index, len(base_colors) - 1)])
        else:
            # Interpolate more colors
            for i in range(num_classes):
                # Use HSV color space for better gradients
                hue = (360 * i) / num_classes
                colors.append(QColor.fromHsv(int(hue), 200, 255))

        return colors
