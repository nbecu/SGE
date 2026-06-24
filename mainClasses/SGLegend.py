from PyQt6.QtGui import *
from PyQt6.QtCore import *
from sqlalchemy import true

from mainClasses.SGGameSpace import SGGameSpace
from mainClasses.SGLegendItem import SGLegendItem


#Class who is responsible of the Legend creation 
class SGLegend(SGGameSpace):
    def __init__(self, parent,backgroundColor=Qt.transparent):
        super().__init__(parent,0,60,0,0,true,backgroundColor)
        self.isLegend=True
        self.isControlPanel=False
        # self.heightOfLabels= 25 #added for CarbonPolis
        self.heightOfLabels= 20 #added for CarbonPolis

    #todo change to the normal way to initialize
    def initialize(self, model, legendName,listOfSymbologies,alwaysDisplayDefaultAgentSymbology=False,borderColor=Qt.black):
        self.id=legendName #todo should be removed as it is managed by the superclass
        self.model=model
        self.alwaysDisplayDefaultAgentSymbology=alwaysDisplayDefaultAgentSymbology
        self.legendItems={}
        # Configure border using gs_aspect instead of self.borderColor
        self.gs_aspect.border_color = borderColor
        self.gs_aspect.border_size = 1
        self.updateWithSymbologies(listOfSymbologies)
        return self
    
    
    def clearAllLegendItems(self):
        for aItem in self.legendItems:
            aItem.deleteLater()
        self.legendItems=[]
        
    def updateWithSymbologies(self,listOfSymbologies):
        self.clearAllLegendItems()
        self.listOfSymbologies=listOfSymbologies
        self.posYOfItems = 0
        anItem=SGLegendItem(self,'Title1',self.id)
        self.legendItems.append(anItem)
        for type, aDictOfSymbology in self.listOfSymbologies.items():
            anItem=SGLegendItem(self,'Title2',type.name)
            self.legendItems.append(anItem)
            # aDictOfSymbology is a dict with keys 'shape' and 'border'
            aShapeSymbology = aDictOfSymbology['shape']
            aBorderSymbology = aDictOfSymbology['border']
            if aShapeSymbology is None and aBorderSymbology is None:
                # Case 1: Default symbology - no POV defined, use entity's default shape color
                # This case corresponds to entities without any POV defined, showing default appearance
                default_aspect = type.get_default_aspect()
                aColor = default_aspect.background_color if default_aspect else type.defaultShapeColor
                anItem=SGLegendItem(self,'symbol','default',type,aColor)
                self.legendItems.append(anItem)
                continue
            if aShapeSymbology is not None:
                # Case 2: Shape symbology - POV for shape color, creates items for each symbol name and color
                # This case corresponds to entities with shape-based POV (e.g., health status affecting color)
                if self.alwaysDisplayDefaultAgentSymbology and type.isAgentType:
                    # Use default symbology for agents without attributes
                    default_aspect = type.get_default_aspect()
                    aColor = default_aspect.background_color if default_aspect else type.defaultShapeColor
                    anItem=SGLegendItem(self,'symbol','default',type,aColor)
                    self.legendItems.append(anItem)

                # Try new symbology system first, then fallback to legacy POV
                # Look for type-specific symbology first, then fallback to plain name
                symbology_key = f"{aShapeSymbology}_{type.name}"
                if symbology_key in self.model.symbologies:
                    symbology = self.model.symbologies[symbology_key]
                elif aShapeSymbology in self.model.symbologies:
                    symbology = self.model.symbologies[aShapeSymbology]
                else:
                    symbology = None

                if symbology is not None:
                    # New symbology system - found it
                    # Get the attribute name associated with this symbology
                    aAtt = self.model.symbology_to_attribute.get(aShapeSymbology, aShapeSymbology)

                    # Check if this is a rule-based symbology (has rule_function)
                    is_rule_based = hasattr(symbology, 'rule_function') and symbology.rule_function is not None

                    # Check if this is a gradient or classification symbology (Phase 3)
                    is_classification = getattr(symbology, 'is_classification', False)
                    is_gradient = getattr(symbology, 'interpolation', None) in ('linear', 'log', 'exp', 'sigmoid') and not is_classification

                    if is_rule_based:
                        # RULE-BASED: Execute rule on entities and show unique aspects
                        unique_aspects = {}  # {label: (color, aspect)}

                        # Collect entities of this type
                        entities = []
                        if type.isAgentType:
                            entities = type.entities if hasattr(type, 'entities') else []
                        else:
                            # For cell types, get all cells from all grids
                            for grid in self.model.getGrids():
                                cell_type = self.model.getCellType(grid)
                                if cell_type == type:
                                    entities = cell_type.entities if hasattr(cell_type, 'entities') else []
                                    break

                        # Execute rule on entities to collect unique aspects
                        seen_colors = {}  # Track colors to deduplicate
                        for entity in entities:
                            aspect = symbology.resolve_aspect(entity=entity)
                            if aspect and hasattr(aspect, 'background_color') and aspect.background_color:
                                color = aspect.background_color
                                if isinstance(color, str):
                                    color = QColor(color)

                                # Use color as key to deduplicate
                                color_key = color.name() if isinstance(color, QColor) else str(color)
                                if color_key not in seen_colors:
                                    seen_colors[color_key] = (color, aspect)

                        # Display unique aspects found
                        if seen_colors:
                            for color_key, (color, aspect) in seen_colors.items():
                                # Use helper to determine label with proper priority
                                label = self._createLegendLabel(aspect, color_key)
                                anItem = SGLegendItem(self, 'symbol', label, type, color, aAtt, color_key)
                                self.legendItems.append(anItem)
                        else:
                            # Fallback if no entities or no colors found
                            anItem = SGLegendItem(self, 'symbol', 'Rule-based', type, Qt.lightGray, aAtt, 'rule-based')
                            self.legendItems.append(anItem)
                    elif is_gradient and len(symbology.mapping) >= 2:
                        # GRADIENT: Create a single gradient bar
                        sorted_values = sorted(symbology.mapping.keys())
                        min_val = sorted_values[0]
                        max_val = sorted_values[-1]

                        # Generate 20 color samples for smooth gradient bar
                        num_samples = 20
                        gradient_colors = []
                        for i in range(num_samples):
                            t = i / (num_samples - 1)  # 0 to 1
                            sample_value = min_val + t * (max_val - min_val)

                            # Resolve aspect at this value (with interpolation)
                            sample_aspect = symbology.resolve_aspect(attribute_value=sample_value)
                            sample_color = sample_aspect.background_color if hasattr(sample_aspect, 'background_color') else Qt.black

                            # Convert string colors to QColor
                            if isinstance(sample_color, str):
                                sample_color = QColor(sample_color)

                            gradient_colors.append(sample_color)

                        # Create single gradient bar item
                        anItem = SGLegendItem(
                            self, 'symbol', '',
                            type, Qt.black, aAtt, min_val,
                            gradient_colors=gradient_colors,
                            gradient_min_value=min_val,
                            gradient_max_value=max_val,
                            gradient_values=sorted_values
                        )
                        self.legendItems.append(anItem)
                        # Gradient bar widget is 35px tall, normal items are 20px (heightOfLabels)
                        # So gradient bar takes ceil(35/20)=2 units, increment by 1 more
                        self.posYOfItems += 1
                    else:
                        # DISCRETE/CLASSIFICATION: Show each class
                        if is_classification:
                            # Show class intervals with proper notation: [min, max)
                            # Last class uses [min, max] to include the maximum value
                            sorted_values = sorted([k for k in symbology.mapping.keys() if k != '__max_value__'])
                            # Get max value from classifier (stored by classify_quantile, etc.)
                            max_class_value = symbology.mapping.get('__max_value__', None)
                            for i, value in enumerate(sorted_values):
                                aspect = symbology.mapping[value]
                                aColor = aspect.background_color if hasattr(aspect, 'background_color') else Qt.black
                                if isinstance(aColor, str):
                                    aColor = QColor(aColor)

                                # Priority: legend_label > generated interval label
                                if getattr(aspect, 'legend_label', None):
                                    label = aspect.legend_label
                                else:
                                    # Format interval label with mathematical notation
                                    if i < len(sorted_values) - 1:
                                        next_value = sorted_values[i + 1]
                                        # [min, max) - min included, max excluded
                                        label = f"[{value:.0f}, {next_value:.0f})"
                                    else:
                                        # [min, max] - last class includes max value
                                        # Use stored max value if available, otherwise use last key
                                        upper_bound = max_class_value if max_class_value is not None else sorted_values[-1]
                                        label = f"[{value:.0f}, {upper_bound:.0f}]"

                                anItem = SGLegendItem(self, 'symbol', label, type, aColor, aAtt, value)
                                self.legendItems.append(anItem)
                        else:
                            # Nominal: Show discrete values (skip __max_value__)
                            for value, aspect in symbology.mapping.items():
                                if value == '__max_value__':
                                    continue
                                aColor = aspect.background_color if hasattr(aspect, 'background_color') else Qt.black
                                if isinstance(aColor, str):
                                    aColor = QColor(aColor)
                                # Use helper to determine label with proper priority
                                label = self._createLegendLabel(aspect, value)
                                anItem = SGLegendItem(self, 'symbol', label, type, aColor, aAtt, value)
                                self.legendItems.append(anItem)
                elif aShapeSymbology in type.povShapeColor:
                    # Legacy POV system
                    aAtt = list(type.povShapeColor[aShapeSymbology].keys())[0]
                    dictSymbolNameAndColor= list(type.povShapeColor[aShapeSymbology].values())[0]
                    for aSymbolName, aColor in dictSymbolNameAndColor.items():
                        anItem=SGLegendItem(self,'symbol',aSymbolName,type,aColor,aAtt,aSymbolName)
                        self.legendItems.append(anItem)
            if aBorderSymbology is not None:
                # Case 3: Border symbology - POV for border color and width, creates items for each symbol name
                # This case corresponds to entities with border-based POV (e.g., ownership or status borders)

                # Try new symbology system first, then fallback to legacy POV
                # Look for type-specific symbology first, then fallback to plain name
                symbology_key = f"{aBorderSymbology}_{type.name}"
                if symbology_key in self.model.symbologies:
                    symbology = self.model.symbologies[symbology_key]
                elif aBorderSymbology in self.model.symbologies:
                    symbology = self.model.symbologies[aBorderSymbology]
                else:
                    symbology = None

                if symbology is not None:
                    # New symbology system - found it
                    # Get the attribute name associated with this symbology
                    aAtt = self.model.symbology_to_attribute.get(aBorderSymbology, aBorderSymbology)

                    # Check if this is a gradient or classification symbology (Phase 3)
                    is_classification = getattr(symbology, 'is_classification', False)
                    is_gradient = getattr(symbology, 'interpolation', None) in ('linear', 'log', 'exp', 'sigmoid') and not is_classification

                    if is_gradient and len(symbology.mapping) >= 2:
                        # GRADIENT: Create a single gradient bar for borders
                        sorted_values = sorted(symbology.mapping.keys())
                        min_val = sorted_values[0]
                        max_val = sorted_values[-1]

                        # Generate 20 color samples for smooth gradient bar
                        num_samples = 20
                        gradient_colors = []
                        for i in range(num_samples):
                            t = i / (num_samples - 1)
                            sample_value = min_val + t * (max_val - min_val)
                            sample_aspect = symbology.resolve_aspect(attribute_value=sample_value)
                            border_color = sample_aspect.border_color if hasattr(sample_aspect, 'border_color') else Qt.black
                            if isinstance(border_color, str):
                                border_color = QColor(border_color)
                            gradient_colors.append(border_color)

                        # Create single gradient bar item for borders
                        anItem = SGLegendItem(
                            self, 'symbol', '',
                            type, nameOfAttribut=aAtt, valueOfAttribut=min_val,
                            isBorderItem=True,
                            gradient_colors=gradient_colors,
                            gradient_min_value=min_val,
                            gradient_max_value=max_val,
                            gradient_values=sorted_values
                        )
                        self.legendItems.append(anItem)
                        # Gradient bar widget is 35px tall, normal items are 20px (heightOfLabels)
                        # So gradient bar takes ceil(35/20)=2 units, increment by 1 more
                        self.posYOfItems += 1
                    else:
                        # DISCRETE/CLASSIFICATION: Show each class
                        if is_classification:
                            # Show class intervals with proper notation: [min, max)
                            # Last class uses [min, max] to include the maximum value
                            sorted_values = sorted([k for k in symbology.mapping.keys() if k != '__max_value__'])
                            max_class_value = symbology.mapping.get('__max_value__', None)
                            for i, value in enumerate(sorted_values):
                                aspect = symbology.mapping[value]
                                border_color = aspect.border_color if hasattr(aspect, 'border_color') else Qt.black
                                if isinstance(border_color, str):
                                    border_color = QColor(border_color)
                                border_size = aspect.border_size if hasattr(aspect, 'border_size') else 1
                                border_info = {'color': border_color, 'width': border_size}

                                # Format interval label with mathematical notation
                                if i < len(sorted_values) - 1:
                                    next_value = sorted_values[i + 1]
                                    # [min, max) - min included, max excluded
                                    label = f"[{value:.0f}, {next_value:.0f})"
                                else:
                                    # [min, max] - last class includes max value
                                    max_value = sorted_values[-1]
                                    label = f"[{value:.0f}, {max_value:.0f}]"

                                anItem = SGLegendItem(self, 'symbol', label, type, nameOfAttribut=aAtt, valueOfAttribut=value, isBorderItem=True, borderColorAndWidth=border_info)
                                self.legendItems.append(anItem)
                        else:
                            # Nominal: Show discrete values (skip __max_value__)
                            for value, aspect in symbology.mapping.items():
                                if value == '__max_value__':
                                    continue
                                border_color = aspect.border_color if hasattr(aspect, 'border_color') else Qt.black
                                if isinstance(border_color, str):
                                    border_color = QColor(border_color)
                                border_size = aspect.border_size if hasattr(aspect, 'border_size') else 1
                                border_info = {'color': border_color, 'width': border_size}
                                anItem = SGLegendItem(self, 'symbol', str(value), type, nameOfAttribut=aAtt, valueOfAttribut=value, isBorderItem=True, borderColorAndWidth=border_info)
                                self.legendItems.append(anItem)
                elif aBorderSymbology in type.povBorderColorAndWidth:
                    # Legacy POV system
                    aPovBorderDef = type.povBorderColorAndWidth.get(aBorderSymbology)
                    aAtt = list(aPovBorderDef.keys())[0]
                    dictSymbolNameAndColorAndWidth= list(aPovBorderDef.values())[0]
                    for aSymbolName, aDictColorAndWidth in dictSymbolNameAndColorAndWidth.items():
                        anItem=SGLegendItem(self,'symbol',aSymbolName,type,nameOfAttribut=aAtt,valueOfAttribut=aSymbolName,isBorderItem=True,borderColorAndWidth=aDictColorAndWidth)
                        self.legendItems.append(anItem)

        for anItem in self.legendItems:
            anItem.adjustSize()  #NEW
            anItem.show()
        self.adjustSize()
        self.updateSizeFromItems()

    def _createLegendLabel(self, aspect, fallback_value):
        """Create legend label with priority: legend_label > text_content > fallback_value.

        Args:
            aspect (SGAspect): The aspect object
            fallback_value: Default value to use if no label found

        Returns:
            str: The label to display in legend
        """
        if aspect and hasattr(aspect, 'legend_label') and aspect.legend_label:
            return aspect.legend_label
        if aspect and hasattr(aspect, 'text_content') and aspect.text_content:
            # Use first line only
            return str(aspect.text_content).split('\n')[0]
        return str(fallback_value)

    def _addLegendItem(self, label, color, entity_type, attribute, value):
        """Add a single legend item with consistent formatting.

        Args:
            label (str): Label to display
            color: Color for the symbol
            entity_type: The entity type
            attribute (str): Attribute name
            value: Value key
        """
        anItem = SGLegendItem(self, 'symbol', label, entity_type, color, attribute, value)
        self.legendItems.append(anItem)

    def showLegendItem(self, typeOfPov, aAttribut, aValue, color, aKeyOfGamespace, added_items, added_colors):
        item_key=aAttribut +' '+ str(aValue)
        if item_key not in added_items and color not in added_colors and color != Qt.transparent:
            self.y=self.y+1
            anItem=SGLegendItem(self,self.model.getGameSpaceByName(aKeyOfGamespace).format,self.y,aAttribut+" "+str(aValue),color,aValue,aAttribut)
            if typeOfPov == "BorderPOV" :
                anItem.border = True
            self.legendItems[aKeyOfGamespace].append(anItem)
            anItem.show()
            added_items.add(item_key)
            added_colors.append(color)


    #Funtion to have the global size of a gameSpace  
    def getSizeXGlobal(self):
        listOfLengths = [len(item.text) for item in self.legendItems]
        listOfLengths.append(len(self.id))
        if len(listOfLengths)==0:
            return 250
        lMax= sorted(listOfLengths,reverse=True)[0]
        return lMax*12+10
    
    def getSizeX_fromAllWidgets(self):
        if self.legendItems:
            widths = []
            for item in self.legendItems:
                try:
                    if hasattr(item, "getRequiredWidth"):
                        w = item.getRequiredWidth()
                    else:
                        w = item.geometry().size().width()
                except Exception:
                    w = 30
                widths.append(w)
            max_width = max(widths) if widths else 30
        else:
            max_width = 30
        return max_width + 10
    
    def getSizeYGlobal(self):
        # Use posYOfItems instead of len(legendItems) to account for gradient bars
        # which take multiple heightOfLabels units
        return (self.heightOfLabels)*(self.posYOfItems+1)

    def updateSizeFromItems(self):
        """Update widget size based on current items."""
        w = max(0, self.getSizeX_fromAllWidgets())
        h = max(0, self.getSizeYGlobal()+3)
        try:
            self.sizeXGlobal = w
            self.sizeYGlobal = h
        except Exception:
            pass
        self.setMinimumSize(w, h)
        self.resize(w, h)
    
    #Funtion to handle the zoom
    def zoomIn(self):
        """IN PROGRESS"""
        return True
    
    def zoomOut(self):
        """IN PROGRESS"""
        return True 
        
    #Drawing the Legend
    def paintEvent(self,event):
        painter = QPainter()
        painter.begin(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        # Background: prefer image, else color with transparency
        self._drawBackgroundImage(painter)
        if not self.getBackgroundImagePixmap():
            bg = self.gs_aspect.getBackgroundColorValue()
            if bg.alpha() == 0:
                painter.setBrush(Qt.NoBrush)
            else:
                painter.setBrush(QBrush(bg, Qt.SolidPattern))
        # Border with style mapping
        pen = QPen(self.gs_aspect.getBorderColorValue(), self.gs_aspect.getBorderSize())
        style_map = {
            'solid': Qt.SolidLine,
            'dotted': Qt.DotLine,
            'dashed': Qt.DashLine,
            'double': Qt.SolidLine,
            'groove': Qt.SolidLine,
            'ridge': Qt.SolidLine,
            'inset': Qt.SolidLine,
        }
        bs = getattr(self.gs_aspect, 'border_style', None)
        if isinstance(bs, str) and bs.lower() in style_map:
            pen.setStyle(style_map[bs.lower()])
        painter.setPen(pen)

        # Compute and cache sizes for consistency
        w = max(0, self.getSizeX_fromAllWidgets())
        h = max(0, self.getSizeYGlobal()+3)
        try:
            self.sizeXGlobal = w
            self.sizeYGlobal = h
        except Exception:
            pass

        radius = getattr(self.gs_aspect, 'border_radius', None) or 0
        if radius > 0:
            painter.drawRoundedRect(0, 0, max(0, w-1), max(0, h-1), radius, radius)
        else:
            painter.drawRect(0, 0, max(0, w-1), max(0, h-1))

        painter.end()

    # =========================
    # STYLE/APPLY HOOKS
    # =========================
    def applyContainerAspectStyle(self):
        """Avoid QSS cascade; rely on paintEvent for container rendering."""
        pass

    def onTextAspectsChanged(self):
        # Trigger repaint of all items so they use current aspects
        try:
            for it in self.legendItems:
                if hasattr(it, 'update'):
                    it.update()
        except Exception:
            pass
        self.update()

    # ============================================================================
    # MODELER METHODS
    # ============================================================================
    
    # ============================================================================
    # NEW/ADD/SET METHODS
    # ============================================================================
    
    def setBorderColor(self, color):
        """
        Set the border color of the legend.
        
        Args:
            color (QColor or Qt.GlobalColor): The border color
        """
        super().setBorderColor(color)
        
    def setBorderSize(self, size):
        """
        Set the border size of the legend.
        
        Args:
            size (int): The border size in pixels
        """
        super().setBorderSize(size)

    #obsolete function
    # def checkSpecie(self,item_key,items):
    #     for legendItem in items:
    #         if item_key in legendItem.text:
    #             return False
    #     return True
