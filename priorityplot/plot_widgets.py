from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget, 
                             QTableWidgetItem, QLabel, QMessageBox, QAbstractItemView, 
                             QHeaderView, QInputDialog, QSplitter, QApplication)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QThread, QPoint, QMimeData
from PyQt6.QtGui import QColor, QFont, QDrag, QPixmap, QPainter, QFontMetrics, QCursor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
from typing import List, Optional
from datetime import datetime
import os

from .interfaces import IPlotWidget, ITaskDisplayWidget, IExportService
from .model import (Task, TaskConstants, TaskStateManager, TaskDisplayFormatter, 
                   ExcelExporter, get_top_tasks, get_task_colors)

class InteractivePlotWidget(QWidget):
    """Single responsibility: Handle interactive plot functionality following SRP
    Implements IPlotWidget protocol methods"""
    
    task_moved = pyqtSignal(int, float, float)  # task_index, value, time
    task_selected = pyqtSignal(int)  # task_index
    task_drag_started = pyqtSignal(int, str)  # task index, task data for external drops
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tasks = []
        self._state_manager = TaskStateManager()
        self._setup_plot()
        self._setup_interaction()
        
        # Interaction state
        self.dragging = False
        self.drag_index = None
        self.current_annotation = None
        self.highlight_scatter = None
        self.highlight_elements = []
        self.drag_threshold = 5  # pixels before starting drag
        self.initial_click_pos = None
        self.is_external_drag = False
        self.drag_preview_annotation = None
        
        # CRITICAL FIX: Store original values to prevent unintended changes
        self.original_task_value = None
        self.original_task_time = None
        
    def _setup_plot(self):
        layout = QVBoxLayout()
        
        # Create matplotlib figure
        self.figure = Figure(figsize=(8, 5), facecolor='#353535')
        self.canvas = FigureCanvas(self.figure)
        self.ax = self.figure.add_subplot(111)
        
        # Set modern plot style
        self.ax.set_facecolor('#353535')
        self.ax.grid(True, linestyle='--', alpha=0.3, color='#555555')
        self.ax.spines['bottom'].set_color('#555555')
        self.ax.spines['top'].set_color('#555555')
        self.ax.spines['left'].set_color('#555555')
        self.ax.spines['right'].set_color('#555555')
        
        # Set labels
        self.ax.set_xlabel('* Value (Impact/Importance)', color='white', fontsize=11, fontweight='bold')
        self.ax.set_ylabel('Time Investment (Hours)', color='white', fontsize=11, fontweight='bold')
        self.ax.set_title('Priority Matrix • Click table row to highlight', color='white', fontsize=13, fontweight='bold', pad=10)
        
        # Style ticks
        self.ax.tick_params(colors='white', which='both')
        
        # Set fixed axis limits
        self.ax.set_xlim(0, TaskConstants.MAX_VALUE)
        self.ax.set_ylim(0, TaskConstants.MAX_TIME)
        
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
        colors = get_task_colors(tasks, self._state_manager.moved_points)
        
        # Plot regular points
        non_top_indices = [i for i in range(len(tasks)) if i not in top_3_indices]
        if non_top_indices:
            self.ax.scatter(
                [x_data[i] for i in non_top_indices],
                [y_data[i] for i in non_top_indices],
                c=[colors[i] for i in non_top_indices],
                picker=True,
                alpha=0.7,
                s=100
            )
        
        # Plot top 3 with special styling
        for rank, task_index in enumerate(top_3_indices, 1):
            if task_index < len(tasks):
                task_x = x_data[task_index]
                task_y = y_data[task_index]
                self.ax.plot(task_x, task_y, 'o', markersize=20, markerfacecolor='none', 
                            markeredgecolor=colors[task_index], markeredgewidth=2)
                self.ax.text(task_x, task_y, str(rank), ha='center', va='center', 
                            fontsize=14, fontweight='bold', color=colors[task_index])
        
        # Update scatter reference for event handling
        self.scatter = self.ax.scatter(x_data, y_data, c=colors, picker=True, alpha=0)
        
        # Adjust layout
        self.figure.subplots_adjust(left=0.12, bottom=0.12, right=0.95, top=0.92)
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
            s=400, facecolors='none',
            edgecolors='#FFD700', linewidths=4,
            alpha=0.9, zorder=10
        )
        
        # Add pulsing effect
        pulse_scatter = self.ax.scatter(
            [task.value], [task.time],
            s=500, facecolors='none',
            edgecolors='#FFD700', linewidths=2,
            alpha=0.5, zorder=9
        )
        self.highlight_elements.append(pulse_scatter)
        
        # Add text label
        highlight_text = self.ax.text(
            task.value, task.time + 0.3,
            f"🎯 {task.task[:20]}{'...' if len(task.task) > 20 else ''}",
            ha='center', va='bottom',
            fontsize=10, fontweight='bold',
            color='#FFD700',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='#2a82da', alpha=0.8),
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
        self.ax.set_facecolor('#353535')
        self.ax.grid(True, linestyle='--', alpha=0.3, color='#555555')
        self.ax.spines['bottom'].set_color('#555555')
        self.ax.spines['top'].set_color('#555555')
        self.ax.spines['left'].set_color('#555555')
        self.ax.spines['right'].set_color('#555555')
        
        self.ax.set_xlabel('* Value (Impact/Importance)', color='white', fontsize=11, fontweight='bold')
        self.ax.set_ylabel('Time Investment (Hours)', color='white', fontsize=11, fontweight='bold')
        self.ax.set_title('Priority Matrix • Click table row to highlight', color='white', fontsize=13, fontweight='bold', pad=10)
        
        self.ax.tick_params(colors='white', which='both')
        self.ax.set_xlim(0, TaskConstants.MAX_VALUE)
        self.ax.set_ylim(0, TaskConstants.MAX_TIME)
    
    def _on_press(self, event):
        if event.inaxes != self.ax:
            return
        contains, ind = self.scatter.contains(event)
        if contains:
            task_index = ind["ind"][0]
            if event.button == 1:  # Left mouse button
                self.initial_click_pos = (event.x, event.y)
                self.drag_index = task_index
                self.task_selected.emit(task_index)
    
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
            xytext=(10, -30),
            textcoords='offset points',
            bbox=dict(
                boxstyle='round,pad=0.5',
                facecolor='#FFD700',
                edgecolor='#FF6B35',
                alpha=0.9,
                linewidth=2
            ),
            color='#000000',
            fontsize=10,
            fontweight='bold',
            zorder=20,
            arrowprops=dict(
                arrowstyle='->',
                connectionstyle='arc3,rad=0.1',
                color='#FF6B35',
                linewidth=2
            )
        )
        
        # Add pulsing highlight to the dragged point
        self.highlight_scatter = self.ax.scatter(
            [task.value], [task.time],
            s=600, facecolors='none',
            edgecolors='#FFD700', linewidths=6,
            alpha=0.8, zorder=15,
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
        self.auto_update_timer.start(100)
    
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
                f"📅 Drop to schedule: {task.task[:15]}{'...' if len(task.task) > 15 else ''}"
            )
            self.drag_preview_annotation.get_bbox_patch().set_facecolor('#00FF7F')
            self.drag_preview_annotation.get_bbox_patch().set_edgecolor('#00CC66')
            self.drag_preview_annotation.set_color('#000000')
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
            self.drag_preview_annotation.get_bbox_patch().set_facecolor('#FFD700')
            self.drag_preview_annotation.get_bbox_patch().set_edgecolor('#FF6B35')
            self.drag_preview_annotation.set_color('#000000')
        
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
        
        # Draw calendar icon
        painter.setPen(QColor(0, 100, 50, 255))
        painter.drawText(padding, padding + text_height//2 + 5, "📅")
        
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
        
        if self.dragging and self.drag_index is not None:
            # Emit final update for internal drags
            if not self.is_external_drag and self.drag_index < len(self._tasks):
                task = self._tasks[self.drag_index]
                self.task_moved.emit(self.drag_index, task.value, task.time)
                # Full redraw
                self.update_plot(self._tasks)
        
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
                xytext=(10, 10),
                textcoords='offset points',
                bbox=dict(
                    boxstyle='round,pad=0.5',
                    fc='#2a82da',
                    ec='#555555',
                    alpha=0.9
                ),
                color='white',
                fontsize=9,
                fontweight='bold',
                arrowprops=dict(
                    arrowstyle='->',
                    connectionstyle='arc3,rad=0.2',
                    color='#555555',
                    linewidth=1.5
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
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tasks = []
        self._sorted_tasks = []
        self._parent_widget = parent
        self._setup_table()
        
    def _setup_table(self):
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(['🏆', 'Task', 'Value', 'Score'])
        
        # Enhanced styling
        self.setStyleSheet("""
            QTableWidget {
                font-size: 14px;
                border-radius: 6px;
                border: 2px solid #555555;
                background-color: #404040;
                selection-background-color: #2a82da;
                gridline-color: #666666;
            }
            QTableWidget::item {
                padding: 12px 8px;
                border-bottom: 1px solid #555555;
                min-height: 16px;
            }
            QTableWidget::item:hover {
                background-color: #555555;
                border: 1px solid #2a82da;
            }
            QTableWidget::item:selected {
                background-color: #2a82da;
                color: white;
                font-weight: bold;
            }
            QHeaderView::section {
                background-color: #555555;
                color: white;
                padding: 12px 8px;
                font-size: 13px;
                font-weight: bold;
                border: 1px solid #666666;
                text-align: center;
            }
        """)
        
        # Table settings
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.verticalHeader().setDefaultSectionSize(35)
        
        # Column widths
        header = self.horizontalHeader()
        header.setStretchLastSection(True)
        self.setColumnWidth(0, 60)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.setColumnWidth(2, 90)
        self.setColumnWidth(3, 90)
        
        # Enable drag
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.DragDropMode.DragOnly)
        self.setDefaultDropAction(Qt.DropAction.CopyAction)
        
        # Connect signals
        self.cellClicked.connect(self._on_cell_clicked)
    
    def refresh_display(self, tasks: List[Task]) -> None:
        """Implementation of ITaskDisplayWidget interface"""
        self._tasks = tasks
        
        # Calculate scores and sort
        for task in tasks:
            task.calculate_score()
        self._sorted_tasks = sorted(tasks, key=lambda t: t.score, reverse=True)
        
        # Update table
        display_count = min(TaskConstants.MAX_DISPLAY_TASKS, len(self._sorted_tasks))
        self.setRowCount(display_count)
        
        for i, task in enumerate(self._sorted_tasks[:display_count]):
            self._populate_row(i, task)
        
        # Apply top 3 highlighting
        self._apply_top_highlighting()
    
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
        if row < 3:
            font = task_item.font()
            font.setBold(True)
            task_item.setFont(font)
        self.setItem(row, 1, task_item)
        
        # Value
        value_item = QTableWidgetItem(TaskDisplayFormatter.format_value(task.value))
        value_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        value_item.setToolTip(f"Impact/Value rating: {task.value:.1f} out of {TaskConstants.MAX_VALUE:.1f}")
        if row < 3:
            font = value_item.font()
            font.setBold(True)
            value_item.setFont(font)
        self.setItem(row, 2, value_item)
        
        # Score
        score_item = QTableWidgetItem(TaskDisplayFormatter.format_priority_score(task.score))
        score_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        score_item.setToolTip(f"Priority Score: {task.score:.2f}\nCalculated as Value({task.value:.1f}) ÷ Time({task.time:.1f})")
        if row < 3:
            font = score_item.font()
            font.setBold(True)
            score_item.setFont(font)
        self.setItem(row, 3, score_item)
    
    def _apply_top_highlighting(self):
        """Apply special highlighting to top 3 tasks"""
        colors = [
            QColor(255, 215, 0, 150),    # Gold
            QColor(192, 192, 192, 150),  # Silver  
            QColor(205, 127, 50, 150)    # Bronze
        ]
        
        for i in range(min(3, self.rowCount())):
            for col in range(4):
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

class ExportWorker(QThread):
    """Single responsibility: Handle Excel export in background following SRP"""
    
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)
    
    def __init__(self, task_list: List[Task], file_path: str):
        super().__init__()
        self.task_list = task_list
        self.file_path = file_path
        
    def run(self):
        try:
            self.progress.emit("Creating Excel workbook...")
            success = ExcelExporter.export_tasks_to_excel(self.task_list, self.file_path)
            
            if success:
                self.progress.emit("Export completed!")
                self.finished.emit(self.file_path)
            else:
                self.error.emit("Failed to export tasks to Excel")
                
        except Exception as e:
            self.error.emit(str(e))

