import sys
import os
import shutil
from datetime import datetime
import threading
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QPushButton, QLineEdit, QLabel, QProgressBar, QCheckBox, QGridLayout,
                           QDialog, QScrollArea, QFormLayout, QMessageBox, QFileDialog, QSizePolicy,
                           QFrame, QButtonGroup, QRadioButton)
from PyQt6.QtGui import QPainter, QLinearGradient, QColor, QFont, QPalette, QGuiApplication, QIcon, QAction
from PyQt6.QtCore import Qt, QTimer

# --- Constants for Styling ---
# Purple Theme Colors (Ensure good contrast)
PURPLE_COLORS = {
    "background": "#1B2333",       # Consistent deep background
    "secondary_bg": "#1B2333",    # Use the same for all backgrounds
    "primary": "#9C27B0",          # Vibrant purple for primary actions
    "secondary": "#7B1FA2",        # Darker muted purple for secondary actions
    "accent": "#BA68C8",          # Lighter purple for accents (e.g., Browse buttons)
    "text_primary": "#FFFFFF",      # White text for high contrast on dark purple
    "text_secondary": "#E1BEE7",    # Light lavender/purple for secondary text
    "border": "#6A1B9A",          # Border color, related to background
    "input_bg": "#1B2333",          # Input background matches background
    "success": "#66BB6A",          # Green (Material Design Green 400)
    "warning": "#FFA726",          # Orange (Material Design Orange 400)
    "danger": "#EF5350",           # Red (Material Design Red 400)
    "progress_bar_bg": "#7B1FA2", # Background of the progress bar area (matches secondary button)
    "progress_bar_chunk": "#E040FB", # Bright pink/purple chunk (Material Design Purple A100/A200)
}

FONT_FAMILY = "Segoe UI"      # Consistent font

class PersonalOrganizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Let's Arrange Your Personal Files & Folders!")

        # --- Use the single Purple Theme ---
        self.current_colors = PURPLE_COLORS

        # --- File Categories ---
        self.file_categories = {
             "Videos": [".mp4", ".avi", ".mov", ".wmv", ".mkv", ".flv", ".webm", ".m4v", ".mpeg", ".mpg", ".3gp"],
            "Audio": [".wav", ".mp3", ".ogg", ".flac", ".aac", ".m4a", ".aiff", ".wma"],
            "Images": [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".gif", ".webp", ".svg", ".heif", ".heic", ".raw", ".psd", ".ai"],
            "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".tar.gz", ".tar.bz2", ".tar.xz", ".cab", ".iso", ".dmg"],
            "Fonts": [".ttf", ".otf", ".woff", ".woff2"],
            "Scripts & Code": [".jsx", ".py", ".lua", ".xml", ".js", ".html", ".css", ".java", ".cpp", ".c", ".cs", ".sh", ".bat"],
            "Documents": [".doc", ".docx", ".pdf", ".txt", ".rtf", ".odt", ".xls", ".xlsx", ".ppt", ".pptx", ".csv", ".md"],
            "Ebooks": [".epub", ".mobi", ".azw", ".azw3"],
            "Executables & Installers": [".exe", ".msi", ".dmg", ".pkg", ".deb", ".rpm", ".app"],
            "Logs & Data": [".log", ".csv", ".json", ".yaml", ".yml", ".xml"],
            "Configuration": [".ini", ".cfg", ".conf", ".plist"],
            "Other": []
        }
        
        # Folder categories based on common naming patterns
        self.folder_categories = {
            "Project Folders": ["project", "projects", "work", "workspace", "development", "dev", "code"],
            "Media Folders": ["videos", "movies", "music", "audio", "photos", "pictures", "images", "media"],
            "Document Folders": ["documents", "docs", "papers", "reports", "files"],
            "Download Folders": ["downloads", "download", "temp", "temporary"],
            "Archive Folders": ["archive", "archives", "backup", "backups", "old"],
            "System Folders": ["system", "config", "configuration", "settings", "program files", "applications"],
            "Personal Folders": ["personal", "private", "my", "desktop", "home"],
            "Other Folders": []
        }

        self.file_categories = dict(sorted(self.file_categories.items()))
        self.folder_categories = dict(sorted(self.folder_categories.items()))
        
        self.custom_folder_names = {k: k for k in self.file_categories.keys()}
        self.custom_folder_names.update({k: k for k in self.folder_categories.keys()})

        # --- Enhanced State ---
        self.unavailable_file_types = set()
        self.uncategorized_folders = set()
        self.is_organizing = False
        self.undo_stack = []
        self.organize_mode = "both"  # "files", "folders", or "both"

        # --- Window Size ---
        screen = QGuiApplication.primaryScreen().availableGeometry()
        max_width, max_height = screen.width(), screen.height()
        self.setGeometry(100, 100, min(1000, max_width - 100), min(750, max_height - 100))
        self.setMinimumSize(700, 600)
        self.setMaximumSize(max_width, max_height)

        self.setup_ui()
        self.update_stylesheet()

    def setup_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(18)

        # --- Header ---
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

        self.greeting_label = QLabel(self.get_greeting())
        self.greeting_label.setObjectName("GreetingLabel")
        self.greeting_label.setFont(QFont(FONT_FAMILY, 12))
        time_greeting_layout.addWidget(self.greeting_label)

        header_layout.addWidget(time_greeting_widget)
        header_layout.addStretch(1)

        # App title
        app_title = QLabel("Personal File & Folder Organizer")
        app_title.setObjectName("app_title")
        app_title.setFont(QFont(FONT_FAMILY, 20, QFont.Weight.Bold))
        header_layout.addWidget(app_title)

        main_layout.addWidget(header_widget)

        # --- Divider ---
        divider1 = QFrame()
        divider1.setObjectName("divider")
        divider1.setFrameShape(QFrame.Shape.HLine)
        divider1.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(divider1)

        # --- Input Section ---
        input_section_widget = QWidget()
        input_section_layout = QVBoxLayout(input_section_widget)
        input_section_layout.setContentsMargins(0, 0, 0, 0)
        input_section_layout.setSpacing(12)

        # Source Directory
        source_widget = QWidget()
        source_layout = QHBoxLayout(source_widget)
        source_layout.setContentsMargins(0, 0, 0, 0)
        source_layout.setSpacing(10)
        source_label = QLabel("Source Folder:")
        source_label.setFont(QFont(FONT_FAMILY, 10, QFont.Weight.Bold))
        source_layout.addWidget(source_label)
        self.source_entry = QLineEdit()
        self.source_entry.setPlaceholderText("Where are the files and folders you want to organize?")
        source_layout.addWidget(self.source_entry)
        source_btn = QPushButton("Browse")
        source_btn.setObjectName("AccentButton")
        source_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        source_btn.clicked.connect(self.browse_source)
        source_layout.addWidget(source_btn)
        input_section_layout.addWidget(source_widget)

        # Destination Directory
        dest_widget = QWidget()
        dest_layout = QHBoxLayout(dest_widget)
        dest_layout.setContentsMargins(0, 0, 0, 0)
        dest_layout.setSpacing(10)
        dest_label = QLabel("Destination Folder:")
        dest_label.setFont(QFont(FONT_FAMILY, 10, QFont.Weight.Bold))
        dest_layout.addWidget(dest_label)
        self.dest_entry = QLineEdit()
        self.dest_entry.setPlaceholderText("Where do you want to save the organized files and folders?")
        dest_layout.addWidget(self.dest_entry)
        dest_btn = QPushButton("Browse")
        dest_btn.setObjectName("AccentButton")
        dest_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        dest_btn.clicked.connect(self.browse_destination)
        dest_layout.addWidget(dest_btn)
        input_section_layout.addWidget(dest_widget)
        main_layout.addWidget(input_section_widget)

        # --- Organization Mode Selection ---
        mode_widget = QWidget()
        mode_layout = QVBoxLayout(mode_widget)
        mode_layout.setContentsMargins(5, 10, 5, 10)
        mode_layout.setSpacing(8)
        
        mode_label = QLabel("What would you like to organize?")
        mode_label.setFont(QFont(FONT_FAMILY, 10, QFont.Weight.Bold))
        mode_layout.addWidget(mode_label)
        
        mode_radio_layout = QHBoxLayout()
        self.mode_group = QButtonGroup()
        
        self.files_radio = QRadioButton("Files Only")
        self.folders_radio = QRadioButton("Folders Only")
        self.both_radio = QRadioButton("Files and Folders")
        self.both_radio.setChecked(True)  # Default selection
        
        self.mode_group.addButton(self.files_radio, 0)
        self.mode_group.addButton(self.folders_radio, 1)
        self.mode_group.addButton(self.both_radio, 2)
        
        mode_radio_layout.addWidget(self.files_radio)
        mode_radio_layout.addWidget(self.folders_radio)
        mode_radio_layout.addWidget(self.both_radio)
        mode_radio_layout.addStretch()
        
        mode_layout.addLayout(mode_radio_layout)
        main_layout.addWidget(mode_widget)

        # --- File Type Selection ---
        self.file_type_widget = QWidget()
        file_type_layout = QVBoxLayout(self.file_type_widget)
        file_type_layout.setContentsMargins(5, 10, 5, 10)
        file_type_layout.setSpacing(8)
        
        file_type_header_layout = QHBoxLayout()
        self.file_type_label = QLabel("Organize Files by Type:")
        self.file_type_label.setFont(QFont(FONT_FAMILY, 10, QFont.Weight.Bold))
        file_type_header_layout.addWidget(self.file_type_label)
        file_type_header_layout.addStretch()
        
        self.file_select_all_btn = QPushButton("Select All")
        self.file_select_all_btn.setObjectName("TextButton")
        self.file_select_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.file_select_all_btn.clicked.connect(lambda: self.toggle_file_checkboxes(True))
        file_type_header_layout.addWidget(self.file_select_all_btn)
        
        self.file_deselect_all_btn = QPushButton("Deselect All")
        self.file_deselect_all_btn.setObjectName("TextButton")
        self.file_deselect_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.file_deselect_all_btn.clicked.connect(lambda: self.toggle_file_checkboxes(False))
        file_type_header_layout.addWidget(self.file_deselect_all_btn)
        
        file_type_layout.addLayout(file_type_header_layout)

        file_checkbox_scroll = QScrollArea()
        file_checkbox_scroll.setObjectName("CheckboxScrollArea")
        file_checkbox_scroll.setWidgetResizable(True)
        file_checkbox_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        file_checkbox_scroll.setMaximumHeight(150)
        
        self.file_types = list(self.file_categories.keys())
        self.file_check_vars = {}
        file_checkbox_widget = QWidget()
        file_checkbox_widget.setObjectName("CheckboxWidget")
        file_checkbox_layout = QGridLayout(file_checkbox_widget)
        file_checkbox_layout.setContentsMargins(5, 5, 15, 5)
        file_checkbox_layout.setSpacing(10)
        file_checkbox_layout.setHorizontalSpacing(20)
        
        num_cols = 4
        for i, file_type in enumerate(self.file_types):
            checkbox = QCheckBox(file_type)
            checkbox.setChecked(True)
            self.file_check_vars[file_type] = checkbox
            file_checkbox_layout.addWidget(checkbox, i // num_cols, i % num_cols)
        
        file_checkbox_scroll.setWidget(file_checkbox_widget)
        file_type_layout.addWidget(file_checkbox_scroll)
        main_layout.addWidget(self.file_type_widget)

        # --- Folder Type Selection ---
        self.folder_type_widget = QWidget()
        folder_type_layout = QVBoxLayout(self.folder_type_widget)
        folder_type_layout.setContentsMargins(5, 10, 5, 10)
        folder_type_layout.setSpacing(8)
        
        folder_type_header_layout = QHBoxLayout()
        self.folder_type_label = QLabel("Organize Folders by Type:")
        self.folder_type_label.setFont(QFont(FONT_FAMILY, 10, QFont.Weight.Bold))
        folder_type_header_layout.addWidget(self.folder_type_label)
        folder_type_header_layout.addStretch()
        
        self.folder_select_all_btn = QPushButton("Select All")
        self.folder_select_all_btn.setObjectName("TextButton")
        self.folder_select_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.folder_select_all_btn.clicked.connect(lambda: self.toggle_folder_checkboxes(True))
        folder_type_header_layout.addWidget(self.folder_select_all_btn)
        
        self.folder_deselect_all_btn = QPushButton("Deselect All")
        self.folder_deselect_all_btn.setObjectName("TextButton")
        self.folder_deselect_all_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.folder_deselect_all_btn.clicked.connect(lambda: self.toggle_folder_checkboxes(False))
        folder_type_header_layout.addWidget(self.folder_deselect_all_btn)
        
        folder_type_layout.addLayout(folder_type_header_layout)

        folder_checkbox_scroll = QScrollArea()
        folder_checkbox_scroll.setObjectName("CheckboxScrollArea")
        folder_checkbox_scroll.setWidgetResizable(True)
        folder_checkbox_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        folder_checkbox_scroll.setMaximumHeight(120)
        
        self.folder_types = list(self.folder_categories.keys())
        self.folder_check_vars = {}
        folder_checkbox_widget = QWidget()
        folder_checkbox_widget.setObjectName("CheckboxWidget")
        folder_checkbox_layout = QGridLayout(folder_checkbox_widget)
        folder_checkbox_layout.setContentsMargins(5, 5, 15, 5)
        folder_checkbox_layout.setSpacing(10)
        folder_checkbox_layout.setHorizontalSpacing(20)
        
        for i, folder_type in enumerate(self.folder_types):
            checkbox = QCheckBox(folder_type)
            checkbox.setChecked(True)
            self.folder_check_vars[folder_type] = checkbox
            folder_checkbox_layout.addWidget(checkbox, i // num_cols, i % num_cols)
        
        folder_checkbox_scroll.setWidget(folder_checkbox_widget)
        folder_type_layout.addWidget(folder_checkbox_scroll)
        main_layout.addWidget(self.folder_type_widget)

        # Connect radio button signals to update UI
        self.files_radio.toggled.connect(self.update_ui_for_mode)
        self.folders_radio.toggled.connect(self.update_ui_for_mode)
        self.both_radio.toggled.connect(self.update_ui_for_mode)

        # --- Progress and Status ---
        progress_widget = QWidget()
        progress_layout = QVBoxLayout(progress_widget)
        progress_layout.setContentsMargins(0, 5, 0, 5)
        progress_layout.setSpacing(5)
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        progress_layout.addWidget(self.progress_bar)
        self.status_label = QLabel("Ready to organize.")
        self.status_label.setObjectName("StatusLabel")
        self.status_label.setFont(QFont(FONT_FAMILY, 10))
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        progress_layout.addWidget(self.status_label)
        main_layout.addWidget(progress_widget)

        main_layout.addStretch(1)

        # --- Divider ---
        divider2 = QFrame()
        divider2.setObjectName("divider")
        divider2.setFrameShape(QFrame.Shape.HLine)
        divider2.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(divider2)

        # --- Action Buttons ---
        action_button_widget = QWidget()
        action_button_layout = QHBoxLayout(action_button_widget)
        action_button_layout.setContentsMargins(0, 5, 0, 0)
        action_button_layout.setSpacing(10)
        
        # Add Undo button
        self.undo_btn = QPushButton("Undo Last Action")
        self.undo_btn.setObjectName("SecondaryButton")
        self.undo_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.undo_btn.clicked.connect(self.undo_last_action)
        self.undo_btn.setEnabled(False)
        action_button_layout.addWidget(self.undo_btn)
        
        self.custom_folder_btn = QPushButton("Customize Folder Names")
        self.custom_folder_btn.setObjectName("SecondaryButton")
        self.custom_folder_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.custom_folder_btn.clicked.connect(self.open_custom_style_dialog)
        action_button_layout.addWidget(self.custom_folder_btn)
        
        # Add About button
        about_btn = QPushButton("About")
        about_btn.setObjectName("SecondaryButton")
        about_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        about_btn.clicked.connect(self.show_about_dialog)
        action_button_layout.addWidget(about_btn)
        
        action_button_layout.addStretch(1)
        self.organize_btn = QPushButton("Start Organizing")
        self.organize_btn.setObjectName("PrimaryButton")
        self.organize_btn.setFont(QFont(FONT_FAMILY, 11, QFont.Weight.Bold))
        self.organize_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.organize_btn.clicked.connect(self.start_organizing)
        action_button_layout.addWidget(self.organize_btn)
        main_layout.addWidget(action_button_widget)

        # --- Timer for Time/Greeting Update ---
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_time_and_greeting)
        self.update_timer.start(1000)

        # --- Apply initial colors ---
        self.update_ui_colors()

        # --- Footer ---
        footer = QLabel(f"© {datetime.now().year} Personal File & Folder Organizer")
        footer.setFont(QFont(FONT_FAMILY, 9))
        footer.setObjectName("FooterLabel")
        footer.setAlignment(Qt.AlignmentFlag.AlignRight)
        main_layout.addWidget(footer)

        # Initialize UI state
        self.update_ui_for_mode()

    def update_ui_for_mode(self):
        """Update UI visibility based on selected organization mode."""
        if self.files_radio.isChecked():
            self.organize_mode = "files"
            self.file_type_widget.setVisible(True)
            self.folder_type_widget.setVisible(False)
        elif self.folders_radio.isChecked():
            self.organize_mode = "folders"
            self.file_type_widget.setVisible(False)
            self.folder_type_widget.setVisible(True)
        else:  # both_radio.isChecked()
            self.organize_mode = "both"
            self.file_type_widget.setVisible(True)
            self.folder_type_widget.setVisible(True)

    def toggle_file_checkboxes(self, state):
        for checkbox in self.file_check_vars.values():
            checkbox.setChecked(state)

    def toggle_folder_checkboxes(self, state):
        for checkbox in self.folder_check_vars.values():
            checkbox.setChecked(state)

    def browse_source(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Source Folder")
        if folder:
            self.source_entry.setText(folder)

    def browse_destination(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder")
        if folder:
            self.dest_entry.setText(folder)

    def categorize_folder(self, folder_name):
        """Categorize folder based on name patterns."""
        folder_lower = folder_name.lower()
        for category, keywords in self.folder_categories.items():
            if category == "Other Folders":
                continue
            for keyword in keywords:
                if keyword in folder_lower:
                    return category
        return "Other Folders"

    def organize_files(self):
        """Organize files and/or folders in the background thread."""
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

            # Get selected types based on mode
            organize_files = self.organize_mode in ["files", "both"]
            organize_folders = self.organize_mode in ["folders", "both"]

            selected_file_types = []
            selected_folder_types = []

            if organize_files:
                selected_file_types = [ft for ft in self.file_categories.keys() if self.file_check_vars[ft].isChecked()]
            
            if organize_folders:
                selected_folder_types = [ft for ft in self.folder_categories.keys() if self.folder_check_vars[ft].isChecked()]

            if not selected_file_types and not selected_folder_types:
                QTimer.singleShot(0, lambda: self.update_status("Please select at least one type to organize.", "warning"))
                QTimer.singleShot(0, self.reset_ui_state)
                return

            # Create a dictionary to store movements for undo
            file_movements = {}

            # Get total items for progress calculation
            items = os.listdir(source_dir)
            total_items = len(items)
            processed_items = 0

            # Process each item
            for item_name in items:
                if not self.is_organizing:  # Check if organization was cancelled
                     break

                item_path = os.path.join(source_dir, item_name)
                
                if os.path.isfile(item_path) and organize_files:
                    # Process file
                    file_ext = os.path.splitext(item_name)[1].lower()
                    moved = False

                    for category in selected_file_types:
                        if file_ext in self.file_categories[category]:
                            category_dir = os.path.join(dest_dir, self.custom_folder_names[category])
                            if not os.path.exists(category_dir):
                                os.makedirs(category_dir)

                            dest_path = os.path.join(category_dir, item_name)
                            file_movements[item_name] = {
                                'source': item_path,
                                'destination': dest_path,
                                'category': category,
                                'type': 'file'
                            }

                            shutil.move(item_path, dest_path)
                            moved = True
                            break

                    if not moved:
                        self.unavailable_file_types.add(file_ext)

                elif os.path.isdir(item_path) and organize_folders:
                    # Process folder
                    folder_category = self.categorize_folder(item_name)
                    
                    if folder_category in selected_folder_types:
                        category_dir = os.path.join(dest_dir, self.custom_folder_names[folder_category])
                        if not os.path.exists(category_dir):
                            os.makedirs(category_dir)

                        dest_path = os.path.join(category_dir, item_name)
                        file_movements[item_name] = {
                            'source': item_path,
                            'destination': dest_path,
                            'category': folder_category,
                            'type': 'folder'
                        }

                        shutil.move(item_path, dest_path)
                else:
                        self.uncategorized_folders.add(item_name)

                processed_items += 1
                progress = int((processed_items / total_items) * 100)
                QTimer.singleShot(0, lambda p=progress: self._update_progress(p))

            # Add the movements to undo stack if any items were moved
            if file_movements:
                QTimer.singleShot(0, lambda: self._add_to_undo_stack(file_movements))

            if self.is_organizing:  # Only show success if not cancelled
                files_organized = sum(1 for m in file_movements.values() if m['type'] == 'file')
                folders_organized = sum(1 for m in file_movements.values() if m['type'] == 'folder')
                
                success_msg = f"Organization complete! "
                if files_organized > 0:
                    success_msg += f"{files_organized} file(s) "
                if folders_organized > 0:
                    success_msg += f"{folders_organized} folder(s) "
                success_msg += "organized successfully!"
                
                QTimer.singleShot(0, lambda: self.update_status(success_msg, "success"))
                
                if self.unavailable_file_types or self.uncategorized_folders:
                    QTimer.singleShot(0, self.show_uncategorized_popup)

        except Exception as e:
            QTimer.singleShot(0, lambda: self.update_status(f"Error organizing items: {str(e)}", "error"))
        finally:
            QTimer.singleShot(0, self.reset_ui_state)

    def show_uncategorized_popup(self):
        """Show popup for uncategorized files and folders."""
        msg = QMessageBox(self)
        msg.setWindowTitle("Uncategorized Items Found")
        msg.setIcon(QMessageBox.Icon.Information)
        
        message_text = "Some items were not categorized:\n\n"
        
        if self.unavailable_file_types:
            message_text += f"Uncategorized file extensions: {', '.join(sorted(self.unavailable_file_types))}\n\n"
        
        if self.uncategorized_folders:
            folder_list = ', '.join(sorted(self.uncategorized_folders))
            if len(folder_list) > 100:
                folder_list = folder_list[:100] + "..."
            message_text += f"Uncategorized folders: {folder_list}\n\n"
        
        message_text += "These items remain in the source directory."
        msg.setText(message_text)
        msg.exec()
        
        # Clear the sets after showing
        self.unavailable_file_types.clear()
        self.uncategorized_folders.clear()

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

    def _update_progress(self, value):
        """Update progress bar (called from thread)."""
        self.progress_bar.setValue(value)

    def _add_to_undo_stack(self, movements):
        """Add movements to undo stack (called from thread)."""
        self.undo_stack.append(movements)
        if len(self.undo_stack) > 10:  # Keep only last 10 operations
            self.undo_stack.pop(0)
        self.undo_btn.setEnabled(True)

    def _clear_undo_stack(self):
        """Clear the undo stack (called from thread)."""
        self.undo_stack.clear()
        self.undo_btn.setEnabled(False)

    def undo_last_action(self):
        """Undo the last organization action."""
        if not self.undo_stack:
            QMessageBox.information(self, "Undo", "No actions to undo.")
            return
        
        last_movements = self.undo_stack.pop()
        
        try:
            for item_name, movement_info in last_movements.items():
                source_path = movement_info['source']
                dest_path = movement_info['destination']
                
                if os.path.exists(dest_path):
                    # Move back to original location
                    shutil.move(dest_path, source_path)
            
            self.update_status(f"Undone: {len(last_movements)} items restored to original location.", "success")
            
            if not self.undo_stack:
                self.undo_btn.setEnabled(False)
                
        except Exception as e:
            QMessageBox.critical(self, "Undo Error", f"Error undoing action: {str(e)}")

    def update_status(self, message, status_type="info"):
        """Update status label with colored message."""
        self.status_label.setText(message)
        if status_type == "success":
            self.status_label.setStyleSheet(f"color: {self.current_colors['success']};")
        elif status_type == "warning":
            self.status_label.setStyleSheet(f"color: {self.current_colors['warning']};")
        elif status_type == "error":
            self.status_label.setStyleSheet(f"color: {self.current_colors['danger']};")
        else:
            self.status_label.setStyleSheet(f"color: {self.current_colors['text_primary']};")

    def open_custom_style_dialog(self):
        """Open dialog to customize folder names."""
        dialog = CustomFolderDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.custom_folder_names = dialog.get_custom_names()

    def show_about_dialog(self):
        """Show about dialog."""
        QMessageBox.about(self, "About Personal File & Folder Organizer",
                         "Personal File & Folder Organizer v2.0\n\n"
                         "A powerful tool to organize your files and folders automatically.\n\n"
                         "Features:\n"
                         "• Organize files by type (Videos, Images, Documents, etc.)\n"
                         "• Organize folders by naming patterns\n"
                         "• Customizable folder names\n"
                         "• Undo functionality\n"
                         "• Modern purple-themed interface\n\n"
                         "Created with PyQt6 and Python")

    def get_current_time(self):
        """Get current time formatted."""
        return datetime.now().strftime("%H:%M:%S")

    def get_greeting(self):
        """Get greeting based on current time."""
        hour = datetime.now().hour
        if 5 <= hour < 12:
            return "Good Morning! Ready to organize?"
        elif 12 <= hour < 17:
            return "Good Afternoon! Let's get organized!"
        elif 17 <= hour < 21:
            return "Good Evening! Time to tidy up!"
        else:
            return "Working late? Let's organize!"

    def update_time_and_greeting(self):
        """Update time and greeting labels."""
        self.time_label.setText(self.get_current_time())
        self.greeting_label.setText(self.get_greeting())

    def update_ui_colors(self):
        """Update UI colors based on current theme."""
        self.update_stylesheet()

    def update_stylesheet(self):
        """Apply comprehensive stylesheet to the application."""
        colors = self.current_colors
        
        stylesheet = f"""
        /* Main Window */
        QMainWindow {{
            background-color: {colors['background']};
            color: {colors['text_primary']};
            font-family: '{FONT_FAMILY}';
        }}
        
        /* Central Widget */
            QWidget {{
            background-color: {colors['background']};
            color: {colors['text_primary']};
                font-family: '{FONT_FAMILY}';
            }}
        
        /* Labels */
            QLabel {{
            color: {colors['text_primary']};
                background-color: transparent;
        }}
        
        QLabel#TimeLabel {{
            color: {colors['primary']};
            font-weight: bold;
        }}
        
        QLabel#GreetingLabel {{
            color: {colors['text_secondary']};
        }}
        
        QLabel#app_title {{
            color: {colors['text_primary']};
            font-weight: bold;
        }}
        
        QLabel#StatusLabel {{
            color: {colors['text_primary']};
            padding: 5px;
        }}
        
        QLabel#FooterLabel {{
            color: {colors['text_secondary']};
        }}
        
        /* Line Edits */
            QLineEdit {{
            background-color: {colors['input_bg']};
            border: 2px solid {colors['border']};
            border-radius: 8px;
            padding: 8px 12px;
            color: {colors['text_primary']};
            font-size: 11px;
        }}
        
            QLineEdit:focus {{
            border-color: {colors['primary']};
            background-color: {colors['secondary_bg']};
            }}

        QLineEdit::placeholder {{
            color: {colors['text_secondary']};
        }}
        
        /* Buttons */
            QPushButton {{
                border: none;
            border-radius: 8px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 11px;
            min-height: 20px;
        }}
        
        QPushButton#PrimaryButton {{
            background-color: {colors['primary']};
            color: {colors['text_primary']};
        }}
        
        QPushButton#PrimaryButton:hover {{
            background-color: {colors['accent']};
        }}
        
        QPushButton#PrimaryButton:pressed {{
            background-color: {colors['secondary']};
        }}
        
        QPushButton#SecondaryButton {{
            background-color: {colors['secondary']};
            color: {colors['text_primary']};
        }}
        
        QPushButton#SecondaryButton:hover {{
            background-color: {colors['primary']};
        }}
        
        QPushButton#SecondaryButton:pressed {{
            background-color: {colors['border']};
        }}
        
        QPushButton#AccentButton {{
            background-color: {colors['accent']};
            color: {colors['text_primary']};
        }}
        
        QPushButton#AccentButton:hover {{
            background-color: {colors['primary']};
        }}
        
        QPushButton#AccentButton:pressed {{
            background-color: {colors['secondary']};
        }}

            QPushButton#TextButton {{
                 background-color: transparent;
            color: {colors['accent']};
                 text-decoration: underline;
            padding: 5px 10px;
             }}
        
             QPushButton#TextButton:hover {{
            color: {colors['primary']};
        }}
        
        QPushButton#DangerButton {{
            background-color: {colors['danger']};
            color: {colors['text_primary']};
        }}
        
        QPushButton#DangerButton:hover {{
            background-color: #D32F2F;
        }}
        
        QPushButton:disabled {{
            background-color: {colors['border']};
            color: {colors['text_secondary']};
        }}
        
        /* Checkboxes */
            QCheckBox {{
            color: {colors['text_primary']};
                spacing: 8px;
            font-size: 11px;
            }}
        
            QCheckBox::indicator {{
            width: 18px;
            height: 18px;
                border-radius: 3px;
            border: 2px solid {colors['border']};
            }}
        
        QCheckBox::indicator:unchecked {{
            background-color: {colors['input_bg']};
            }}
        
            QCheckBox::indicator:checked {{
            background-color: {colors['primary']};
            border-color: {colors['primary']};
        }}
        
        QCheckBox::indicator:hover {{
            border-color: {colors['accent']};
        }}
        
        /* Radio Buttons */
        QRadioButton {{
            color: {colors['text_primary']};
            spacing: 8px;
            font-size: 11px;
        }}
        
        QRadioButton::indicator {{
            width: 18px;
            height: 18px;
            border-radius: 9px;
            border: 2px solid {colors['border']};
        }}
        
        QRadioButton::indicator:unchecked {{
            background-color: {colors['input_bg']};
        }}
        
        QRadioButton::indicator:checked {{
            background-color: {colors['primary']};
            border-color: {colors['primary']};
        }}
        
        QRadioButton::indicator:hover {{
            border-color: {colors['accent']};
        }}
        
        /* Progress Bar */
        QProgressBar {{
            border: 2px solid {colors['border']};
            border-radius: 8px;
            background-color: {colors['progress_bar_bg']};
            text-align: center;
            height: 25px;
        }}
        
        QProgressBar::chunk {{
            background-color: {colors['progress_bar_chunk']};
            border-radius: 6px;
        }}
        
        /* Scroll Areas */
        QScrollArea {{
            border: 1px solid {colors['border']};
            border-radius: 8px;
            background-color: {colors['secondary_bg']};
        }}
        
        QScrollArea#CheckboxScrollArea {{
            background-color: transparent;
            border: 1px solid {colors['border']};
        }}
        
        QWidget#CheckboxWidget {{
            background-color: transparent;
        }}
        
        /* Scroll Bars */
            QScrollBar:vertical {{
            background-color: {colors['secondary_bg']};
            width: 12px;
            border-radius: 6px;
        }}
        
            QScrollBar::handle:vertical {{
            background-color: {colors['accent']};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {colors['primary']};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        /* Frames and Dividers */
            QFrame#divider {{
            color: {colors['border']};
            background-color: {colors['border']};
        }}
        
        /* Message Boxes */
        QMessageBox {{
            background-color: {colors['background']};
            color: {colors['text_primary']};
        }}
        
            QMessageBox QPushButton {{
            background-color: {colors['primary']};
            color: {colors['text_primary']};
            border: none;
            border-radius: 6px;
            padding: 8px 16px;
                 min-width: 80px;
        }}
        
        QMessageBox QPushButton:hover {{
            background-color: {colors['accent']};
        }}
        """
        
        self.setStyleSheet(stylesheet)


class CustomFolderDialog(QDialog):
    """Dialog for customizing folder names."""
    
    def __init__(self, parent):
        super().__init__(parent)
        self.parent_app = parent
        self.setWindowTitle("Customize Folder Names")
        self.setModal(True)
        self.resize(600, 500)
        
        # Copy current custom names
        self.custom_names = self.parent_app.custom_folder_names.copy()
        
        self.setup_ui()
        self.setStyleSheet(parent.styleSheet())  # Apply parent's stylesheet

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("Customize Folder Names")
        header.setFont(QFont(FONT_FAMILY, 16, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        description = QLabel("Edit the names of the folders that will be created for each category:")
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(description)
        
        # Scroll area for form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setContentsMargins(10, 10, 10, 10)
        form_layout.setSpacing(12)
        
        self.name_entries = {}
        
        # Add file categories
        file_label = QLabel("File Categories:")
        file_label.setFont(QFont(FONT_FAMILY, 12, QFont.Weight.Bold))
        form_layout.addRow(file_label)
        
        for category in sorted(self.parent_app.file_categories.keys()):
            entry = QLineEdit(self.custom_names[category])
            entry.setPlaceholderText(f"Folder name for {category}")
            self.name_entries[category] = entry
            form_layout.addRow(f"{category}:", entry)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        form_layout.addRow(separator)
        
        # Add folder categories
        folder_label = QLabel("Folder Categories:")
        folder_label.setFont(QFont(FONT_FAMILY, 12, QFont.Weight.Bold))
        form_layout.addRow(folder_label)
        
        for category in sorted(self.parent_app.folder_categories.keys()):
            entry = QLineEdit(self.custom_names[category])
            entry.setPlaceholderText(f"Folder name for {category}")
            self.name_entries[category] = entry
            form_layout.addRow(f"{category}:", entry)
        
        scroll.setWidget(form_widget)
        layout.addWidget(scroll)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        reset_btn = QPushButton("Reset to Defaults")
        reset_btn.setObjectName("SecondaryButton")
        reset_btn.clicked.connect(self.reset_to_defaults)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setObjectName("SecondaryButton")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save Changes")
        save_btn.setObjectName("PrimaryButton")
        save_btn.clicked.connect(self.accept)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)

    def reset_to_defaults(self):
        """Reset all folder names to defaults."""
        for category, entry in self.name_entries.items():
            entry.setText(category)

    def get_custom_names(self):
        """Get the custom names from the form."""
        custom_names = {}
        for category, entry in self.name_entries.items():
            name = entry.text().strip()
            custom_names[category] = name if name else category
        return custom_names


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Personal File & Folder Organizer")
    app.setApplicationVersion("2.0")
    
    # Set application icon if available
    try:
        app.setWindowIcon(QIcon("icon.png"))
    except:
        pass

    window = PersonalOrganizerApp()
    window.show()
    window.setWindowFlags(Qt.WindowType.Window |
                  Qt.WindowType.CustomizeWindowHint |
                  Qt.WindowType.WindowMinimizeButtonHint | 
                  Qt.WindowType.WindowMaximizeButtonHint | 
                  Qt.WindowType.WindowCloseButtonHint)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()