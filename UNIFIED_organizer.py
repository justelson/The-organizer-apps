import sys
import os
import shutil
from datetime import datetime
import threading
import time
import tkinter as tk
from tkinter import ttk
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QLineEdit, QLabel, QProgressBar, QCheckBox, QGridLayout,
                             QDialog, QScrollArea, QFormLayout, QMessageBox, QFileDialog, QSizePolicy,
                             QTabWidget, QFrame)
from PyQt6.QtGui import QPainter, QLinearGradient, QColor, QFont, QPalette, QGuiApplication, QIcon
from PyQt6.QtCore import Qt, QTimer

class UnifiedOrganizerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Unified File Organizer")

        # Get available screen size
        screen = QGuiApplication.primaryScreen().availableGeometry()
        max_width, max_height = screen.width(), screen.height()


        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook.Tab', padding=[20, 10], font=('Segoe UI', 10, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', '#ffffff')], foreground=[('selected', '#000000')])


        # Set reasonable default size
        self.setGeometry(100, 100, min(1000, max_width), min(650, max_height))
        self.setMinimumSize(800, 500)
        self.setMaximumSize(max_width, max_height)

        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E293B;
            }
            QTabWidget::pane {
                border: none;
                background-color: #1E293B;
            }
            QTabBar::tab {
                background-color: #334155;
                color: #E2E8F0;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                margin: 2px;
            }
            QTabBar::tab:selected {
                background-color: #3B82F6;
                color: white;
            }
            QTabBar::tab:hover:!selected {
                background-color: #475569;
            }
        """)

        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #2D3748;
                background: #1E293B;
                border-radius: 4px;
            }
            QTabBar::tab {
                background: #2D3748;
                color: #CBD5E1;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background: #3B82F6;
                color: white;
            }
            QTabBar::tab:hover {
                background: #4B5563;
            }
        """)

        # Create and add tabs
        from PersonalOrganizerBuild.PERSONAL_organizer import PersonalOrganizerApp
        from FILE_ORGANIZER_OFFICE_SUITE.OFFICE_organizer import OfficeFileOrganizerApp
        from FILE_ORGANIZER_CREATORS_SUITE.media_organizer import MediaOrganizerApp

        personal_tab = PersonalOrganizerApp()
        office_tab = OfficeFileOrganizerApp()
        media_tab = MediaOrganizerApp()

        # Remove window decorations from tab widgets
        for tab in [personal_tab, office_tab, media_tab]:
            tab.setWindowFlags(Qt.WindowType.Widget)

        self.tab_widget.addTab(personal_tab, QIcon("app_icons/icon_personal.png"), "Personal")
        self.tab_widget.addTab(office_tab, QIcon("app_icons/icon_office.png"), "Office")
        self.tab_widget.addTab(media_tab, QIcon("app_icons/icon-creators.png"), "Media")
        
        # Add Help tab
        help_tab = self.create_help_tab()
        self.tab_widget.addTab(help_tab, QIcon("app_icons/icon_help.png"), "Help")

        main_layout.addWidget(self.tab_widget)

        # Timer for updating time
        self.update_timer = QTimer(self)
        self.update_timer.timeout.connect(self.update_time)
        self.update_timer.start(1000)

    def create_help_tab(self):
        help_widget = QWidget()
        help_layout = QVBoxLayout(help_widget)
        help_layout.setContentsMargins(0, 0, 0, 0)
        help_layout.setSpacing(0)
        
        # Create a scroll area for all content
        main_scroll_area = QScrollArea()
        main_scroll_area.setWidgetResizable(True)
        main_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        main_scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background: #1E293B;
                width: 10px; 
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #3B82F6;
                min-height: 25px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
                height: 0px;
            }
        """)
        
        # Create content widget for the scrollable area
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setContentsMargins(25, 20, 25, 20)
        scroll_layout.setSpacing(20)
        
        # Title and intro
        title = QLabel("Unified File Organizer - Help")
        title.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: #3B82F6;") # Blue title
        scroll_layout.addWidget(title)
        
        intro = QLabel("Welcome to the Unified File Organizer! This application combines three powerful organizing tools into one suite.")
        intro.setFont(QFont("Segoe UI", 11))
        intro.setWordWrap(True)
        scroll_layout.addWidget(intro)
        
        # Divider
        divider1 = QFrame()
        divider1.setFrameShape(QFrame.Shape.HLine)
        divider1.setFrameShadow(QFrame.Shadow.Sunken)
        divider1.setStyleSheet("background-color: #334155;")
        scroll_layout.addWidget(divider1)
        
        # About section
        about_title = QLabel("About the Suite")
        about_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        scroll_layout.addWidget(about_title)
        
        about_text = QLabel(
            f"<p><b>Version:</b> 1.0.0</p>"
            f"<p><b>Developer:</b> JUST ELSON PRODUCTIVE.labs</p>"
            f"<p><b>Copyright:</b> © {datetime.now().year} JUST ELSON PRODUCTIVE.labs</p>"
            "<p><b>License:</b> All rights reserved. Licensed under the application license agreement.</p>"
        )
        about_text.setWordWrap(True)
        about_text.setFont(QFont("Segoe UI", 11))
        scroll_layout.addWidget(about_text)
        
        # Divider
        divider2 = QFrame()
        divider2.setFrameShape(QFrame.Shape.HLine)
        divider2.setFrameShadow(QFrame.Shadow.Sunken)
        divider2.setStyleSheet("background-color: #334155;")
        scroll_layout.addWidget(divider2)
        
        # Components description
        components_title = QLabel("Suite Components")
        components_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        scroll_layout.addWidget(components_title)
        
        # Personal component
        personal_label = QLabel("<h3 style='color:#9C27B0;'>Personal File Organizer</h3>")
        personal_label.setTextFormat(Qt.TextFormat.RichText)
        scroll_layout.addWidget(personal_label)
        
        personal_desc = QLabel(
            "<p>The Personal File Organizer helps you organize your everyday personal files.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Simple, friendly interface with purple theme</li>"
            "<li>Customizable folder names</li>"
            "<li>Multiple personal file type support</li>"
            "<li>Intelligent file categorization</li>"
            "</ul>"
        )
        personal_desc.setTextFormat(Qt.TextFormat.RichText)
        personal_desc.setWordWrap(True)
        scroll_layout.addWidget(personal_desc)
        
        # Office component
        office_label = QLabel("<h3 style='color:#3B82F6;'>Office File Organizer</h3>")
        office_label.setTextFormat(Qt.TextFormat.RichText)
        scroll_layout.addWidget(office_label)
        
        office_desc = QLabel(
            "<p>The Office File Organizer is designed for business and professional document management.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Professional interface with blue theme</li>"
            "<li>Business document categorization</li>"
            "<li>Support for office file formats</li>"
            "<li>Customizable organization system</li>"
            "</ul>"
        )
        office_desc.setTextFormat(Qt.TextFormat.RichText)
        office_desc.setWordWrap(True)
        scroll_layout.addWidget(office_desc)
        
        # Media component
        media_label = QLabel("<h3 style='color:#FFA500;'>Media File Organizer</h3>")
        media_label.setTextFormat(Qt.TextFormat.RichText)
        scroll_layout.addWidget(media_label)
        
        media_desc = QLabel(
            "<p>The Media File Organizer specializes in organizing creative and media files.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Media-specific interface with orange theme</li>"
            "<li>Support for various media formats</li>"
            "<li>Categories designed for creative workflows</li>"
            "<li>Customizable media organization system</li>"
            "</ul>"
        )
        media_desc.setTextFormat(Qt.TextFormat.RichText)
        media_desc.setWordWrap(True)
        scroll_layout.addWidget(media_desc)
        
        # Usage instructions
        usage_label = QLabel("<h3>How to Use</h3>")
        usage_label.setTextFormat(Qt.TextFormat.RichText)
        scroll_layout.addWidget(usage_label)
        
        usage_desc = QLabel(
            "<p>Using any of the organizers is simple:</p>"
            "<ol>"
            "<li>Select your source folder containing files to organize</li>"
            "<li>Choose a destination folder where organized files will be placed</li>"
            "<li>Select the file types you want to organize</li>"
            "<li>Click 'Start Organizing' to begin</li>"
            "</ol>"
            "<p>You can also customize folder names by clicking the 'Customize Folder Names' button.</p>"
        )
        usage_desc.setTextFormat(Qt.TextFormat.RichText)
        usage_desc.setWordWrap(True)
        scroll_layout.addWidget(usage_desc)
        
        # Add some space at the bottom for better scrolling
        spacer = QWidget()
        spacer.setMinimumHeight(20)
        scroll_layout.addWidget(spacer)
        
        # Set the content widget to the scroll area
        main_scroll_area.setWidget(scroll_content)
        help_layout.addWidget(main_scroll_area)
        
        return help_widget

    def update_time(self):
        # Update time in all tabs
        for i in range(self.tab_widget.count()):
            tab = self.tab_widget.widget(i)
            if hasattr(tab, 'update_time'):
                tab.update_time()

    def setup_menu(self):
        # Removing menu since we now have a Help tab
        pass

    def show_about_dialog(self):
        # Not needed anymore as we have the Help tab
        pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Set application icon
    app_icon = QIcon("app_icons/the_all_in_one.png")
    app.setWindowIcon(app_icon)
    
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#1E293B"))
    app.setPalette(palette)
    
    window = UnifiedOrganizerApp()
    window.show()    
    window.setWindowFlags(Qt.WindowType.Window |
                  Qt.WindowType.CustomizeWindowHint |
                  Qt.WindowType.WindowMinimizeButtonHint | 
                  Qt.WindowType.WindowMaximizeButtonHint | 
                  Qt.WindowType.WindowCloseButtonHint)
    window.show()
    sys.exit(app.exec()) 