class ExportButtonWidget(QWidget):
    """Single responsibility: Handle export UI and coordination following SRP
    Implements IExportService protocol methods"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tasks = []
        self._export_worker = None
        self._setup_ui()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        
        # Quick export button (primary)
        self.quick_export_button = QPushButton('📊 Export to Excel (Quick)')
        self.quick_export_button.clicked.connect(self._quick_export)
        self.quick_export_button.setToolTip("💾 Save to Downloads folder - RECOMMENDED")
        self.quick_export_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 12px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        layout.addWidget(self.quick_export_button)
        
        # Custom location export (secondary)
        self.export_button = QPushButton('📁 Export to Custom Location')
        self.export_button.clicked.connect(self._custom_export)
        self.export_button.setToolTip("💾 Choose save location")
        self.export_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        layout.addWidget(self.export_button)
        
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
    
    def _quick_export(self):
        """Quick export to default location"""
        if not self._tasks:
            QMessageBox.warning(self, "❌ No Data", "There are no tasks to export!")
            return
            
        try:
            self.quick_export_button.setText('⏳ Creating Excel file...')
            self.quick_export_button.setEnabled(False)
            
            save_dir = self.get_default_export_path()
            filename = ExcelExporter.generate_filename()
            file_path = os.path.join(save_dir, filename)
            
            self.quick_export_button.setText('⏳ Exporting...')
            success = self.export_tasks(self._tasks, file_path)
            
            self.quick_export_button.setText('📊 Export to Excel (Quick)')
            self.quick_export_button.setEnabled(True)
            
            if success:
                folder_name = os.path.basename(save_dir)
                QMessageBox.information(self, "✅ Quick Export Successful!", 
                                      f"🎉 Exported to {folder_name} folder!\n\n"
                                      f"📁 File: {filename}")
            else:
                QMessageBox.critical(self, "❌ Export Error", "Failed to export tasks.")
                
        except Exception as e:
            self.quick_export_button.setText('📊 Export to Excel (Quick)')
            self.quick_export_button.setEnabled(True)
            QMessageBox.critical(self, "❌ Export Error", f"Export failed:\n{str(e)}")
    
    def _custom_export(self):
        """Export to custom location using input dialog"""
        if not self._tasks:
            QMessageBox.warning(self, "❌ No Data", "There are no tasks to export!")
            return
            
        default_filename = ExcelExporter.generate_filename()
        default_path = self.get_default_export_path()
        
        folder_path, ok = QInputDialog.getText(
            self, "📁 Choose Export Folder",
            f"💾 Enter folder path to save '{default_filename}':\n\n"
            f"💡 Leave empty to use: {default_path}",
            text=default_path
        )
        
        if not ok:
            return
            
        if not folder_path.strip():
            folder_path = default_path
        else:
            folder_path = os.path.expanduser(folder_path.strip())
        
        # Validate and create if needed
        try:
            if not os.path.exists(folder_path):
                reply = QMessageBox.question(
                    self, "📁 Create Folder?", 
                    f"Create folder?\n{folder_path}",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    os.makedirs(folder_path, exist_ok=True)
                else:
                    return
            
            file_path = os.path.join(folder_path, default_filename)
            
            # Start worker thread
            self.export_button.setText('⏳ Starting export...')
            self.export_button.setEnabled(False)
            
            self._export_worker = ExportWorker(self._tasks, file_path)
            self._export_worker.finished.connect(self._on_export_finished)
            self._export_worker.error.connect(self._on_export_error)
            self._export_worker.progress.connect(self._on_export_progress)
            self._export_worker.start()
            
        except Exception as e:
            QMessageBox.warning(self, "❌ Invalid Path", f"Invalid path:\n{str(e)}")
    
    def _on_export_finished(self, file_path: str):
        self.export_button.setText('📁 Export to Custom Location')
        self.export_button.setEnabled(True)
        QMessageBox.information(self, "✅ Export Successful!", 
                              f"🎉 Exported successfully!\n\n📁 {file_path}")
    
    def _on_export_error(self, error_message: str):
        self.export_button.setText('📁 Export to Custom Location')
        self.export_button.setEnabled(True)
        QMessageBox.critical(self, "❌ Export Error", f"Export failed:\n{error_message}")
    
    def _on_export_progress(self, message: str):
        self.export_button.setText(f"⏳ {message}")

class PlotResultsCoordinator(QWidget):
    """Single responsibility: Coordinate plot and results display following SRP"""
    
    task_selected = pyqtSignal(int)  # task_index
    task_updated = pyqtSignal(int, float, float)  # task_index, value, time
    task_drag_started = pyqtSignal(int, str)  # task_index, task_data (forwarded from graph and table)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._tasks = []
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(5, 0, 5, 5)
        
        # Header with updated instructions
        self.priority_header = QLabel(">> Drag tasks to prioritize • Drag from graph OR table to calendar to schedule • Top 3 priorities shown below")
        self.priority_header.setStyleSheet("color: #ffffff; font-weight: bold; padding: 5px; font-size: 14px;")
        layout.addWidget(self.priority_header)
        
        # Splitter for plot and results
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Plot widget
        self.plot_widget = InteractivePlotWidget()
        
        # Results panel
        results_widget = QWidget()
        results_widget.setMinimumHeight(300)
        results_widget.setMaximumHeight(500)
        results_layout = QVBoxLayout()
        
        # Header
        live_header = QLabel("🏆 Live Priority Ranking (Drag to Calendar →)")
        live_header.setStyleSheet("""
            color: #ffffff; font-weight: bold; font-size: 16px; 
            padding: 8px; background-color: #2a82da; 
            border-radius: 6px; margin-bottom: 5px;
        """)
        results_layout.addWidget(live_header)
        
        # Enhanced drag instruction
        drag_instruction = QLabel("✨ Drag tasks from GRAPH or TABLE below to schedule them on the calendar!")
        drag_instruction.setStyleSheet("""
            color: #00FF7F; font-weight: bold; font-size: 12px; 
            padding: 8px 12px; background-color: #2a4040; 
            border: 2px dashed #00FF7F; border-radius: 6px; 
            margin-bottom: 8px;
        """)
        drag_instruction.setWordWrap(True)
        results_layout.addWidget(drag_instruction)
        
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
        self.results_table.task_selected.connect(self._on_task_selected)
        self.results_table.task_drag_started.connect(self._on_task_drag_started)  # Connect table drag signal
    
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
        print(f"🎯 Task drag started from coordinator: {task_index} - {task_data}")
        self.task_drag_started.emit(task_index, task_data)
    
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