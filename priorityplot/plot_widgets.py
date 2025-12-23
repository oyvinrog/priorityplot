from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
                             QTableWidgetItem, QLabel, QMessageBox, QAbstractItemView,
                             QHeaderView, QSplitter, QApplication, QLineEdit)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPoint, QMimeData
from PyQt6.QtGui import QColor, QFont, QDrag, QPixmap, QPainter, QFontMetrics, QCursor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from typing import List, Optional
from datetime import datetime
import os

from .interfaces import IPlotWidget, ITaskDisplayWidget, IExportService
from .model import (Task, TaskConstants, TaskStateManager, TaskDisplayFormatter, 
                   ExcelExporter, get_top_tasks, get_task_colors, TaskValidator)
from .ui_constants import (ColorPalette, SizeConstants, OpacityConstants, 
                           InteractionConstants, LayoutConstants, FigureConstants)

class InteractivePlotWidget(QWidget):
    """Single responsibility: Handle interactive plot functionality following SRP
    Implements IPlotWidget protocol methods"""
    
    task_moved = pyqtSignal(int, float, float)  # task_index, value, time
    task_selected = pyqtSignal(int)  # task_index
    task_drag_started = pyqtSignal(int, str)  # task index, task data for external drops
    task_delete_requested = pyqtSignal(int)  # task index to delete
    task_move_finished = pyqtSignal(int, float, float)  # task_index, value, time
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tasks = []
        self._state_manager = TaskStateManager()
        self._setup_plot()
        self._setup_interaction()
        
        # Interaction state
        self.dragging = False
        self.drag_index = None
        self.selected_task_index = None  # Track the selected task for deletion
        self.current_annotation = None
        self.highlight_scatter = None
        self.highlight_elements = []
        self.drag_threshold = InteractionConstants.DRAG_THRESHOLD_PIXELS
        self.initial_click_pos = None
        self.is_external_drag = False
        self.drag_preview_annotation = None
        
        # CRITICAL FIX: Store original values to prevent unintended changes
        self.original_task_value = None
        self.original_task_time = None
        
        # Enable keyboard focus to receive key events
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
    def _setup_plot(self):
        layout = QVBoxLayout()
        
        # Create matplotlib figure with modern styling
        self.figure = Figure(
            figsize=(FigureConstants.FIG_WIDTH, FigureConstants.FIG_HEIGHT),
            facecolor=ColorPalette.BG_PRIMARY
        )
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        
        # Set modern plot style
        self.ax.set_facecolor(ColorPalette.PLOT_BG)
        self.ax.grid(
            True,
            linestyle='--',
            alpha=OpacityConstants.ALPHA_GRID,
            color=ColorPalette.GRID_LINE,
            linewidth=SizeConstants.LINE_WIDTH_NORMAL
        )
        self.ax.spines['bottom'].set_color(ColorPalette.ACCENT_PURPLE)
        self.ax.spines['top'].set_color(ColorPalette.BORDER_PRIMARY)
        self.ax.spines['left'].set_color(ColorPalette.ACCENT_PURPLE)
        self.ax.spines['right'].set_color(ColorPalette.BORDER_PRIMARY)
        self.ax.spines['bottom'].set_linewidth(SizeConstants.LINE_WIDTH_THICK)
        self.ax.spines['left'].set_linewidth(SizeConstants.LINE_WIDTH_THICK)
        self.ax.spines['top'].set_linewidth(SizeConstants.LINE_WIDTH_THIN)
        self.ax.spines['right'].set_linewidth(SizeConstants.LINE_WIDTH_THIN)
        
        # Set labels with modern typography
        self.ax.set_xlabel(
            'Value (Impact/Importance)',
            color=ColorPalette.TEXT_PRIMARY,
            fontsize=SizeConstants.FONT_LARGE,
            fontweight='600',
            labelpad=LayoutConstants.LABEL_PAD
        )
        self.ax.set_ylabel(
            'Time Investment (Hours)',
            color=ColorPalette.TEXT_PRIMARY,
            fontsize=SizeConstants.FONT_LARGE,
            fontweight='600',
            labelpad=LayoutConstants.LABEL_PAD
        )
        self.ax.set_title(
            'Priority Matrix  •  Click to highlight',
            color=ColorPalette.TEXT_SECONDARY,
            fontsize=SizeConstants.FONT_HEADER,
            fontweight='bold',
            pad=LayoutConstants.LABEL_PAD_LARGE,
            fontstyle='normal'
        )
        self.figure.subplots_adjust(
            left=LayoutConstants.FIG_LEFT,
            bottom=LayoutConstants.FIG_BOTTOM,
            right=LayoutConstants.FIG_RIGHT,
            top=LayoutConstants.FIG_TOP
        )
        
        # Style ticks with modern colors
        self.ax.tick_params(colors=ColorPalette.TEXT_MUTED, which='both', labelsize=SizeConstants.FONT_NORMAL)
        
        # Set fixed axis limits
        self.ax.set_xlim(0, TaskConstants.MAX_VALUE)
        self.ax.set_ylim(0, TaskConstants.MAX_TIME)
        
        # Add quadrant lines for visual structure
        mid_x = TaskConstants.MAX_VALUE / 2
        mid_y = TaskConstants.MAX_TIME / 2
        self.ax.axvline(x=mid_x, color=ColorPalette.ACCENT_PURPLE, linestyle='-', alpha=0.3, linewidth=1.5)
        self.ax.axhline(y=mid_y, color=ColorPalette.ACCENT_PURPLE, linestyle='-', alpha=0.3, linewidth=1.5)
        
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        
    def _setup_interaction(self):
        # Connect mouse events
        self.canvas.mpl_connect('button_press_event', self._on_press)
        self.canvas.mpl_connect('button_release_event', self._on_release)
        self.canvas.mpl_connect('motion_notify_event', self._on_motion)
        self.canvas.mpl_connect('motion_notify_event', self._on_hover)
        
        # Auto-update timer for real-time updates
        self.auto_update_timer = QTimer()
        self.auto_update_timer.timeout.connect(self._emit_task_moved)
        self.auto_update_timer.setSingleShot(True)
    
    def update_plot(self, tasks: List[Task]) -> None:
        """Implementation of IPlotWidget interface"""
        self._tasks = tasks
        self.clear_highlighting()
        
        self.ax.clear()
        self._reapply_styling()
        
        if not tasks:
            self.canvas.draw()
            return
        
        # Create arrays for all points
        x_data = [t.value for t in tasks]
        y_data = [t.time for t in tasks]
        
        # Get top 3 tasks
        top_3_tasks = get_top_tasks(tasks, 3)
        top_3_indices = []
        for task in top_3_tasks:
            if task in tasks:
                top_3_indices.append(tasks.index(task))
        
        # Get colors
        colors = get_task_colors(tasks, self._state_manager.moved_points, self._state_manager.new_task_indices)
        
        # Plot regular points
        non_top_indices = [i for i in range(len(tasks)) if i not in top_3_indices]
        if non_top_indices:
            self.ax.scatter(
                [x_data[i] for i in non_top_indices],
                [y_data[i] for i in non_top_indices],
                c=[colors[i] for i in non_top_indices],
                picker=True,
                alpha=OpacityConstants.ALPHA_SCATTER,
                s=SizeConstants.SCATTER_NORMAL
            )
        
        # Plot top 3 with special styling
        for rank, task_index in enumerate(top_3_indices, 1):
            if task_index < len(tasks):
                task_x = x_data[task_index]
                task_y = y_data[task_index]
                self.ax.plot(
                    task_x, task_y, 'o',
                    markersize=SizeConstants.SCATTER_TOP_RANK,
                    markerfacecolor='none',
                    markeredgecolor=colors[task_index],
                    markeredgewidth=SizeConstants.LINE_WIDTH_THICK
                )
                self.ax.text(
                    task_x, task_y, str(rank),
                    ha='center', va='center',
                    fontsize=SizeConstants.FONT_XXLARGE,
                    fontweight='bold',
                    color=colors[task_index]
                )
        
        # Update scatter reference for event handling
        self.scatter = self.ax.scatter(x_data, y_data, c=colors, picker=True, alpha=OpacityConstants.ALPHA_HIDDEN)
        
        # Adjust layout
        self.figure.subplots_adjust(
            left=LayoutConstants.FIG_LEFT,
            bottom=LayoutConstants.FIG_BOTTOM,
            right=LayoutConstants.FIG_RIGHT,
            top=LayoutConstants.FIG_TOP
        )
        self.canvas.draw()
    
    def highlight_task_in_plot(self, task_index: int) -> None:
        """Implementation of IPlotWidget interface"""
        if task_index >= len(self._tasks):
            return
            
        task = self._tasks[task_index]
        
        # Remove previous highlights
        self.clear_highlighting()
        
        # Create highlight circle
        self.highlight_scatter = self.ax.scatter(
            [task.value], [task.time],
            s=SizeConstants.SCATTER_HIGHLIGHT,
            facecolors='none',
            edgecolors=ColorPalette.HIGHLIGHT_GOLD,
            linewidths=SizeConstants.LINE_WIDTH_EXTRA_THICK,
            alpha=OpacityConstants.ALPHA_HIGHLIGHT,
            zorder=10
        )
        
        # Add pulsing effect
        pulse_scatter = self.ax.scatter(
            [task.value], [task.time],
            s=SizeConstants.SCATTER_PULSE,
            facecolors='none',
            edgecolors=ColorPalette.HIGHLIGHT_GOLD,
            linewidths=SizeConstants.LINE_WIDTH_THICK,
            alpha=OpacityConstants.ALPHA_LIGHT,
            zorder=9
        )
        self.highlight_elements.append(pulse_scatter)
        
        # Add text label
        highlight_text = self.ax.text(
            task.value, task.time + 0.3,
            f"{task.task[:20]}{'...' if len(task.task) > 20 else ''}",
            ha='center', va='bottom',
            fontsize=SizeConstants.FONT_NORMAL,
            fontweight='bold',
            color=ColorPalette.HIGHLIGHT_GOLD,
            bbox=dict(boxstyle='round,pad=0.3', facecolor=ColorPalette.TOOLTIP_BG, alpha=OpacityConstants.ALPHA_DRAG),
            zorder=11
        )
        self.highlight_elements.append(highlight_text)
        
        # Use state manager
        self._state_manager.set_highlighted_task(task_index)
        
        self.canvas.draw_idle()
    
    def clear_highlighting(self):
        """Clear all highlighting"""
        if self.highlight_scatter:
            self.highlight_scatter.remove()
            self.highlight_scatter = None
        
        for element in self.highlight_elements:
            try:
                element.remove()
            except:
                pass
        self.highlight_elements = []
        
        self._state_manager.clear_highlighting()
        
        if hasattr(self, 'canvas'):
            self.canvas.draw_idle()
    
    def _reapply_styling(self):
        """Reapply plot styling after clear"""
        self.ax.set_facecolor(ColorPalette.PLOT_BG)
        self.ax.grid(
            True,
            linestyle='--',
            alpha=OpacityConstants.ALPHA_GRID,
            color=ColorPalette.GRID_LINE,
            linewidth=SizeConstants.LINE_WIDTH_NORMAL
        )
        self.ax.spines['bottom'].set_color(ColorPalette.ACCENT_PURPLE)
        self.ax.spines['top'].set_color(ColorPalette.BORDER_PRIMARY)
        self.ax.spines['left'].set_color(ColorPalette.ACCENT_PURPLE)
        self.ax.spines['right'].set_color(ColorPalette.BORDER_PRIMARY)
        self.ax.spines['bottom'].set_linewidth(SizeConstants.LINE_WIDTH_THICK)
        self.ax.spines['left'].set_linewidth(SizeConstants.LINE_WIDTH_THICK)
        self.ax.spines['top'].set_linewidth(SizeConstants.LINE_WIDTH_THIN)
        self.ax.spines['right'].set_linewidth(SizeConstants.LINE_WIDTH_THIN)
        
        self.ax.set_xlabel(
            'Value (Impact/Importance)',
            color=ColorPalette.TEXT_PRIMARY,
            fontsize=SizeConstants.FONT_LARGE,
            fontweight='600',
            labelpad=LayoutConstants.LABEL_PAD
        )
        self.ax.set_ylabel(
            'Time Investment (Hours)',
            color=ColorPalette.TEXT_PRIMARY,
            fontsize=SizeConstants.FONT_LARGE,
            fontweight='600',
            labelpad=LayoutConstants.LABEL_PAD
        )
        self.ax.set_title(
            'Priority Matrix  •  Click to highlight',
            color=ColorPalette.TEXT_SECONDARY,
            fontsize=SizeConstants.FONT_HEADER,
            fontweight='bold',
            pad=LayoutConstants.LABEL_PAD_LARGE
        )
        
        self.ax.tick_params(colors=ColorPalette.TEXT_MUTED, which='both', labelsize=SizeConstants.FONT_NORMAL)
        self.ax.set_xlim(0, TaskConstants.MAX_VALUE)
        self.ax.set_ylim(0, TaskConstants.MAX_TIME)
        
        # Add quadrant lines for visual structure
        mid_x = TaskConstants.MAX_VALUE / 2
        mid_y = TaskConstants.MAX_TIME / 2
        self.ax.axvline(x=mid_x, color=ColorPalette.ACCENT_PURPLE, linestyle='-', alpha=0.3, linewidth=1.5)
        self.ax.axhline(y=mid_y, color=ColorPalette.ACCENT_PURPLE, linestyle='-', alpha=0.3, linewidth=1.5)
    
    def _on_press(self, event):
        if event.inaxes != self.ax:
            return
        contains, ind = self.scatter.contains(event)
        if contains:
            task_index = ind["ind"][0]
            if event.button == 1:  # Left mouse button
                self.initial_click_pos = (event.x, event.y)
                self.drag_index = task_index
                self.selected_task_index = task_index  # Track for deletion
                self.task_selected.emit(task_index)
                # Set focus to enable keyboard events
                self.setFocus()
    
    def _on_motion(self, event):
        if self.drag_index is None:
            return
            
        # Check if we should start dragging
        if not self.dragging and self.initial_click_pos:
            current_pos = (event.x, event.y)
            distance = ((current_pos[0] - self.initial_click_pos[0])**2 + 
                       (current_pos[1] - self.initial_click_pos[1])**2)**0.5
            
            if distance > self.drag_threshold:
                self._start_drag(event)
                return
        
        if not self.dragging:
            return
            
        # Check if we're dragging outside the plot area for external drop
        if event.inaxes != self.ax:
            if not self.is_external_drag:
                self._start_external_drag(event)
            return
        else:
            if self.is_external_drag:
                return
        
        # Normal internal dragging within plot (only if not in external drag mode)
        if event.inaxes == self.ax and not self.is_external_drag:
            self._handle_internal_drag(event)
    
    def _start_drag(self, event):
        """Start the drag operation with enhanced visual feedback"""
        self.dragging = True
        task = self._tasks[self.drag_index]
        
        # CRITICAL FIX: Store original values to restore if external drag is detected
        self.original_task_value = task.value
        self.original_task_time = task.time
        
        # Create drag preview annotation
        self.drag_preview_annotation = self.ax.annotate(
            f"🎯 Dragging: {task.task[:20]}{'...' if len(task.task) > 20 else ''}",
            xy=(task.value, task.time),
            xytext=(LayoutConstants.TEXT_OFFSET_X, -LayoutConstants.TEXT_OFFSET_Y_LARGE),
            textcoords='offset points',
            bbox=dict(
                boxstyle='round,pad=0.5',
                facecolor=ColorPalette.DRAG_PREVIEW_BG,
                edgecolor=ColorPalette.HIGHLIGHT_GOLD_ALT,
                alpha=OpacityConstants.ALPHA_HIGHLIGHT,
                linewidth=SizeConstants.LINE_WIDTH_THICK
            ),
            color=ColorPalette.TEXT_BLACK,
            fontsize=SizeConstants.FONT_NORMAL,
            fontweight='bold',
            zorder=20,
            arrowprops=dict(
                arrowstyle='->',
                connectionstyle='arc3,rad=0.1',
                color=ColorPalette.HIGHLIGHT_GOLD_ALT,
                linewidth=SizeConstants.LINE_WIDTH_THICK
            )
        )
        
        # Add pulsing highlight to the dragged point
        self.highlight_scatter = self.ax.scatter(
            [task.value], [task.time],
            s=SizeConstants.SCATTER_DRAG,
            facecolors='none',
            edgecolors=ColorPalette.HIGHLIGHT_GOLD,
            linewidths=SizeConstants.LINE_WIDTH_VERY_THICK,
            alpha=OpacityConstants.ALPHA_DRAG,
            zorder=15,
            animated=True
        )
        
        self.canvas.draw_idle()
    
    def _handle_internal_drag(self, event):
        """Handle dragging within the plot area"""
        # CRITICAL FIX: Prevent value changes during external drag
        if self.is_external_drag:
            return
            
        # Update task values
        new_value = max(0, min(TaskConstants.MAX_VALUE, event.xdata))
        new_time = max(0, min(TaskConstants.MAX_TIME, event.ydata))
        
        self._tasks[self.drag_index].value = new_value
        self._tasks[self.drag_index].time = new_time
        self._state_manager.mark_task_moved(self.drag_index)
        
        # Update scatter plot data for smooth movement
        x_data = [t.value for t in self._tasks]
        y_data = [t.time for t in self._tasks]
        self.scatter.set_offsets(np.column_stack([x_data, y_data]))
        
        # Update highlight position
        if self.highlight_scatter:
            self.highlight_scatter.set_offsets([[new_value, new_time]])
        
        # Update drag preview annotation position
        if self.drag_preview_annotation:
            self.drag_preview_annotation.xy = (new_value, new_time)
        
        self.canvas.draw_idle()
        
        # Trigger update with delay
        self.auto_update_timer.start(InteractionConstants.AUTO_UPDATE_DELAY_MS)
    
    def _start_external_drag(self, event):
        """Start external drag operation for dropping outside the plot"""
        if self.is_external_drag:
            return
            
        self.is_external_drag = True
        task = self._tasks[self.drag_index]
        
        # CRITICAL FIX: Restore original values to prevent unintended changes
        if self.original_task_value is not None and self.original_task_time is not None:
            task.value = self.original_task_value
            task.time = self.original_task_time
            print(f"🔧 Restored original values: value={self.original_task_value}, time={self.original_task_time}")
        
        # Change cursor to indicate external drag
        QApplication.setOverrideCursor(QCursor(Qt.CursorShape.DragMoveCursor))
        
        # Update drag preview to indicate external drag
        if self.drag_preview_annotation:
            self.drag_preview_annotation.set_text(
                f"📋 Moving: {task.task[:15]}{'...' if len(task.task) > 15 else ''}"
            )
            self.drag_preview_annotation.get_bbox_patch().set_facecolor(ColorPalette.EXTERNAL_DRAG_BG)
            self.drag_preview_annotation.get_bbox_patch().set_edgecolor(ColorPalette.HIGHLIGHT_GREEN_DARK)
            self.drag_preview_annotation.set_color(ColorPalette.TEXT_BLACK)
            # Update annotation position to original values
            self.drag_preview_annotation.xy = (task.value, task.time)
        
        # Update highlight position to original values
        if self.highlight_scatter:
            self.highlight_scatter.set_offsets([[task.value, task.time]])
        
        # Update scatter plot data to show restored values
        x_data = [t.value for t in self._tasks]
        y_data = [t.time for t in self._tasks]
        if hasattr(self, 'scatter'):
            self.scatter.set_offsets(np.column_stack([x_data, y_data]))
        
        # Create and start Qt drag operation
        drag = QDrag(self)
        mime_data = QMimeData()
        mime_data.setText(f"task_{self.drag_index}")
        drag.setMimeData(mime_data)
        
        # Create drag pixmap for visual feedback
        drag_pixmap = self._create_drag_pixmap(task)
        drag.setPixmap(drag_pixmap)
        drag.setHotSpot(QPoint(drag_pixmap.width() // 2, drag_pixmap.height() // 2))
        
        # Emit signal for external drag
        self.task_drag_started.emit(self.drag_index, f"task_{self.drag_index}")
        
        self.canvas.draw_idle()
        
        # Execute the drag operation asynchronously
        QTimer.singleShot(0, lambda: self._execute_drag(drag))
    
    def _execute_drag(self, drag):
        """Execute the Qt drag operation"""
        try:
            result = drag.exec(Qt.DropAction.CopyAction | Qt.DropAction.MoveAction)
            print(f"🎯 Drag operation completed with result: {result}")
        except Exception as e:
            print(f"❌ Error during drag operation: {e}")
        finally:
            self._cleanup_drag()
    
    def _end_external_drag(self):
        """End external drag and return to internal drag mode"""
        if not self.is_external_drag:
            return
            
        self.is_external_drag = False
        QApplication.restoreOverrideCursor()
        
        # Update drag preview back to internal mode
        if self.drag_preview_annotation:
            task = self._tasks[self.drag_index]
            self.drag_preview_annotation.set_text(
                f"🎯 Dragging: {task.task[:20]}{'...' if len(task.task) > 20 else ''}"
            )
            self.drag_preview_annotation.get_bbox_patch().set_facecolor(ColorPalette.DRAG_PREVIEW_BG)
            self.drag_preview_annotation.get_bbox_patch().set_edgecolor(ColorPalette.HIGHLIGHT_GOLD_ALT)
            self.drag_preview_annotation.set_color(ColorPalette.TEXT_BLACK)
        
        self.canvas.draw_idle()
    
    def _create_drag_pixmap(self, task):
        """Create a visual pixmap for the drag operation"""
        task_text = task.task
        if len(task_text) > 25:
            task_text = task_text[:22] + "..."
        
        font = QFont("Arial", 11, QFont.Weight.Bold)
        metrics = QFontMetrics(font)
        
        text_width = metrics.horizontalAdvance(task_text)
        text_height = metrics.height()
        
        padding = 15
        icon_space = 35
        pixmap_width = max(text_width + icon_space + padding * 2, 220)
        pixmap_height = text_height + padding * 2 + 10
        
        pixmap = QPixmap(pixmap_width, pixmap_height)
        pixmap.fill(QColor(0, 255, 127, 220))  # Semi-transparent green
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setFont(font)
        
        # Draw border with rounded corners
        painter.setPen(QColor(0, 204, 102, 255))
        painter.setBrush(QColor(0, 255, 127, 180))
        painter.drawRoundedRect(2, 2, pixmap_width-4, pixmap_height-4, 10, 10)
        
        # Draw task icon
        painter.setPen(QColor(0, 100, 50, 255))
        painter.drawText(padding, padding + text_height//2 + 5, "📋")
        
        # Draw task text
        painter.setPen(QColor(0, 50, 25, 255))
        text_x = padding + icon_space
        text_y = padding + text_height//2 + 5
        painter.drawText(text_x, text_y, task_text)
        
        # Draw value and time info
        painter.setPen(QColor(0, 100, 50, 200))
        info_text = f"★{task.value:.1f} ⏰{task.time:.1f}h"
        painter.drawText(text_x, text_y + 15, info_text)
        
        painter.end()
        
        return pixmap
    
    def _on_release(self, event):
        """Handle mouse release events"""
        self._cleanup_drag()
    
    def _cleanup_drag(self):
        """Clean up after drag operation"""
        # Restore cursor
        QApplication.restoreOverrideCursor()
        finished_task = None
        
        if self.dragging and self.drag_index is not None:
            # Emit final update for internal drags
            if not self.is_external_drag and self.drag_index < len(self._tasks):
                task = self._tasks[self.drag_index]
                self.task_moved.emit(self.drag_index, task.value, task.time)
                # Full redraw
                self.update_plot(self._tasks)
                finished_task = (self.drag_index, task.value, task.time)
        
        # Clean up visual elements
        if self.drag_preview_annotation:
            try:
                self.drag_preview_annotation.remove()
            except:
                pass
            self.drag_preview_annotation = None
            
        if self.highlight_scatter:
            try:
                self.highlight_scatter.remove()
            except:
                pass
            self.highlight_scatter = None
        
        # Reset state
        self.dragging = False
        self.drag_index = None
        self.initial_click_pos = None
        self.is_external_drag = False
        
        # CRITICAL FIX: Reset stored original values
        self.original_task_value = None
        self.original_task_time = None
        
        if hasattr(self, 'canvas'):
            self.canvas.draw_idle()

        if finished_task is not None:
            self.task_move_finished.emit(*finished_task)
    
    def keyPressEvent(self, event):
        """Handle keyboard events for task deletion"""
        from PyQt6.QtCore import Qt
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            # Delete the currently selected task
            if self.selected_task_index is not None:
                self.task_delete_requested.emit(self.selected_task_index)
        else:
            super().keyPressEvent(event)
    
    def _on_hover(self, event):
        if event.inaxes != self.ax:
            if self.current_annotation:
                self.current_annotation.set_visible(False)
                self.current_annotation = None
                self.canvas.draw_idle()
            return

        contains, ind = self.scatter.contains(event)
        if contains:
            pos = ind["ind"][0]
            task = self._tasks[pos]
            
            # Remove previous annotation
            if self.current_annotation:
                self.current_annotation.set_visible(False)
            
            # Create new annotation
            priority_score = task.value / task.time if task.time > 0 else 0
            text = f"{task.task}\nValue: {task.value:.1f}\nTime: {task.time:.1f}\nPriority: {priority_score:.2f}"
            self.current_annotation = self.ax.annotate(
                text,
                xy=(task.value, task.time),
                xytext=(LayoutConstants.TEXT_OFFSET_X, LayoutConstants.TEXT_OFFSET_Y),
                textcoords='offset points',
                bbox=dict(
                    boxstyle='round,pad=0.5',
                    fc=ColorPalette.TOOLTIP_BG,
                    ec=ColorPalette.TEXT_DISABLED,
                    alpha=OpacityConstants.ALPHA_TOOLTIP
                ),
                color=ColorPalette.TEXT_WHITE,
                fontsize=SizeConstants.FONT_SMALL,
                fontweight='bold',
                arrowprops=dict(
                    arrowstyle='->',
                    connectionstyle='arc3,rad=0.2',
                    color=ColorPalette.TEXT_DISABLED,
                    linewidth=SizeConstants.LINE_WIDTH_MEDIUM
                )
            )
            self.canvas.draw_idle()
        elif self.current_annotation:
            self.current_annotation.set_visible(False)
            self.current_annotation = None
            self.canvas.draw_idle()
    
    def _emit_task_moved(self):
        """Emit task moved signal after delay"""
        if self.drag_index is not None and self.drag_index < len(self._tasks):
            task = self._tasks[self.drag_index]
            self.task_moved.emit(self.drag_index, task.value, task.time)

class DraggableTaskTable(QTableWidget):
    """Single responsibility: Display priority ranking with drag capability following SRP
    Implements ITaskDisplayWidget protocol methods"""
    
    task_selected = pyqtSignal(int)  # original task index
    task_drag_started = pyqtSignal(int, str)  # task index, task data
    task_delete_requested = pyqtSignal(int)  # task index to delete
    task_renamed = pyqtSignal(int, str)  # task index, new name
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tasks = []
        self._sorted_tasks = []
        self._parent_widget = parent
        self._max_score = 1.0  # Track max score for progress bar scaling
        self._ignore_item_changes = False
        self._setup_table()
        
    def _setup_table(self):
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels(['🏆', 'TASK', 'VALUE', 'SCORE', '', ''])
        
        # Modern enhanced styling
        self.setStyleSheet("""
            QTableWidget {
                font-size: 13px;
                border-radius: 12px;
                border: 2px solid #2D3139;
                background: #181A1F;
                selection-background-color: #4F46E5;
                gridline-color: #2D3139;
            }
            QTableWidget::item {
                padding: 14px 10px;
                border-bottom: 1px solid #2D3139;
                min-height: 18px;
                color: #E5E7EB;
            }
            QTableWidget::item:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #252830, stop:1 #1F2228);
                border: none;
            }
            QTableWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #6366F1, stop:1 #4F46E5);
                color: white;
                font-weight: 700;
            }
            QHeaderView::section {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #252830, stop:1 #1F2228);
                color: #F3F4F6;
                padding: 14px 10px;
                font-size: 12px;
                font-weight: 700;
                border: 1px solid #2D3139;
                text-align: center;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }
        """)
        
        # Table settings
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.verticalHeader().setDefaultSectionSize(40)
        
        # Column widths
        header = self.horizontalHeader()
        header.setStretchLastSection(False)
        self.setColumnWidth(0, 50)   # Rank column
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # Task name
        self.setColumnWidth(2, 70)   # Value column
        self.setColumnWidth(3, 70)   # Score column  
        self.setColumnWidth(4, 100)  # Progress bar column
        self.setColumnWidth(5, 50)   # Delete button column
        
        # Enable drag
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragOnly)
        self.setDefaultDropAction(Qt.DropAction.CopyAction)
        
        # Connect signals
        self.cellClicked.connect(self._on_cell_clicked)
        self.itemChanged.connect(self._on_item_changed)
    
    def refresh_display(self, tasks: List[Task]) -> None:
        """Implementation of ITaskDisplayWidget interface"""
        self._ignore_item_changes = True
        self._tasks = tasks
        
        # Calculate scores and sort
        for task in tasks:
            task.calculate_score()
        self._sorted_tasks = sorted(tasks, key=lambda t: t.score, reverse=True)
        
        # Calculate max score for progress bar scaling
        self._max_score = max((t.score for t in tasks), default=1.0) if tasks else 1.0
        
        # Update table
        display_count = min(TaskConstants.MAX_DISPLAY_TASKS, len(self._sorted_tasks))
        self.setRowCount(display_count)
        
        for i, task in enumerate(self._sorted_tasks[:display_count]):
            self._populate_row(i, task)
        
        # Apply top 3 highlighting
        self._apply_top_highlighting()
        self._ignore_item_changes = False
    
    def highlight_task(self, task_index: int) -> None:
        """Implementation of ITaskDisplayWidget interface"""
        # Find row for this task
        if task_index < len(self._tasks):
            task = self._tasks[task_index]
            for row, sorted_task in enumerate(self._sorted_tasks):
                if sorted_task == task:
                    self.selectRow(row)
                    self._highlight_row(row)
                    break
    
    def clear_highlighting(self) -> None:
        """Implementation of ITaskDisplayWidget interface"""
        self.clearSelection()
        self._restore_normal_colors()
    
    def _populate_row(self, row: int, task: Task):
        """Populate a single table row"""
        # Rank
        rank_text = TaskDisplayFormatter.format_rank(row + 1)
        rank_item = QTableWidgetItem(rank_text)
        rank_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        rank_item.setFlags(rank_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        if row < 3:
            font = rank_item.font()
            font.setBold(True)
            font.setPointSize(font.pointSize() + 1)
            rank_item.setFont(font)
        self.setItem(row, 0, rank_item)
        
        # Task name
        task_name = TaskDisplayFormatter.format_task_name(task)
        task_item = QTableWidgetItem(task_name)
        task_item.setToolTip(TaskDisplayFormatter.get_tooltip_text(task))
        task_item.setFlags(task_item.flags() | Qt.ItemFlag.ItemIsEditable)
        if row < 3:
            font = task_item.font()
            font.setBold(True)
            task_item.setFont(font)
        self.setItem(row, 1, task_item)
        
        # Value
        value_item = QTableWidgetItem(TaskDisplayFormatter.format_value(task.value))
        value_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        value_item.setToolTip(f"Impact/Value rating: {task.value:.1f} out of {TaskConstants.MAX_VALUE:.1f}")
        value_item.setFlags(value_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        if row < 3:
            font = value_item.font()
            font.setBold(True)
            value_item.setFont(font)
        self.setItem(row, 2, value_item)
        
        # Score
        score_item = QTableWidgetItem(TaskDisplayFormatter.format_priority_score(task.score))
        score_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        score_item.setToolTip(f"Priority Score: {task.score:.2f}\nCalculated as Value({task.value:.1f}) ÷ Time({task.time:.1f})")
        score_item.setFlags(score_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        if row < 3:
            font = score_item.font()
            font.setBold(True)
            score_item.setFont(font)
        self.setItem(row, 3, score_item)
        
        # Progress bar (visual score indicator)
        progress_widget = self._create_progress_bar(task.score, row)
        self.setCellWidget(row, 4, progress_widget)
        
        # Delete button
        delete_btn = QPushButton("✕")
        delete_btn.setToolTip("Remove this task")
        delete_btn.setProperty("variant", "danger")
        # Find original task index
        original_index = self._tasks.index(task) if task in self._tasks else -1
        delete_btn.clicked.connect(lambda checked, idx=original_index: self._on_delete_clicked(idx))
        self.setCellWidget(row, 5, delete_btn)
    
    def _create_progress_bar(self, score: float, row: int) -> QWidget:
        """Create a gradient progress bar widget for score visualization"""
        from PyQt6.QtWidgets import QProgressBar
        
        # Calculate percentage based on max score
        percentage = int((score / self._max_score) * 100) if self._max_score > 0 else 0
        percentage = min(100, max(0, percentage))
        
        progress = QProgressBar()
        progress.setMinimum(0)
        progress.setMaximum(100)
        progress.setValue(percentage)
        progress.setTextVisible(False)
        progress.setFixedHeight(12)
        
        # Different gradient colors based on rank
        if row == 0:  # Gold/top
            gradient = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #FFD700, stop:0.5 #FFA500, stop:1 #FF6B35)"
        elif row == 1:  # Silver
            gradient = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #C0C0C0, stop:0.5 #A8A8A8, stop:1 #909090)"
        elif row == 2:  # Bronze
            gradient = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #CD7F32, stop:0.5 #B8722D, stop:1 #A36628)"
        else:  # Others - cyan/teal
            gradient = "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #06B6D4, stop:0.5 #0891B2, stop:1 #0E7490)"
        
        progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: #1F2937;
                border: none;
                border-radius: 6px;
            }}
            QProgressBar::chunk {{
                background: {gradient};
                border-radius: 6px;
            }}
        """)
        
        return progress
    
    def _on_delete_clicked(self, task_index: int):
        """Handle delete button click"""
        if task_index >= 0:
            self.task_delete_requested.emit(task_index)
    
    def keyPressEvent(self, event):
        """Handle keyboard events for task deletion"""
        from PyQt6.QtCore import Qt
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace):
            # Get currently selected row
            selected_rows = self.selectionModel().selectedRows()
            if selected_rows:
                row = selected_rows[0].row()
                # Get the task at this row position (sorted order)
                if 0 <= row < len(self._sorted_tasks):
                    # Find the original task index in unsorted list
                    sorted_task = self._sorted_tasks[row]
                    if sorted_task in self._tasks:
                        original_index = self._tasks.index(sorted_task)
                        self.task_delete_requested.emit(original_index)
        else:
            super().keyPressEvent(event)
    
    def _apply_top_highlighting(self):
        """Apply special highlighting to top 3 tasks"""
        colors = [
            QColor(255, 215, 0, 150),    # Gold
            QColor(192, 192, 192, 150),  # Silver  
            QColor(205, 127, 50, 150)    # Bronze
        ]
        
        for i in range(min(3, self.rowCount())):
            for col in range(4):  # Only color first 4 columns (not delete button)
                item = self.item(i, col)
                if item:
                    item.setBackground(colors[i])
                    item.setForeground(QColor(255, 255, 255))
    
    def _highlight_row(self, row: int):
        """Highlight specific row with bright effect"""
        for j in range(self.columnCount()):
            item = self.item(row, j)
            if item:
                # Preserve existing color but make brighter
                current_bg = item.background()
                if current_bg.color().alpha() > 0:
                    color = current_bg.color()
                    color.setAlpha(255)
                    item.setBackground(color)
                else:
                    item.setBackground(QColor(0, 255, 255, 100))
                
                # Make text bold
                font = item.font()
                font.setBold(True)
                font.setWeight(900)
                item.setFont(font)
    
    def _restore_normal_colors(self):
        """Restore normal row colors"""
        for i in range(self.rowCount()):
            for j in range(self.columnCount()):
                item = self.item(i, j)
                if item:
                    # Reset colors
                    if i < 3:
                        colors = [
                            QColor(255, 215, 0, 150),
                            QColor(192, 192, 192, 150),
                            QColor(205, 127, 50, 150)
                        ]
                        item.setBackground(colors[i])
                        item.setForeground(QColor(255, 255, 255))
                    else:
                        item.setBackground(QColor())
                        item.setForeground(QColor(255, 255, 255))
    
    def _on_cell_clicked(self, row: int, column: int):
        """Handle cell click to find original task index"""
        if row < len(self._sorted_tasks):
            selected_task = self._sorted_tasks[row]
            original_index = self._tasks.index(selected_task)
            self.task_selected.emit(original_index)

    def _on_item_changed(self, item: QTableWidgetItem):
        if self._ignore_item_changes:
            return
        if item.column() != 1:
            return
        row = item.row()
        if row >= len(self._sorted_tasks):
            return
        selected_task = self._sorted_tasks[row]
        if selected_task not in self._tasks:
            return
        original_index = self._tasks.index(selected_task)
        clean_name = TaskValidator.sanitize_task_name(item.text())
        if not TaskValidator.validate_task_name(clean_name):
            self._ignore_item_changes = True
            item.setText(selected_task.task)
            self._ignore_item_changes = False
            QMessageBox.warning(self, "Invalid Task", "Task name cannot be empty.")
            return
        if selected_task.task == clean_name:
            return
        self.task_renamed.emit(original_index, clean_name)
    
    def startDrag(self, supportedActions):
        """Override to provide custom drag data"""
        item = self.currentItem()
        if item and item.row() >= 0:
            row = item.row()
            
            if row < len(self._sorted_tasks):
                selected_task = self._sorted_tasks[row]
                original_index = self._tasks.index(selected_task)
                
                # Create drag operation
                drag = QDrag(self)
                
                # Create and set mime data properly
                mimeData = QMimeData()
                mimeData.setText(f"task_{original_index}")
                drag.setMimeData(mimeData)
                
                # Create visual drag pixmap
                self._create_drag_pixmap(drag, selected_task, row)
                
                # Execute drag
                drag.exec(supportedActions)
    
    def _create_drag_pixmap(self, drag, task, row):
        """Create visual representation of dragged task"""
        task_text = task.task
        if len(task_text) > 25:
            task_text = task_text[:22] + "..."
        
        font = QFont("Arial", 12, QFont.Weight.Bold)
        metrics = QFontMetrics(font)
        
        text_width = metrics.horizontalAdvance(task_text)
        text_height = metrics.height()
        
        padding = 12
        icon_space = 30
        pixmap_width = max(text_width + icon_space + padding * 2, 200)
        pixmap_height = text_height + padding * 2
        
        pixmap = QPixmap(pixmap_width, pixmap_height)
        pixmap.fill(QColor(42, 130, 218, 200))
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setFont(font)
        
        painter.setPen(QColor(255, 255, 255, 255))
        painter.drawRoundedRect(0, 0, pixmap_width-1, pixmap_height-1, 8, 8)
        
        rank_text = f"#{row + 1}"
        painter.setPen(QColor(255, 215, 0, 255))
        painter.drawText(padding, padding + text_height//2 + 2, rank_text)
        
        painter.setPen(QColor(255, 255, 255, 255))
        text_x = padding + icon_space
        text_y = padding + text_height//2 + 4
        painter.drawText(text_x, text_y, task_text)
        
        painter.setPen(QColor(255, 255, 255, 200))
        painter.drawText(pixmap_width - 25, text_y, "📋")
        
        painter.end()
        
        drag.setPixmap(pixmap)
        drag.setHotSpot(QPoint(pixmap_width // 2, pixmap_height // 2))

class ExportButtonWidget(QWidget):
    """Single responsibility: Handle export UI and coordination following SRP
    Implements IExportService protocol methods"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tasks = []
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 10, 0, 0)
        
        # Quick export button (primary)
        self.quick_export_button = QPushButton('📊  Export to Excel')
        self.quick_export_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.quick_export_button.setProperty("variant", "primary")
        self.quick_export_button.clicked.connect(self._quick_export)
        layout.addWidget(self.quick_export_button, alignment=Qt.AlignmentFlag.AlignLeft)
        
        self.setLayout(layout)
    
    def export_tasks(self, tasks: List[Task], file_path: str) -> bool:
        """Implementation of IExportService interface"""
        return ExcelExporter.export_tasks_to_excel(tasks, file_path)
    
    def get_default_export_path(self) -> str:
        """Implementation of IExportService interface"""
        return ExcelExporter.get_default_export_path()
    
    def set_tasks(self, tasks: List[Task]):
        """Set tasks for export"""
        self._tasks = tasks
    
    def _show_export_success(self, title: str, message: str, file_path: str):
        """Show export success message"""
        QMessageBox.information(self, title, message)
    
    def _quick_export(self):
        """Quick export to default location"""
        if not self._tasks:
            QMessageBox.warning(self, "No Data", "There are no tasks to export.")
            return
            
        try:
            self.quick_export_button.setText('Exporting...')
            self.quick_export_button.setEnabled(False)
            
            save_dir = self.get_default_export_path()
            filename = ExcelExporter.generate_filename()
            file_path = os.path.join(save_dir, filename)
            
            success = self.export_tasks(self._tasks, file_path)
            
            self.quick_export_button.setText('Export to Excel')
            self.quick_export_button.setEnabled(True)
            
            if success:
                self._show_export_success(
                    "Export Successful",
                    f"Exported to {save_dir}\n\nFile: {filename}",
                    file_path
                )
            else:
                QMessageBox.critical(self, "Export Error", "Failed to export tasks.")
                
        except Exception as e:
            self.quick_export_button.setText('Export to Excel')
            self.quick_export_button.setEnabled(True)
            QMessageBox.critical(self, "Export Error", f"Export failed:\n{str(e)}")

class PlotResultsCoordinator(QWidget):
    """Single responsibility: Coordinate plot and results display following SRP"""
    
    task_selected = pyqtSignal(int)  # task_index
    task_updated = pyqtSignal(int, float, float)  # task_index, value, time
    task_drag_started = pyqtSignal(int, str)  # task_index, task_data (forwarded from graph and table)
    task_added = pyqtSignal(str)  # task_name (when new task is added)
    task_deleted = pyqtSignal(int)  # task_index (when task is deleted)
    task_renamed = pyqtSignal(int, str)  # task_index, new name
    task_move_finished = pyqtSignal(int, float, float)  # task_index, value, time
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tasks = []
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 5, 10, 10)
        layout.setSpacing(8)
        
        # Title removed - the plot has its own title now

        # Quick add input with enhanced styling
        quick_add_layout = QHBoxLayout()
        quick_add_layout.setSpacing(8)
        
        self.quick_task_input = QLineEdit()
        self.quick_task_input.setPlaceholderText("Add a task")
        self.quick_task_input.setMinimumHeight(38)
        self.quick_task_input.setStyleSheet("""
            QLineEdit {
                background: #1F2937;
                border: 2px solid #374151;
                border-radius: 8px;
                padding: 8px 14px;
                color: #E5E7EB;
                font-size: 13px;
            }
            QLineEdit:focus {
                border: 2px solid #10B981;
                background: #1F2937;
            }
            QLineEdit::placeholder {
                color: #6B7280;
            }
        """)
        self.quick_task_input.returnPressed.connect(self._add_quick_task)
        quick_add_layout.addWidget(self.quick_task_input)

        self.quick_add_button = QPushButton("Add")
        self.quick_add_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.quick_add_button.setProperty("variant", "primary")
        self.quick_add_button.clicked.connect(self._add_quick_task)
        quick_add_layout.addWidget(self.quick_add_button)
        layout.addLayout(quick_add_layout)
        
        # Splitter for plot and results
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Plot widget
        self.plot_widget = InteractivePlotWidget()
        
        # Results panel
        results_widget = QWidget()
        results_widget.setMinimumHeight(300)
        results_widget.setMaximumHeight(500)
        results_layout = QVBoxLayout()
        
        results_title = QLabel("Ranking")
        results_title.setStyleSheet("color: #C9D2DD; font-weight: 600; font-size: 12px; padding: 6px 0px;")
        results_layout.addWidget(results_title)
        
        # Results table
        self.results_table = DraggableTaskTable(self)
        results_layout.addWidget(self.results_table)
        
        # Export buttons
        self.export_widget = ExportButtonWidget()
        results_layout.addWidget(self.export_widget)
        
        results_widget.setLayout(results_layout)
        
        # Add to splitter
        splitter.addWidget(self.plot_widget)
        splitter.addWidget(results_widget)
        splitter.setSizes([300, 350])
        
        layout.addWidget(splitter)
        self.setLayout(layout)
    
    def _connect_signals(self):
        self.plot_widget.task_moved.connect(self._on_task_moved)
        self.plot_widget.task_selected.connect(self._on_task_selected)
        self.plot_widget.task_drag_started.connect(self._on_task_drag_started)  # Connect graph drag signal
        self.plot_widget.task_delete_requested.connect(self._on_task_delete_requested)  # Connect plot delete signal
        self.plot_widget.task_move_finished.connect(self._on_task_move_finished)
        self.results_table.task_selected.connect(self._on_task_selected)
        self.results_table.task_drag_started.connect(self._on_task_drag_started)  # Connect table drag signal
        self.results_table.task_delete_requested.connect(self._on_task_delete_requested)
        self.results_table.task_renamed.connect(self._on_task_renamed)
    
    def _on_task_moved(self, task_index: int, value: float, time: float):
        """Handle task movement in plot"""
        self.task_updated.emit(task_index, value, time)
        self._update_displays()
    
    def _on_task_selected(self, task_index: int):
        """Handle task selection"""
        self.task_selected.emit(task_index)
        self.plot_widget.highlight_task_in_plot(task_index)
        self.results_table.highlight_task(task_index)
    
    def _on_task_drag_started(self, task_index: int, task_data: str):
        """Handle task drag started from either graph or table"""
        self.task_drag_started.emit(task_index, task_data)

    def _add_quick_task(self):
        """Handle quick task addition"""
        task_text = self.quick_task_input.text().strip()
        if task_text:
            self.task_added.emit(task_text)
            self.quick_task_input.clear()

    def _on_task_delete_requested(self, task_index: int):
        """Handle task deletion request from results table or plot"""
        if 0 <= task_index < len(self._tasks):
            self.task_deleted.emit(task_index)

    def _on_task_renamed(self, task_index: int, task_name: str):
        """Handle task rename request from results table"""
        if 0 <= task_index < len(self._tasks):
            self.task_renamed.emit(task_index, task_name)

    def _on_task_move_finished(self, task_index: int, value: float, time: float):
        """Forward move completion so persistence can happen once per drag."""
        self.task_move_finished.emit(task_index, value, time)
    
    def set_tasks(self, tasks: List[Task]):
        """Set tasks for display"""
        self._tasks = tasks
        self._update_displays()
    
    def _update_displays(self):
        """Update all displays with current tasks"""
        self.plot_widget.update_plot(self._tasks)
        self.results_table.refresh_display(self._tasks)
        self.export_widget.set_tasks(self._tasks)
    
    def highlight_task(self, task_index: int):
        """Highlight task across all widgets"""
        self.plot_widget.highlight_task_in_plot(task_index)
        self.results_table.highlight_task(task_index)
    
    def clear_highlighting(self):
        """Clear highlighting across all widgets"""
        self.plot_widget.clear_highlighting()
        self.results_table.clear_highlighting() 
