

    # ============================================================
    # Mouse, Drag/Drop, Keyboard, Window Event Handlers + Tooltip example
    # ------------------------------------------------------------
    # These methods override Qt's built-in event handlers
    # to serve as a coding guide. By default, they just forward
    # the event to the parent class (no behavior change).
    # ============================================================


class SGEventHandlerGuide:
    """
    Mixin class serving as a documentation guide for mouse, drag/drop,
    window, keyboard and tooltip event handlers in PyQt5.

    ⚠️ General rule for all event handlers:
    - Call event.accept() if you want to handle and consume the event.
    - Call event.ignore() if you want the event to propagate to the parent widget
      or be handled by the default Qt implementation.
    - In Drag & Drop events, prefer event.acceptProposedAction() instead of accept(),
      since it validates the action proposed by the drag source (e.g. Copy, Move).
    """

    # ============================================================
    # 🖱️ Mouse Events
    # ============================================================

    def mousePressEvent(self, event):
        """
        Called when a mouse button is pressed on this widget.

        - Left click   → if event.button() == Qt.LeftButton   → handle left click or initiate a drag
        - Right click  → if event.button() == Qt.RightButton  → open context menu or custom actions
        - Middle click → if event.button() == Qt.MiddleButton → custom actions (e.g. panning, special commands)
        """
        pass

    def mouseReleaseEvent(self, event):
        """
        Called when a mouse button is released on this widget.

        Typically used to finalize a click action.
        Note: drag-and-drop operations usually bypass this event.
        """
        pass

    def mouseMoveEvent(self, event):
        """
        Called when the mouse is moved while a button is pressed.

        Often used to start a drag operation or implement custom dragging.
        """
        pass

    # ============================================================
    # 🔄 Enter / Leave Events
    # ============================================================

    def enterEvent(self, event):
        """
        Called when the mouse cursor enters the widget's area.

        Useful for hover effects or highlighting the widget.
        """
        pass

    def leaveEvent(self, event):
        """
        Called when the mouse cursor leaves the widget's area.

        Useful for removing hover effects or restoring the normal state.
        """
        pass

    # ============================================================
    # 📦 Drag & Drop Events
    # ============================================================

    def dragEnterEvent(self, event):
        """
        Called when a drag operation enters the widget's area.

        Typical use: check the type of data and accept/reject the drag.
        - Use event.acceptProposedAction() to accept the proposed action (preferred).
        - Use event.ignore() to reject the drag.
        """
        pass

    def dragLeaveEvent(self, event):
        """
        Called when a drag operation leaves the widget's area without dropping.
        """
        pass

    def dropEvent(self, event):
        """
        Called when a drag operation is dropped onto the widget.

        - To get the dragged widget: source = event.source()
        - To finalize the drop: call event.acceptProposedAction() (preferred over accept()).
        - If you do not accept the drop: call event.ignore()
        """
        pass

    # ============================================================
    # 🪟 Window Events
    # ============================================================

    def closeEvent(self, event):
        """
        Called when the widget is requested to close (e.g. user clicks the X,
        or self.close() is called).

        - Use event.accept() to allow closing.
        - Use event.ignore() to block closing (e.g. after asking confirmation).
        """
        pass

    def showEvent(self, event):
        """
        Called when the widget becomes visible (e.g. after show()).

        Useful for initialization that requires the widget to be fully displayed.
        """
        pass

    def hideEvent(self, event):
        """
        Called when the widget is hidden (e.g. after hide()).

        Useful for cleanup or pausing background tasks.
        """
        pass

    def resizeEvent(self, event):
        """
        Called when the widget is resized.

        Useful for adjusting layouts, redrawing content, or resizing child widgets.
        """
        pass

    # ============================================================
    # ⌨️ Keyboard Events (optional)
    # ============================================================

    def keyPressEvent(self, event):
        """
        Called when a key is pressed while the widget has focus.

        Example:
        - if event.key() == Qt.Key_Delete → delete selected item
        - if event.key() == Qt.Key_Escape → cancel operation
        """
        pass

    def keyReleaseEvent(self, event):
        """
        Called when a key is released while the widget has focus.
        """
        pass

    # ============================================================
    # 💬 Tooltips (Info-bubbles)
    # ============================================================

    def set_tooltip_example(self):
        """
        Tooltips (infobulles) provide additional info when the user hovers over a widget.

        How to define a tooltip:
        - self.setToolTip("This is a tooltip text")

        Example with HTML formatting:
        - self.setToolTip("<b>Bold text</b><br>Extra description")

        How to show a tooltip manually (at a given position):
        - QToolTip.showText(event.globalPos(), "Tooltip text", self)

        How to hide tooltip:
        - QToolTip.hideText()

        How to show an image as tooltip:
        - self.setToolTip('<img src="path/to/image.png">')
        (Note: image can be local path or Qt resource)
        """
        pass