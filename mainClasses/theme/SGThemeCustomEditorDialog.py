from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from mainClasses.SGAspect import SGAspect


class SGThemeCustomEditorDialog(QDialog):
    """
    Editor dialog to tweak gs_aspect (base) and per-text aspects (title1/2/3, text1/2/3),
    and save as a new runtime theme (name + spec dict).
    """

    def __init__(self, model, gameSpace, parent=None, init_theme=None):
        super().__init__(parent)
        self.model = model
        self.gs = gameSpace
        self.init_theme = init_theme.strip() if isinstance(init_theme, str) and init_theme.strip() else None
        self.setWindowTitle("Custom Theme Editor")
        self.resize(720, 560)
        # Snapshot original state for cancel
        self._orig_spec = self._capture_current_gs()
        self._orig_flags = {
            'current_theme_name': getattr(self.gs, 'current_theme_name', None),
            'theme_overridden': getattr(self.gs, 'theme_overridden', False),
        }
        # If asked to initialize from a theme, temporarily apply it AFTER snapshot
        if self.init_theme:
            try:
                if hasattr(self.gs, 'applyTheme'):
                    self.gs.applyTheme(self.init_theme)
            except Exception:
                pass
        self._buildUI()

    def _buildUI(self):
        layout = QVBoxLayout()

        # Context info
        info = QLabel(f"Editing: {self.gs.__class__.__name__} / {getattr(self.gs, 'id', '')}")
        info.setStyleSheet("color: #555;")
        layout.addWidget(info)

        # Theme name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Theme name:"))
        self.name_edit = QLineEdit()
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)

        tabs = QTabWidget()
        tabs.setContentsMargins(0, 0, 0, 0)
        # Minimize padding of the tab pane
        tabs.setStyleSheet("QTabWidget::pane{margin:0px; padding:0px;}")
        tabs.addTab(self._buildBaseTab(), "Container (Background & Border)")
        tabs.addTab(self._buildTextTab(), "Titles & Texts")
        layout.addWidget(tabs)

        # Buttons
        btns = QHBoxLayout()
        btns.addStretch()
        preview_btn = QPushButton("Preview")
        preview_btn.clicked.connect(self._onPreview)
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self._onSave)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(preview_btn)
        btns.addWidget(save_btn)
        btns.addWidget(cancel_btn)
        layout.addLayout(btns)

        self.setLayout(layout)
        # Reduce dialog to its minimum height based on contents
        layout.setSizeConstraint(QLayout.SetFixedSize)
        self.adjustSize()
        
        # Setup automatic preview updates
        self._setupAutoPreview()

    def _buildBaseTab(self):
        w = QWidget()
        form = QFormLayout()
        # Ensure rows and the whole form are aligned to the left/top
        form.setLabelAlignment(Qt.AlignLeft)
        form.setFormAlignment(Qt.AlignLeft | Qt.AlignTop)
        a = self.gs.gs_aspect

        # Initialize with actual CSS color from current aspect
        bg_init = SGAspect()._qt_color_to_css(a.background_color) or ""
        brd_init = SGAspect()._qt_color_to_css(a.border_color) or ""
        # Compact pickers for container colors (no text field, no Clear)
        self.base_background_color = ColorPickerField(bg_init, show_line=False, show_clear=False)
        self.base_border_color = ColorPickerField(brd_init, show_line=False, show_clear=False)
        self.base_border_size = QSpinBox(); self.base_border_size.setRange(0, 20); self.base_border_size.setValue(self._int(a.border_size))
        # Border style as dropdown
        self.base_border_style = QComboBox()
        border_style_options = ["", "solid", "dotted", "dashed", "double", "groove", "ridge", "inset"]
        self.base_border_style.addItems(border_style_options)
        current_bs = self._val(a.border_style)
        if current_bs in border_style_options:
            self.base_border_style.setCurrentText(current_bs)
        # Text-related fields moved to Titles & Texts tab; hide from Base
        self.base_text_color = None
        self.base_font = None
        self.base_size = None
        self.base_font_weight = None
        self.base_border_radius = QSpinBox(); self.base_border_radius.setRange(0, 50); self.base_border_radius.setValue(self._int(a.border_radius))

        # add transparent helper
        bg_row = QHBoxLayout()
        bg_row.setAlignment(Qt.AlignLeft)
        bg_row.addWidget(self.base_background_color)
        bg_transparent_btn = QPushButton("Transparent")
        bg_transparent_btn.setFixedWidth(90)
        bg_transparent_btn.clicked.connect(self._on_bg_transparent)
        bg_row.addWidget(bg_transparent_btn)
        bg_row_w = QWidget(); bg_row_w.setLayout(bg_row)
        bg_row_w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        form.addRow("background_color", bg_row_w)
        b_row = QHBoxLayout()
        b_row.setAlignment(Qt.AlignLeft)
        b_row.addWidget(self.base_border_color)
        b_transparent_btn = QPushButton("Transparent")
        b_transparent_btn.setFixedWidth(90)
        b_transparent_btn.clicked.connect(self._on_border_transparent)
        b_row.addWidget(b_transparent_btn)
        b_row_w = QWidget(); b_row_w.setLayout(b_row)
        b_row_w.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        form.addRow("border_color", b_row_w)
        form.addRow("border_size", self.base_border_size)
        form.addRow("border_style", self.base_border_style)
        # Text fields removed from Base tab to avoid duplication
        form.addRow("border_radius", self.base_border_radius)
        w.setLayout(form)
        return w

    def _buildTextTab(self):
        w = QWidget()
        w.setObjectName("theme_text_tab")
        w.setStyleSheet("#theme_text_tab{margin:0px; padding:0px;}")
        w.setContentsMargins(0, 0, 0, 0)
        grid = QGridLayout()
        # Strongly reduce margins and spacings to tighten header and first row
        grid.setContentsMargins(0, 0, 0, 0)
        grid.setVerticalSpacing(0)
        grid.setHorizontalSpacing(4)
        labels = [
            ("title1", self.gs.title1_aspect),
            ("title2", self.gs.title2_aspect),
            ("title3", self.gs.title3_aspect),
            ("text1", self.gs.text1_aspect),
            ("text2", self.gs.text2_aspect),
            ("text3", self.gs.text3_aspect),
        ]

        self.text_controls = {}
        headers = ["Aspect", "color", "font", "size", "font_weight", "font_style", "text_decoration", "alignment"]
        for c, h in enumerate(headers):
            lbl = QLabel(h)
            # Remove extra paddings/margins on header labels
            lbl.setStyleSheet("font-weight: bold; margin: 0px; padding: 0px;")
            lbl.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
            grid.addWidget(lbl, 0, c)

        for r, (name, asp) in enumerate(labels, start=1):
            grid.addWidget(QLabel(name), r, 0)
            # Compact color picker (no text field, no Clear button)
            init_color = SGAspect()._qt_color_to_css(asp.color) or ""
            color = ColorPickerField(init_color, show_line=False, show_clear=False); grid.addWidget(color, r, 1)
            font = QComboBox();
            font_list = [
                "", "Times New Roman", "Georgia", "Garamond", "Baskerville", "Arial", "Helvetica", "Verdana",
                "Tahoma", "Trebuchet MS", "Courier New", "Lucida Console", "Monaco", "Consolas",
                "Comic Sans MS", "Papyrus", "Impact"
            ]
            font.addItems(font_list)
            if self._val(asp.font) in font_list:
                font.setCurrentText(self._val(asp.font))
            grid.addWidget(font, r, 2)
            size = QSpinBox(); size.setRange(6, 72); size.setValue(self._int(asp.size, 12)); grid.addWidget(size, r, 3)
            weight = QComboBox();
            weight_list = ["", "normal", "bold", "bolder", "lighter", "100", "200", "300", "400", "500", "600", "700", "800", "900"]
            weight.addItems(weight_list)
            if self._val(asp.font_weight) in weight_list:
                weight.setCurrentText(self._val(asp.font_weight))
            grid.addWidget(weight, r, 4)
            style = QComboBox();
            style_list = ["", "normal", "italic", "oblique"]
            style.addItems(style_list)
            if self._val(asp.font_style) in style_list:
                style.setCurrentText(self._val(asp.font_style))
            grid.addWidget(style, r, 5)
            deco = QComboBox();
            deco_list = ["", "none", "underline", "overline", "line-through", "blink"]
            deco.addItems(deco_list)
            if self._val(asp.text_decoration) in deco_list:
                deco.setCurrentText(self._val(asp.text_decoration))
            grid.addWidget(deco, r, 6)
            align = QComboBox();
            align_list = ["", "Left", "Right", "Center", "HCenter", "Top", "Bottom", "VCenter", "Justify"]
            align.addItems(align_list)
            if self._val(getattr(asp, 'alignment', None)) in align_list:
                align.setCurrentText(self._val(getattr(asp, 'alignment', None)))
            grid.addWidget(align, r, 7)
            self.text_controls[name] = {
                'color': color,
                'font': font,
                'size': size,
                'font_weight': weight,
                'font_style': style,
                'text_decoration': deco,
                'alignment': align,
            }

        w.setLayout(grid)
        return w

    def _val(self, v):
        return "" if v is None else str(v)

    def _int(self, v, default=0):
        try:
            return int(v) if v is not None else default
        except Exception:
            return default

    def _setupAutoPreview(self):
        """Connect all widgets to automatically trigger preview on change."""
        # Use a timer to debounce rapid changes (wait 150ms after last change)
        self._preview_timer = QTimer()
        self._preview_timer.setSingleShot(True)
        self._preview_timer.timeout.connect(self._onPreview)
        
        # Connect base tab widgets
        # ColorPickerField: connect to colorChanged signal
        if hasattr(self, 'base_background_color') and self.base_background_color:
            self.base_background_color.colorChanged.connect(self._triggerAutoPreview)
        
        if hasattr(self, 'base_border_color') and self.base_border_color:
            self.base_border_color.colorChanged.connect(self._triggerAutoPreview)
        
        if hasattr(self, 'base_border_size'):
            self.base_border_size.valueChanged.connect(self._triggerAutoPreview)
        
        if hasattr(self, 'base_border_style'):
            self.base_border_style.currentTextChanged.connect(self._triggerAutoPreview)
        
        if hasattr(self, 'base_border_radius'):
            self.base_border_radius.valueChanged.connect(self._triggerAutoPreview)
        
        # Connect text tab widgets
        if hasattr(self, 'text_controls'):
            for name, controls in self.text_controls.items():
                if 'color' in controls and controls['color']:
                    # ColorPickerField for text aspects - connect to colorChanged signal
                    controls['color'].colorChanged.connect(self._triggerAutoPreview)
                
                if 'font' in controls:
                    controls['font'].currentTextChanged.connect(self._triggerAutoPreview)
                
                if 'size' in controls:
                    controls['size'].valueChanged.connect(self._triggerAutoPreview)
                
                if 'font_weight' in controls:
                    controls['font_weight'].currentTextChanged.connect(self._triggerAutoPreview)
                
                if 'font_style' in controls:
                    controls['font_style'].currentTextChanged.connect(self._triggerAutoPreview)
                
                if 'text_decoration' in controls:
                    controls['text_decoration'].currentTextChanged.connect(self._triggerAutoPreview)
                
                if 'alignment' in controls:
                    controls['alignment'].currentTextChanged.connect(self._triggerAutoPreview)

    def _triggerAutoPreview(self):
        """Trigger a debounced preview update."""
        self._preview_timer.stop()  # Cancel previous timer
        self._preview_timer.start(150)  # Wait 150ms before applying preview

    def _onPreview(self):
        """Apply form changes temporarily to the target GameSpace (no save)."""
        try:
            spec = self._build_spec_from_form(compact=False)
            self._apply_spec_to_gs(spec)
            if hasattr(self.model, 'update'):
                self.model.update()
        except Exception:
            pass

    def _on_bg_transparent(self):
        # Prefer to reflect immediately in the picker preview
        if hasattr(self.base_background_color, 'set_value'):
            self.base_background_color.set_value('transparent')
        elif hasattr(self.base_background_color, 'line') and self.base_background_color.line is not None:
            self.base_background_color.line.setText('transparent')
            self.base_background_color._update_preview()
        # Trigger auto preview
        self._triggerAutoPreview()

    def _on_border_transparent(self):
        if hasattr(self.base_border_color, 'set_value'):
            self.base_border_color.set_value('transparent')
        elif hasattr(self.base_border_color, 'line') and self.base_border_color.line is not None:
            self.base_border_color.line.setText('transparent')
            self.base_border_color._update_preview()
        # Trigger auto preview
        self._triggerAutoPreview()

    def _build_spec_from_form(self, compact=False):
        base = {
            'background_color': self.base_background_color.value_text() or None,
            'border_color': self.base_border_color.value_text() or None,
            'border_size': self.base_border_size.value() or None,
            'border_style': self.base_border_style.currentText().strip() or None,
            # Text properties managed in Titles & Texts tab
            'border_radius': self.base_border_radius.value() or None,
        }
        text_aspects = {}
        for name_key, ctrls in self.text_controls.items():
            spec = {
                'color': ctrls['color'].value_text() or None,
                'font': ctrls['font'].currentText().strip() or None,
                'size': ctrls['size'].value() or None,
                'font_weight': ctrls['font_weight'].currentText().strip() or None,
                'font_style': ctrls['font_style'].currentText().strip() or None,
                'text_decoration': ctrls['text_decoration'].currentText().strip() or None,
                'alignment': ctrls['alignment'].currentText().strip() or None,
            }
            if compact:
                spec = {k: v for k, v in spec.items() if v not in (None, "")}
            text_aspects[name_key] = spec
        spec = {'base': base, 'text_aspects': text_aspects}
        if compact:
            spec['text_aspects'] = {k: v for k, v in text_aspects.items() if v}
        return spec

    def _apply_spec_to_gs(self, spec):
        base = spec.get('base', {})
        ta = spec.get('text_aspects', {})
        a = self.gs.gs_aspect
        # Only update attributes when values are provided; avoid overwriting with None
        if base.get('background_color') is not None and base.get('background_color') != "":
            a.background_color = base.get('background_color')
        if base.get('border_color') is not None and base.get('border_color') != "":
            a.border_color = base.get('border_color')
        if base.get('border_size') is not None:
            a.border_size = base.get('border_size')
        if base.get('border_style') is not None:
            a.border_style = base.get('border_style')
        if base.get('color') is not None:
            a.color = base.get('color')
        if base.get('font') is not None:
            a.font = base.get('font')
        if base.get('size') is not None:
            a.size = base.get('size')
        if base.get('font_weight') is not None:
            a.font_weight = base.get('font_weight')
        if base.get('border_radius') is not None:
            a.border_radius = base.get('border_radius')
        mapping = {
            'title1': self.gs.title1_aspect,
            'title2': self.gs.title2_aspect,
            'title3': self.gs.title3_aspect,
            'text1': self.gs.text1_aspect,
            'text2': self.gs.text2_aspect,
            'text3': self.gs.text3_aspect,
        }
        for key, asp in mapping.items():
            spec_t = ta.get(key, {})
            if 'color' in spec_t and spec_t['color'] is not None:
                asp.color = spec_t['color']
            if 'font' in spec_t and spec_t['font'] is not None:
                asp.font = spec_t['font']
            if 'size' in spec_t and spec_t['size'] is not None:
                asp.size = spec_t['size']
            if 'font_weight' in spec_t and spec_t['font_weight'] is not None:
                asp.font_weight = spec_t['font_weight']
            if 'font_style' in spec_t and spec_t['font_style'] is not None:
                asp.font_style = spec_t['font_style']
            if 'text_decoration' in spec_t and spec_t['text_decoration'] is not None:
                asp.text_decoration = spec_t['text_decoration']
            # NEW: apply alignment from editor when provided
            if 'alignment' in spec_t and spec_t['alignment'] is not None and spec_t['alignment'] != "":
                asp.alignment = spec_t['alignment']
        self.gs.theme_overridden = True
        self.gs.current_theme_name = None
        # Apply container-only style via public hook (subclasses may no-op to avoid QSS cascade)
        if hasattr(self.gs, 'applyContainerAspectStyle'):
            try:
                self.gs.applyContainerAspectStyle()
            except Exception:
                pass
        # If the target GameSpace exposes a hook to refresh text styling, call it
        if hasattr(self.gs, 'onTextAspectsChanged'):
            try:
                self.gs.onTextAspectsChanged()
            except Exception:
                self.gs.update()
        else:
            self.gs.update()

    def _capture_current_gs(self):
        a = self.gs.gs_aspect
        base = {
            'background_color': a.background_color,
            'border_color': a.border_color,
            'border_size': a.border_size,
            'border_style': a.border_style,
            'color': a.color,
            'font': a.font,
            'size': a.size,
            'font_weight': a.font_weight,
            'border_radius': a.border_radius,
        }
        text_aspects = {}
        mapping = {
            'title1': self.gs.title1_aspect,
            'title2': self.gs.title2_aspect,
            'title3': self.gs.title3_aspect,
            'text1': self.gs.text1_aspect,
            'text2': self.gs.text2_aspect,
            'text3': self.gs.text3_aspect,
        }
        for key, asp in mapping.items():
            text_aspects[key] = {
                'color': asp.color,
                'font': asp.font,
                'size': asp.size,
                'font_weight': asp.font_weight,
                'font_style': asp.font_style,
                'text_decoration': asp.text_decoration,
                'alignment': getattr(asp, 'alignment', None),
            }
        return {'base': base, 'text_aspects': text_aspects}

    def _restore_original(self):
        self._apply_spec_to_gs(self._orig_spec)
        self.gs.current_theme_name = self._orig_flags.get('current_theme_name')
        self.gs.theme_overridden = self._orig_flags.get('theme_overridden', False)
        # Clean any residual QSS and reapply container/text via hooks to avoid cascade
        try:
            self.gs.setStyleSheet("")
        except Exception:
            pass
        if hasattr(self.gs, 'applyContainerAspectStyle'):
            try:
                self.gs.applyContainerAspectStyle()
            except Exception:
                pass
        if hasattr(self.gs, 'onTextAspectsChanged'):
            try:
                self.gs.onTextAspectsChanged()
            except Exception:
                self.gs.update()
        else:
            self.gs.update()

    def reject(self):
        self._restore_original()
        super().reject()

    def _onSave(self):
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Theme", "Please enter a theme name")
            return
        # Build theme spec from form using the same builder as Preview
        theme_spec = self._build_spec_from_form(compact=True)

        # Save to persistent storage via SGThemeConfigManager
        from mainClasses.theme.SGThemeConfigManager import SGThemeConfigManager
        from PyQt5.QtWidgets import QMessageBox
        manager = SGThemeConfigManager(self.model)
        
        # Try to save (returns None if theme exists and needs confirmation)
        result = manager.saveCustomTheme(name, theme_spec, overwrite=False)
        
        if result is None:
            # Theme already exists, ask for confirmation
            reply = QMessageBox.question(
                self,
                "Theme Already Exists",
                f"A custom theme named '{name}' already exists.\n\n"
                "Do you want to overwrite it?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                # User confirmed, save with overwrite=True
                if not manager.saveCustomTheme(name, theme_spec, overwrite=True):
                    # Error already displayed by saveCustomTheme, but don't proceed
                    return
            else:
                # User cancelled, don't save
                return
        elif not result:
            # Error occurred (already displayed by saveCustomTheme), don't proceed
            return

        # Also save in memory for immediate use
        if not hasattr(self.model, '_runtime_themes'):
            self.model._runtime_themes = {}
        self.model._runtime_themes[name] = theme_spec
        
        QMessageBox.information(self, "Theme", f"Custom theme '{name}' saved.")
        # Apply the newly saved theme to the current GameSpace and reset override state
        try:
            if hasattr(self.gs, 'applyTheme'):
                self.gs.applyTheme(name)
            # Ensure flags reflect an assigned theme, not a custom override
            self.gs.current_theme_name = name
            self.gs.theme_overridden = False
        except Exception:
            pass
        self.accept()


class ColorPickerField(QWidget):
    """Simple color picker with preview and optional text/clear controls."""
    # Signal emitted when color changes
    colorChanged = pyqtSignal()
    
    def __init__(self, initial_text="", parent=None, show_line=True, show_clear=True):
        super().__init__(parent)
        self._color = self._parse_color(initial_text)
        h = QHBoxLayout()
        h.setContentsMargins(0, 0, 0, 0)
        self.preview = QPushButton()
        self.preview.setFixedWidth(40)
        self.preview.clicked.connect(self._pick)
        # Ensure attributes exist before any preview update
        self.line = None
        self.clear_btn = None
        if show_line:
            self.line = QLineEdit(initial_text)
            self.line.editingFinished.connect(self._line_changed)
        if show_clear:
            self.clear_btn = QPushButton("Clear")
            self.clear_btn.setFixedWidth(50)
            self.clear_btn.clicked.connect(self._clear)
        h.addWidget(self.preview)
        if self.line is not None:
            h.addWidget(self.line)
        if self.clear_btn is not None:
            h.addWidget(self.clear_btn)
        self.setLayout(h)
        # Now that widgets are created, update preview safely
        self._update_preview()

    def _parse_color(self, text):
        if not text:
            return None
        c = QColor(text)
        if c.isValid():
            return c
        return None

    def _update_preview(self):
        # Transparent if explicit text 'transparent' or color with alpha 0
        is_transparent = False
        if self.line is not None and isinstance(self.line.text(), str) and self.line.text().strip().lower() == 'transparent':
            is_transparent = True
        elif self._color and self._color.isValid() and self._color.alpha() == 0:
            is_transparent = True

        if is_transparent:
            # Build a checkerboard with a red diagonal to indicate transparency
            w = max(24, self.preview.width())
            h = max(16, self.preview.height())
            pix = QPixmap(w, h)
            pix.fill(Qt.white)
            painter = QPainter(pix)
            # Checkerboard
            tile = 4
            for y in range(0, h, tile):
                for x in range(0, w, tile):
                    if ((x // tile) + (y // tile)) % 2 == 0:
                        painter.fillRect(x, y, tile, tile, QColor(220, 220, 220))
            # Red diagonal
            pen = QPen(QColor(220, 0, 0))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawLine(0, 0, w, h)
            painter.end()
            self.preview.setIcon(QIcon(pix))
            self.preview.setIconSize(QSize(w, h))
            self.preview.setStyleSheet("background: none;")
        elif self._color and self._color.isValid():
            # Clear icon and set background color
            self.preview.setIcon(QIcon())
            self.preview.setStyleSheet(f"background-color: {self._color.name()}")
        else:
            self.preview.setIcon(QIcon())
            self.preview.setStyleSheet("")

    def _pick(self):
        c = QColorDialog.getColor(self._color or QColor("#ffffff"), self, "Select Color")
        if c.isValid():
            self._color = c
            if self.line is not None:
                self.line.setText(c.name())
            self._update_preview()
            # Emit signal to notify color change
            self.colorChanged.emit()

    def _line_changed(self):
        old_color = self._color
        self._color = self._parse_color(self.line.text().strip())
        self._update_preview()
        # Emit signal if color actually changed
        if old_color != self._color:
            self.colorChanged.emit()

    def _clear(self):
        old_color = self._color
        self._color = None
        if self.line is not None:
            self.line.setText("")
        self._update_preview()
        # Emit signal if color actually changed
        if old_color != self._color:
            self.colorChanged.emit()

    def value_text(self):
        # Prefer explicit text (e.g., 'transparent') if present
        if self.line is not None:
            t = self.line.text().strip()
            if t:
                return t
        if self._color and self._color.isValid():
            # If alpha is 0, represent as 'transparent' to preserve semantics
            if self._color.alpha() == 0:
                return 'transparent'
            return self._color.name()
        return None

    def set_value(self, text):
        """Programmatically set the color (supports 'transparent' and hex)."""
        old_color = self._color
        if self.line is not None:
            self.line.setText(text or "")
        self._color = self._parse_color(text)
        self._update_preview()
        # Emit signal if color actually changed
        if old_color != self._color:
            self.colorChanged.emit()


