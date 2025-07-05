# --- START OF MODIFIED FILE media_organizer_orange_themed.py ---

import sys
import os
import shutil
from datetime import datetime
import threading
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLineEdit, QLabel, QProgressBar, QCheckBox, QGridLayout,
                           QDialog, QScrollArea, QFormLayout, QMessageBox, QFileDialog, QSizePolicy,
                           QFrame)
# Removed QPainter, QLinearGradient, QPalette as background is handled by stylesheet
from PyQt6.QtGui import QColor, QFont, QGuiApplication, QIcon, QAction
from PyQt6.QtCore import Qt, QTimer

# --- Constants for Styling ---
# Orange Theme Colors (From Original Media)
ORANGE_COLORS = {
    "background": "#1B2333",       # Consistent deep background
    "secondary_bg": "#1B2333",    # Use the same for all backgrounds
    "primary": "#FFA500",         # Vibrant orange for primary actions
    "secondary": "#FF8C00",       # Darker orange for secondary actions
    "accent": "#FFB347",          # Lighter orange for accents (e.g., Browse buttons)
    "text_primary": "#FFFFFF",     # White text for high contrast on dark orange
    "text_secondary": "#FFD580",  # Light orange/yellow for secondary text
    "border": "#FF8C00",          # Border color, related to background
    "input_bg": "#334155",        # Using the distinct input bg from OFFICE for better contrast
    "success": "#66BB6A",          # Green (Standard)
    "warning": "#FFA726",          # Orange (Standard)
    "danger": "#EF5350",           # Red (Standard)
    "progress_bar_bg": "#FF8C00", # Background of the progress bar area (matches secondary button)
    "progress_bar_chunk": "#FFA500", # Bright orange chunk
}

FONT_FAMILY = "Segoe UI"      # Consistent font

class MediaOrganizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Let's Sort Your Media Files!")

        # --- Use the Orange Theme ---
        self.current_colors = ORANGE_COLORS

        # --- Media File Categories (From Original Media) ---
        self.file_categories = {
            "Videos": [".mp4", ".avi", ".mov", ".wmv", ".mkv", ".flv", ".webm", ".m4v", ".mpeg", ".mpg", ".3gp"],
            "Sound Effects": [".wav", ".mp3", ".ogg", ".flac", ".aac", ".m4a", ".aiff", ".wma"],
            "Background Music": [".wav", ".mp3", ".ogg", ".flac", ".aac", ".m4a", ".aiff", ".wma"],
            "Images": [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".gif", ".webp", ".svg", ".heif", ".heic", ".raw"],
            "Overlays": [".mov", ".png", ".tiff", ".webm", ".avi", ".mkv"], # Note overlaps
            "GIFs": [".gif", ".apng"], # Note overlaps
            "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".tar.gz", ".tar.bz2", ".tar.xz", ".cab", ".iso", ".dmg"],
            "Project Files": [".prproj", ".fcpxml", ".veg", ".drp", ".sesx", ".als", ".cpr", ".blend", ".aep", ".c4d", ".ma", ".mb", ".max"],
            "Vector & Design Files": [".ai", ".eps", ".psd", ".sketch", ".fig", ".indd", ".xd"],
            "Subtitles & Captions": [".srt", ".vtt", ".ass", ".sub"],
            "3D & Animation Files": [".obj", ".fbx", ".stl", ".gltf", ".glb", ".bvh"],
            "Fonts & Text Styles": [".ttf", ".otf", ".woff", ".woff2"],
            "Code & Scripts": [".jsx", ".py", ".lua", ".xml"]
            # Consider adding an "Other" category if desired
        }
        # Sort categories alphabetically for consistent display order
        self.file_categories = dict(sorted(self.file_categories.items()))
        self.custom_folder_names = {k: k for k in self.file_categories.keys()}

        # --- State (From Personal/Office refactor) ---
        self.unavailable_file_types = set()
        self.is_organizing = False
        self.undo_stack = []  # Add undo stack to track file movements

        # --- Window Size (Adapted from Personal/Office refactor) ---
        screen = QGuiApplication.primaryScreen().availableGeometry()
        max_width, max_height = screen.width(), screen.height()
        # Default size might need adjustment based on category list length
        self.setGeometry(100, 100, min(950, max_width - 100), min(700, max_height - 100))
        self.setMinimumSize(700, 550) # Adjusted minimum
        self.setMaximumSize(max_width, max_height)

        self.setup_ui()
        self.update_stylesheet() # Apply the orange theme stylesheet

    def setup_ui(self):
        # Structure largely taken from PERSONAL/OFFICE refactor
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(25, 20, 25, 20) # Spacing from refactor
        main_layout.setSpacing(15) # Adjusted spacing

        # --- Header (Style from refactor) ---
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(15)

        # Time/Greeting (Left)
        time_greeting_widget = QWidget()
        time_greeting_layout = QVBoxLayout(time_greeting_widget)
        time_greeting_layout.setContentsMargins(0, 0, 0, 0)
        time_greeting_layout.setSpacing(2)

        self.time_label = QLabel(self.get_current_time())
        self.time_label.setObjectName("TimeLabel")
        self.time_label.setFont(QFont(FONT_FAMILY, 24, QFont.Weight.Bold))
        time_greeting_layout.addWidget(self.time_label)

        self.greeting_label = QLabel(self.get_greeting()) # Use Media greeting
        self.greeting_label.setObjectName("GreetingLabel")
        self.greeting_label.setFont(QFont(FONT_FAMILY, 12))
        time_greeting_layout.addWidget(self.greeting_label)

        header_layout.addWidget(time_greeting_widget)
        header_layout.addStretch(1)

        # App title (Right)
        app_title = QLabel("Media File Organizer") # Updated title
        app_title.setObjectName("app_title")
        app_title.setFont(QFont(FONT_FAMILY, 20, QFont.Weight.Bold))
        header_layout.addWidget(app_title)

        main_layout.addWidget(header_widget)

        # --- Divider (Style from refactor) ---
        divider1 = QFrame()
        divider1.setObjectName("divider")
        divider1.setFrameShape(QFrame.Shape.HLine)
        divider1.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(divider1)

        # --- Input Section (Layout from refactor, Placeholders from Media) ---
        input_section_widget = QWidget()
        input_section_layout = QVBoxLayout(input_section_widget)
        input_section_layout.setContentsMargins(0, 5, 0, 5) # Adjusted margins
        input_section_layout.setSpacing(12)

        # Source Directory
        source_widget = QWidget()
        source_layout = QHBoxLayout(source_widget)
        source_layout.setContentsMargins(0, 0, 0, 0)
        source_layout.setSpacing(10)
        source_label = QLabel("Source Folder:") # Consistent label
        source_label.setFont(QFont(FONT_FAMILY, 10, QFont.Weight.Bold))
        source_layout.addWidget(source_label)
        self.source_entry = QLineEdit()
        self.source_entry.setPlaceholderText("Where are the files you want to organize?...") # Placeholder from Media
        source_layout.addWidget(self.source_entry)
        source_btn = QPushButton("Browse")
        source_btn.setObjectName("AccentButton") # Use accent color for browse
        source_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        source_btn.clicked.connect(self.browse_source)
        source_layout.addWidget(source_btn)
        input_section_layout.addWidget(source_widget)

        # Destination Directory
        dest_widget = QWidget()
        dest_layout = QHBoxLayout(dest_widget)
        dest_layout.setContentsMargins(0, 0, 0, 0)
        dest_layout.setSpacing(10)
        dest_label = QLabel("Destination Folder:") # Consistent label
        dest_label.setFont(QFont(FONT_FAMILY, 10, QFont.Weight.Bold))
        dest_layout.addWidget(dest_label)
        self.dest_entry = QLineEdit()
        self.dest_entry.setPlaceholderText("Where do you want to organize your files?...") # Placeholder from Media
        dest_layout.addWidget(self.dest_entry)
        dest_btn = QPushButton("Browse")
        dest_btn.setObjectName("AccentButton") # Use accent color for browse
        dest_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        dest_btn.clicked.connect(self.browse_destination)
        dest_layout.addWidget(dest_btn)
        input_section_layout.addWidget(dest_widget)
        main_layout.addWidget(input_section_widget)

        # --- File Type Selection (Layout/Functionality from refactor, Categories from Media) ---
        file_type_widget = QWidget()
        file_type_layout = QVBoxLayout(file_type_widget)
        file_type_layout.setContentsMargins(5, 10, 5, 10)
        file_type_layout.setSpacing(8)
        file_type_header_layout = QHBoxLayout()
        file_type_label = QLabel("Select file types to organize:") # Text from Media
        file_type_label.setFont(QFont(FONT_FAMILY, 10, QFont.Weight.Bold))
        file_type_header_layout.addWidget(file_type_label)
        file_type_header_layout.addStretch()
        select_all_btn = QPushButton("Select All") # Added from refactor
        select_all_btn.setObjectName("TextButton")
        select_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        select_all_btn.clicked.connect(lambda: self.toggle_all_checkboxes(True))
        file_type_header_layout.addWidget(select_all_btn)
        deselect_all_btn = QPushButton("Deselect All") # Added from refactor
        deselect_all_btn.setObjectName("TextButton")
        deselect_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        deselect_all_btn.clicked.connect(lambda: self.toggle_all_checkboxes(False))
        file_type_header_layout.addWidget(deselect_all_btn)
        file_type_layout.addLayout(file_type_header_layout)

        checkbox_scroll = QScrollArea()
        checkbox_scroll.setObjectName("CheckboxScrollArea")
        checkbox_scroll.setWidgetResizable(True)
        checkbox_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        checkbox_scroll.setMaximumHeight(180) # Max height from refactor
        self.file_types = list(self.file_categories.keys()) # Use Media categories
        self.check_vars = {}
        checkbox_widget = QWidget()
        checkbox_widget.setObjectName("CheckboxWidget")
        checkbox_layout = QGridLayout(checkbox_widget)
        checkbox_layout.setContentsMargins(5, 5, 15, 5)
        checkbox_layout.setSpacing(10)
        checkbox_layout.setHorizontalSpacing(20)
        num_cols = 3 # Keep 3 columns as in original example
        for i, file_type in enumerate(self.file_types):
            checkbox = QCheckBox(file_type)
            checkbox.setChecked(True)
            self.check_vars[file_type] = checkbox
            checkbox_layout.addWidget(checkbox, i // num_cols, i % num_cols)
        checkbox_scroll.setWidget(checkbox_widget)
        file_type_layout.addWidget(checkbox_scroll)
        main_layout.addWidget(file_type_widget)

        # --- Progress and Status (Layout/Functionality from refactor) ---
        progress_widget = QWidget()
        progress_layout = QVBoxLayout(progress_widget)
        progress_layout.setContentsMargins(0, 5, 0, 5)
        progress_layout.setSpacing(5)
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        progress_layout.addWidget(self.progress_bar)
        self.status_label = QLabel("Ready to organize.") # Default status
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setFont(QFont(FONT_FAMILY, 10))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        progress_layout.addWidget(self.status_label)
        main_layout.addWidget(progress_widget)

        main_layout.addStretch(1)

        # --- Divider (Style from refactor) ---
        divider2 = QFrame()
        divider2.setObjectName("divider")
        divider2.setFrameShape(QFrame.Shape.HLine)
        divider2.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(divider2)

        # --- Action Buttons (Layout from refactor, Text from Media) ---
        action_button_widget = QWidget()
        action_button_layout = QHBoxLayout(action_button_widget)
        action_button_layout.setContentsMargins(0, 5, 0, 0)
        action_button_layout.setSpacing(10)
        
        # Add Undo button
        self.undo_btn = QPushButton("Undo Last Action")
        self.undo_btn.setObjectName("SecondaryButton")
        self.undo_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.undo_btn.clicked.connect(self.undo_last_action)
        self.undo_btn.setEnabled(False)  # Initially disabled
        action_button_layout.addWidget(self.undo_btn)
        
        self.custom_folder_btn = QPushButton("Customize Folder Names")
        self.custom_folder_btn.setObjectName("SecondaryButton")
        self.custom_folder_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.custom_folder_btn.clicked.connect(self.open_custom_style_dialog)
        action_button_layout.addWidget(self.custom_folder_btn)
        
        # Add About button
        about_btn = QPushButton("About")
        about_btn.setObjectName("SecondaryButton") # Use same style as custom folder button
        about_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        about_btn.clicked.connect(self.show_about_dialog)
        action_button_layout.addWidget(about_btn)
        
        action_button_layout.addStretch(1)
        self.organize_btn = QPushButton("Start Organizing") # Changed from 'Organize Files' to 'Start Organizing'
        self.organize_btn.setObjectName("PrimaryButton") # Use primary style
        self.organize_btn.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Bold)) # Consistent bold style
        self.organize_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.organize_btn.clicked.connect(self.start_organizing)
        action_button_layout.addWidget(self.organize_btn)
        main_layout.addWidget(action_button_widget)

        # --- Footer (Consistent and friendly) ---
        footer = QLabel(f"© {datetime.now().year} Media File Organizer")
        footer.setFont(QFont(FONT_FAMILY, 9))
        footer.setObjectName("FooterLabel")
        footer.setAlignment(Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(footer)

        # --- Timer for Time/Greeting Update (From refactor) ---
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_time_and_greeting)
        self.update_timer.start(1000)

        # --- Apply initial colors ---
        self.update_ui_colors() # Set initial label colors etc.


    # --- Methods like toggle_all_checkboxes, browse_source, browse_destination ---
    # --- open_custom_style_dialog, save_custom_names remain the same as refactor ---
    def toggle_all_checkboxes(self, state):
        for checkbox in self.check_vars.values():
            checkbox.setChecked(state)

    def browse_source(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Source Folder")
        if folder:
            self.source_entry.setText(folder)

    def browse_destination(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if folder:
            self.dest_entry.setText(folder)

    def open_custom_style_dialog(self):
        # Dialog inherits main window stylesheet (structure from refactor)
        dialog = QDialog(self)
        dialog.setWindowTitle("Customize Folder Names")
        dialog.setMinimumWidth(500)
        dialog.setMinimumHeight(450) # Increased height for longer media category list

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(15)

        instruction_label = QLabel("Enter the desired folder name for each category:", dialog)
        instruction_label.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Bold))
        layout.addWidget(instruction_label)

        scroll_area = QScrollArea(dialog)
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("DialogScrollArea") # Style inherits

        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setContentsMargins(5, 5, 15, 5)

        self.custom_name_entries = {}
        # Use the current (sorted) Media categories
        sorted_categories = sorted(self.file_categories.keys())
        for category in sorted_categories:
            label = QLabel(f"{category}:", form_widget)
            entry = QLineEdit(form_widget)
            entry.setText(self.custom_folder_names.get(category, category))
            self.custom_name_entries[category] = entry
            form_layout.addRow(label, entry)

        scroll_area.setWidget(form_widget)
        layout.addWidget(scroll_area)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        cancel_btn = QPushButton("Cancel", dialog)
        cancel_btn.setObjectName("SecondaryButton") # Use secondary style
        cancel_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_btn.clicked.connect(dialog.reject)
        button_layout.addWidget(cancel_btn)
        save_btn = QPushButton("Save Changes", dialog)
        save_btn.setObjectName("PrimaryButton") # Use primary style
        save_btn.setDefault(True)
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.clicked.connect(lambda: self.save_custom_names(dialog))
        button_layout.addWidget(save_btn)

        layout.addLayout(button_layout)
        dialog.exec()

    def save_custom_names(self, dialog):
        # Logic from refactor
        for category, entry in self.custom_name_entries.items():
            new_name = entry.text().strip()
            if new_name:
                # Basic validation: replace invalid filename characters
                invalid_chars = r'<>:"/\|?*'
                for char in invalid_chars:
                    new_name = new_name.replace(char, '_')
                self.custom_folder_names[category] = new_name
            else:
                # Revert to default if emptied
                self.custom_folder_names[category] = category
        dialog.accept()
        self.update_status("Custom folder names saved.", "info")

    # --- organize_files, reset_ui_state, update_status, _update_status_ui ---
    # --- show_unavailable_types_popup, start_organizing remain functionally the same ---
    # --- as refactor, but use orange theme colors via update_status ---

    def start_organizing(self):
        """Start the organization process."""
        if self.is_organizing:
            self.cancel_organizing()
            return
        
        self.is_organizing = True
        self.organize_btn.setText("Cancel Organization")
        self.organize_btn.setObjectName("DangerButton")
        self.update_stylesheet()
        self.progress_bar.setValue(0)
        self.update_status("Starting organization...", "info")
        
        # Start organization in a separate thread
        self.organize_thread = threading.Thread(target=self.organize_files)
        self.organize_thread.daemon = True
        self.organize_thread.start()

    def cancel_organizing(self):
        """Cancel the ongoing organization process."""
        self.is_organizing = False
        self.update_status("Organization cancelled by user.", "warning")
        self.reset_ui_state()

    def reset_ui_state(self):
        """Reset UI to initial state after organization."""
        self.is_organizing = False
        self.organize_btn.setText("Start Organizing")
        self.organize_btn.setObjectName("PrimaryButton")
        self.update_stylesheet()
        self.progress_bar.setValue(0)

    def organize_files(self):
        """Organize files in the background thread."""
        try:
            if not self.source_entry.text() or not self.dest_entry.text():
                QTimer.singleShot(0, lambda: self.update_status("Please select both source and destination folders.", "warning"))
                QTimer.singleShot(0, self.reset_ui_state)
                return

            source_dir = self.source_entry.text()
            dest_dir = self.dest_entry.text()

            if not os.path.exists(source_dir):
                QTimer.singleShot(0, lambda: self.update_status("Source directory does not exist.", "error"))
                QTimer.singleShot(0, self.reset_ui_state)
                return

            if not os.path.exists(dest_dir):
                try:
                    os.makedirs(dest_dir)
                except Exception as e:
                    QTimer.singleShot(0, lambda: self.update_status(f"Error creating destination directory: {str(e)}", "error"))
                    QTimer.singleShot(0, self.reset_ui_state)
                    return

            # Clear undo stack when starting new organization
            QTimer.singleShot(0, self._clear_undo_stack)

            # Get selected file types
            selected_types = [ft for ft in self.file_categories.keys() if self.check_vars[ft].isChecked()]
            if not selected_types:
                QTimer.singleShot(0, lambda: self.update_status("Please select at least one file type to organize.", "warning"))
                QTimer.singleShot(0, self.reset_ui_state)
                return

            # Create a dictionary to store file movements for undo
            file_movements = {}

            # Get total files for progress calculation
            total_files = sum(1 for f in os.listdir(source_dir) if os.path.isfile(os.path.join(source_dir, f)))
            processed_files = 0

            # Process each file
            for filename in os.listdir(source_dir):
                if not self.is_organizing:  # Check if organization was cancelled
                    break

                if not os.path.isfile(os.path.join(source_dir, filename)):
                    continue

                file_ext = os.path.splitext(filename)[1].lower()
                moved = False

                for category in selected_types:
                    if file_ext in self.file_categories[category]:
                        category_dir = os.path.join(dest_dir, self.custom_folder_names[category])
                        if not os.path.exists(category_dir):
                            os.makedirs(category_dir)

                        source_path = os.path.join(source_dir, filename)
                        dest_path = os.path.join(category_dir, filename)

                        # Store original location for undo
                        file_movements[filename] = {
                            'source': source_path,
                            'destination': dest_path,
                            'category': category
                        }

                        shutil.move(source_path, dest_path)
                        moved = True
                        break

                if not moved:
                    self.unavailable_file_types.add(file_ext)

                processed_files += 1
                progress = int((processed_files / total_files) * 100)
                QTimer.singleShot(0, lambda p=progress: self._update_progress(p))

            # Add the file movements to undo stack if any files were moved
            if file_movements:
                QTimer.singleShot(0, lambda: self._add_to_undo_stack(file_movements))

            if self.is_organizing:  # Only show success if not cancelled
                QTimer.singleShot(0, lambda: self.update_status("Files organized successfully!", "success"))
                if self.unavailable_file_types:
                    QTimer.singleShot(0, self.show_unavailable_types_popup)

        except Exception as e:
            QTimer.singleShot(0, lambda: self.update_status(f"Error organizing files: {str(e)}", "error"))
        finally:
            QTimer.singleShot(0, self.reset_ui_state)

    def _clear_undo_stack(self):
        """Clear the undo stack and disable the undo button."""
        self.undo_stack = []
        self.undo_btn.setEnabled(False)

    def _update_progress(self, value):
        """Update the progress bar value."""
        self.progress_bar.setValue(value)

    def _add_to_undo_stack(self, file_movements):
        """Add file movements to the undo stack and enable the undo button."""
        self.undo_stack.append(file_movements)
        self.undo_btn.setEnabled(True)

    def undo_last_action(self):
        """Undo the last file organization action."""
        if not self.undo_stack:
            self.update_status("Nothing to undo.", "info")
            return

        try:
            # Get the last set of file movements
            last_movements = self.undo_stack.pop()
            
            # Move files back to their original locations
            for filename, movement in last_movements.items():
                if os.path.exists(movement['destination']):
                    shutil.move(movement['destination'], movement['source'])
            
            # Update UI
            self.undo_btn.setEnabled(len(self.undo_stack) > 0)
            self.update_status("Last action undone successfully!", "success")
            
        except Exception as e:
            self.update_status(f"Error undoing last action: {str(e)}", "error")
            # If there was an error, we should clear the undo stack to prevent further issues
            self.undo_stack = []
            self.undo_btn.setEnabled(False)

    def update_status(self, message, level="info", temporary=False):
        """Update status label with colored message."""
        if threading.current_thread() != threading.main_thread():
            QTimer.singleShot(0, lambda: self._update_status_ui(message, level, temporary))
        else:
            self._update_status_ui(message, level, temporary)

    def _update_status_ui(self, message, level="info", temporary=False):
        """Update status UI with appropriate color."""
        color_map = {
            "success": self.current_colors['success'],
            "warning": self.current_colors['warning'],
            "error": self.current_colors['danger'],
            "info": self.current_colors['text_secondary']
        }
        color = color_map.get(level, self.current_colors['text_secondary'])

        self.status_label.setText(message)
        self.status_label.setStyleSheet(f"color: {color};")

        if hasattr(self, '_status_reset_timer') and self._status_reset_timer and self._status_reset_timer.isActive():
            self._status_reset_timer.stop()
        self._status_reset_timer = None

        if temporary:
            self._status_reset_timer = QTimer()
            self._status_reset_timer.setSingleShot(True)
            self._status_reset_timer.timeout.connect(lambda: self._update_status_ui("Ready to organize.", "info"))
            self._status_reset_timer.start(5000)

    def show_unavailable_types_popup(self):
        """Show popup for uncategorized file types."""
        if not self.unavailable_file_types:
            return
            
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Uncategorized File Types")
        msg_box.setIcon(QMessageBox.Icon.Information)
        
        max_display = 20
        sorted_types = sorted(list(self.unavailable_file_types))
        display_text = ", ".join(sorted_types[:max_display])
        if len(sorted_types) > max_display:
            display_text += f", ... and {len(sorted_types) - max_display} more."

        msg_box.setText(f"Some files were skipped because their extensions were not recognized or categorized:\n\n{display_text}")
        msg_box.exec()

    # --- get_current_time, get_greeting, update_time_and_greeting ---
    # --- closeEvent remain functionally the same ---
    def get_current_time(self):
        # Format consistent with original screenshot format
        return datetime.now().strftime("%I:%M:%S %p") # Added seconds for more detail

    def get_greeting(self):
        # Greetings from original Media script
        hour = datetime.now().hour
        if hour < 12:
            return "Good morning, ready to organize your files?" # Kept standard morning
        elif hour < 18:
            return "Good afternoon, let's organize your media."
        else:
            return "Good evening, time to declutter your media."

    def update_time_and_greeting(self):
        # From refactor
        self.time_label.setText(self.get_current_time())
        current_greeting = self.get_greeting()
        if self.greeting_label.text() != current_greeting:
            self.greeting_label.setText(current_greeting)

    def closeEvent(self, event):
        # From refactor (Handles closing during organization)
        if self.is_organizing:
            reply = QMessageBox.question(self, 'Confirm Exit',
                                         "Organization is in progress. Are you sure you want to exit?",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                         QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self.is_organizing = False
                time.sleep(0.1)
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def update_stylesheet(self):
        # Stylesheet structure from refactor, using ORANGE_COLORS
        # No code changes needed here, as it dynamically uses self.current_colors
        sheet = f"""
            QMainWindow, QDialog {{
                background-color: {self.current_colors['background']};
            }}
            QWidget {{
                color: {self.current_colors['text_primary']};
                font-family: '{FONT_FAMILY}';
                background-color: transparent;
            }}
            QLabel {{
                background-color: transparent;
                color: {self.current_colors['text_primary']};
            }}
            QLabel#TimeLabel {{ /* White, default */ }}
            QLabel#GreetingLabel {{ color: {self.current_colors['text_secondary']}; }}
            QLabel#app_title {{ color: {self.current_colors['primary']}; }} /* Primary Orange title */
            QLabel#StatusLabel {{ color: {self.current_colors['text_secondary']}; }}
            QLabel#FooterLabel {{ color: #64748B; }} /* Standard footer color */
            QDialog QLabel {{ padding-top: 2px; }}

            QLineEdit {{
                background-color: {self.current_colors['input_bg']}; /* Use distinct input bg */
                border: 1px solid {self.current_colors['border']};
                border-radius: 5px;
                padding: 8px 10px;
                color: {self.current_colors['text_primary']};
                font-size: 10pt;
            }}
            QLineEdit:focus {{
                border: 1px solid {self.current_colors['primary']}; /* Highlight with primary orange */
            }}

            QPushButton {{
                border-radius: 5px;
                padding: 9px 18px;
                font-size: 10pt;
                font-weight: 500;
                border: none;
                color: {self.current_colors['text_primary']}; /* White text on buttons */
            }}
            QPushButton:hover {{ opacity: 0.85; }}
            QPushButton:disabled {{
                background-color: {self.current_colors['secondary']}; /* Use secondary orange */
                opacity: 0.6;
            }}

            QPushButton#PrimaryButton {{ background-color: {self.current_colors['primary']}; }} /* Primary Orange */
            QPushButton#SecondaryButton {{ background-color: {self.current_colors['secondary']}; }} /* Secondary Orange */
            QPushButton#AccentButton {{ background-color: {self.current_colors['accent']}; }} /* Accent Orange */

            QPushButton#TextButton {{
                 background-color: transparent;
                 color: {self.current_colors['accent']}; /* Use accent orange */
                 font-size: 9pt;
                 font-weight: normal;
                 padding: 4px 8px;
                 text-decoration: underline;
                 opacity: 1.0;
             }}
             QPushButton#TextButton:hover {{
                 color: {self.current_colors['text_primary']}; /* White on hover */
                 text-decoration: underline;
                 opacity: 1.0;
             }}

            QProgressBar {{
                border: none;
                border-radius: 5px;
                background-color: {self.current_colors['progress_bar_bg']}; /* Use orange progress bg */
                height: 10px;
                text-align: center;
                color: transparent;
            }}
            QProgressBar::chunk {{
                background-color: {self.current_colors['progress_bar_chunk']}; /* Use orange chunk color */
                border-radius: 5px;
            }}

            QCheckBox {{
                spacing: 8px;
                font-size: 10pt;
                color: {self.current_colors['text_primary']};
            }}
            QCheckBox::indicator {{
                width: 16px; height: 16px;
                border: 1px solid {self.current_colors['border']};
                border-radius: 3px;
                background-color: {self.current_colors['input_bg']}; /* Match input background */
            }}
            QCheckBox::indicator:hover {{
                border: 1px solid {self.current_colors['primary']}; /* Highlight with primary orange */
            }}
            QCheckBox::indicator:checked {{
                background-color: {self.current_colors['primary']}; /* Use primary orange */
                border: 1px solid {self.current_colors['primary']};
            }}
            QCheckBox::indicator:checked:hover {{ opacity: 0.85; }}

            QScrollArea {{ border: none; background-color: transparent; }}
            QScrollArea > QWidget > QWidget {{ background-color: transparent; }}
            QScrollArea#DialogScrollArea {{ }} /* No specific style needed now */

            QScrollBar:vertical {{
                border: none;
                background: {self.current_colors['secondary_bg']}; /* Use secondary bg */
                width: 10px; margin: 0px; border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: {self.current_colors['primary']}; /* Use primary orange */
                min-height: 25px; border-radius: 5px;
            }}
            QScrollBar::handle:vertical:hover {{ background: {self.current_colors['accent']}; }} /* Use accent orange */
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none; background: none; height: 0px;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{ background: none; }}

            QFrame#divider {{
                 border: none;
                 border-top: 1px solid {self.current_colors['border']};
                 height: 1px; margin: 5px 0px;
             }}

            QMessageBox {{ background-color: {self.current_colors['secondary_bg']}; }}
            QMessageBox QLabel {{ color: {self.current_colors['text_primary']}; font-size: 10pt; }}
            QMessageBox QPushButton {{
                 min-width: 80px;
                 background-color: {self.current_colors['primary']}; /* Primary orange for buttons */
                 color: {self.current_colors['text_primary']};
            }}
            QMessageBox QPushButton:hover {{ opacity: 0.85; }}
        """
        self.setStyleSheet(sheet)


    def update_ui_colors(self):
        # Simplified: Most colors handled by stylesheet + object names
        self.greeting_label.setStyleSheet(f"color: {self.current_colors['text_secondary']};")
        self.status_label.setStyleSheet(f"color: {self.current_colors['text_secondary']};") # Initial status color
        footer = self.findChild(QLabel, "FooterLabel")
        if footer:
            footer.setStyleSheet("color: #64748B;") # Standard footer color
        app_title = self.findChild(QLabel, "app_title")
        if app_title:
             app_title.setStyleSheet(f"color: {self.current_colors['primary']};") # Set title color explicitly

    def show_about_dialog(self):
        about_text = (
            "<h2>Media File Organizer</h2>"
            f"<p>Version 1.0.0 • © {datetime.now().year} JUST ELSON PRODUCTIVE.labs</p>"
            "<p>A specialized tool for organizing your media and creative files.</p>"
            "<p>Features:</p>"
            "<ul>"
            "<li>Media-specific categorization</li>"
            "<li>Support for various media formats</li>"
            "<li>Customizable organization system</li>"
            "</ul>"
            "<p>All rights reserved. Licensed under the application license agreement.</p>"
        )
        
        QMessageBox.about(self, "About Media File Organizer", about_text)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # app.setStyle("Fusion") # Optional: Enforce Fusion style

    # --- Application Icon (Use path from original Media script) ---
    icon_path = "C:/Users/elson/MY CODING PLAY/all the folders for APP DEVELOPMENT CODING/app icons/app_icon(media).ico"
    # It's better practice to use relative paths if possible, but using the provided path:
    # icon_dir = os.path.dirname(__file__)
    # icon_path = os.path.join(icon_dir, "app_icons", "icon_media.png") # Example relative path
    if os.path.exists(icon_path):
        app_icon = QIcon(icon_path)
        app.setWindowIcon(app_icon)
    else:
        print(f"Warning: Application icon not found at {icon_path}")


    # Removed QPalette setting as background is handled by stylesheet
    window = MediaOrganizerApp()
    # Standard window flags (like refactor)
    window.setWindowFlags(Qt.WindowType.Window |
                  Qt.WindowType.CustomizeWindowHint |
                  Qt.WindowType.WindowMinimizeButtonHint |
                  Qt.WindowType.WindowMaximizeButtonHint |
                  Qt.WindowType.WindowCloseButtonHint)
    window.show()
    sys.exit(app.exec())

# --- END OF MODIFIED FILE media_organizer_orange_themed.py ---