"""
Main window for Hair QC Tool

Provides the primary user interface with group/module/style management tabs.
"""

from PySide2 import QtWidgets, QtCore, QtGui
import maya.cmds as cmds
from pathlib import Path

from ..config import config


class HairQCMainWindow(QtWidgets.QMainWindow):
    """Main window for Hair QC Tool"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hair QC Tool v1.0")
        self.setMinimumSize(800, 600)
        self.resize(1400, 1000)
        # Start maximized by default for more vertical space
        self.setWindowState(self.windowState() | QtCore.Qt.WindowMaximized)
        
        # Make window stay on top but not always
        self.setWindowFlags(QtCore.Qt.Window)
        
        self.setup_ui()
        self.setup_shortcuts()
        
        # Initialize with first refresh
        self.refresh_data()
    
    def setup_ui(self):
        """Set up the main UI layout"""
        # Create menu bar first
        self.create_menu_bar()
        
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        # Root layout
        root_layout = QtWidgets.QVBoxLayout(central_widget)
        root_layout.setSpacing(10)
        root_layout.setContentsMargins(10, 10, 10, 10)
        
        # Scroll area wrapping the entire interface content
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(10)
        scroll_layout.setContentsMargins(0, 0, 0, 0)
        
        # Hotkey reference widget at top
        self.create_hotkey_widget(scroll_layout)
        
        # Use a vertical splitter so sections are independently resizable
        self.main_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        
        # Group selection section (top of splitter)
        group_frame = self.create_group_section()
        self.main_splitter.addWidget(group_frame)
        
        # Module/Style tab section (bottom of splitter)
        tab_widget = self.create_tab_section()
        self.main_splitter.addWidget(tab_widget)
        
        # Prefer more space to the tab section by default
        self.main_splitter.setStretchFactor(0, 1)
        self.main_splitter.setStretchFactor(1, 3)
        # Give an initial generous size allocation to improve vertical real estate
        self.main_splitter.setSizes([400, 900])
        
        scroll_layout.addWidget(self.main_splitter)
        scroll_area.setWidget(scroll_content)
        root_layout.addWidget(scroll_area)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def create_hotkey_widget(self, parent_layout):
        """Create hotkey reference widget at top"""
        hotkey_frame = QtWidgets.QFrame()
        hotkey_frame.setFrameStyle(QtWidgets.QFrame.Box)
        hotkey_frame.setStyleSheet("QFrame { background-color: #f0f0f0; }")
        
        hotkey_layout = QtWidgets.QHBoxLayout(hotkey_frame)
        
        hotkey_label = QtWidgets.QLabel("Shortcuts: Tab=Switch Tabs | F5=Refresh | Ctrl+R=Regen Timeline | Ctrl+S=Save | Ctrl+O=Change Directory")
        hotkey_label.setStyleSheet("font-size: 11px; color: #666;")
        
        hotkey_layout.addWidget(hotkey_label)
        hotkey_layout.addStretch()
        
        parent_layout.addWidget(hotkey_frame)
    
    def create_menu_bar(self):
        """Create the menu bar with File menu"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        # Change USD Directory action
        change_dir_action = QtWidgets.QAction('Change USD Directory...', self)
        change_dir_action.setShortcut('Ctrl+O')
        change_dir_action.setStatusTip('Change the USD directory location')
        change_dir_action.triggered.connect(self.change_usd_directory)
        file_menu.addAction(change_dir_action)
        
        # Show current directory action
        show_dir_action = QtWidgets.QAction('Show Current Directory', self)
        show_dir_action.setStatusTip('Show the current USD directory path')
        show_dir_action.triggered.connect(self.show_current_directory)
        file_menu.addAction(show_dir_action)
        
        file_menu.addSeparator()
        
        # Validate directory action
        validate_action = QtWidgets.QAction('Validate Directory Structure', self)
        validate_action.setStatusTip('Check if current directory has valid USD structure')
        validate_action.triggered.connect(self.validate_directory)
        file_menu.addAction(validate_action)
        
        # Initialize directory action
        init_action = QtWidgets.QAction('Initialize Empty Directory...', self)
        init_action.setStatusTip('Initialize an empty directory with USD structure')
        init_action.triggered.connect(self.initialize_directory)
        file_menu.addAction(init_action)
        
        file_menu.addSeparator()
        
        # Refresh action
        refresh_action = QtWidgets.QAction('Refresh Data', self)
        refresh_action.setShortcut('F5')
        refresh_action.setStatusTip('Refresh all data from USD files')
        refresh_action.triggered.connect(self.refresh_data)
        file_menu.addAction(refresh_action)
        
        # Settings menu
        settings_menu = menubar.addMenu('Settings')
        
        # Preferences action
        prefs_action = QtWidgets.QAction('Preferences...', self)
        prefs_action.setStatusTip('Open preferences dialog')
        prefs_action.triggered.connect(self.show_preferences)
        settings_menu.addAction(prefs_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        # About action
        about_action = QtWidgets.QAction('About Hair QC Tool', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_group_section(self):
        """Create group selection section"""
        # Group section frame
        group_frame = QtWidgets.QGroupBox("Select Group")
        group_layout = QtWidgets.QVBoxLayout(group_frame)
        
        # Group list
        self.group_list = QtWidgets.QListWidget()
        # Allow splitter-driven resizing instead of a fixed max height
        self.group_list.setMinimumHeight(120)
        self.group_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.group_list.currentRowChanged.connect(self.on_group_selected)
        group_layout.addWidget(self.group_list)
        
        # Group controls
        group_controls = QtWidgets.QHBoxLayout()
        self.add_group_btn = QtWidgets.QPushButton("Add Group")
        self.add_group_btn.clicked.connect(self.add_group)
        group_controls.addWidget(self.add_group_btn)
        group_controls.addStretch()
        
        group_layout.addLayout(group_controls)
        
        # Alpha whitelist (expandable)
        self.alpha_expander = QtWidgets.QGroupBox("Alpha Whitelist")
        self.alpha_expander.setCheckable(True)
        self.alpha_expander.setChecked(False)
        alpha_layout = QtWidgets.QVBoxLayout(self.alpha_expander)
        
        self.alpha_list = QtWidgets.QTableWidget()
        self.alpha_list.setColumnCount(3)
        self.alpha_list.setHorizontalHeaderLabels(["Whitelisted", "Texture Path", ""]) 
        self.alpha_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.alpha_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.alpha_list.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        alpha_layout.addWidget(self.alpha_list)
        
        group_layout.addWidget(self.alpha_expander)
        
        return group_frame
    
    def create_tab_section(self):
        """Create module/style tab section"""
        # Tab widget
        self.tab_widget = QtWidgets.QTabWidget()
        
        # Module tab
        self.module_tab = QtWidgets.QWidget()
        self.setup_module_tab()
        self.tab_widget.addTab(self.module_tab, "Module")
        
        # Style tab
        self.style_tab = QtWidgets.QWidget()
        self.setup_style_tab()
        self.tab_widget.addTab(self.style_tab, "Style")
        
        return self.tab_widget
    
    def setup_module_tab(self):
        """Set up the module management tab"""
        layout = QtWidgets.QVBoxLayout(self.module_tab)
        
        # Module selection
        module_select_frame = QtWidgets.QGroupBox("Module Selection")
        module_select_layout = QtWidgets.QVBoxLayout(module_select_frame)
        
        self.module_list = QtWidgets.QTableWidget()
        self.module_list.setColumnCount(2)
        self.module_list.setHorizontalHeaderLabels(["Type", "Name"]) 
        self.module_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.module_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.module_list.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.module_list.cellClicked.connect(self.on_module_row_clicked)
        self.module_list.currentItemChanged.connect(self.on_module_selected)
        module_select_layout.addWidget(self.module_list)
        
        # Module controls
        module_controls = QtWidgets.QHBoxLayout()
        self.add_module_btn = QtWidgets.QPushButton("Add Module")
        self.add_module_btn.clicked.connect(self.add_module)
        module_controls.addWidget(self.add_module_btn)
        module_controls.addStretch()
        
        module_select_layout.addLayout(module_controls)
        
        # Edit Module (expandable)
        self.module_edit_frame = QtWidgets.QGroupBox("Edit Module")
        self.module_edit_frame.setCheckable(True)
        self.module_edit_frame.setChecked(False)
        self.module_edit_frame.setEnabled(False)
        
        module_edit_layout = QtWidgets.QVBoxLayout(self.module_edit_frame)
        
        # Module properties
        # MODULE LIST 
        props_layout = QtWidgets.QFormLayout()
        self.module_name_edit = QtWidgets.QLineEdit()
        self.module_type_combo = QtWidgets.QComboBox()
        self.module_type_combo.addItems(["scalp", "crown", "tail", "bang"])
        
        props_layout.addRow("Name:", self.module_name_edit)
        props_layout.addRow("Type:", self.module_type_combo)
        
        module_edit_layout.addLayout(props_layout)
        
        # Base mesh LOADING 
        mesh_layout = QtWidgets.QHBoxLayout()
        self.base_mesh_label = QtWidgets.QLabel("No mesh loaded")
        self.replace_mesh_btn = QtWidgets.QPushButton("Replace")
        self.replace_mesh_btn.clicked.connect(self.replace_base_mesh)
        
        mesh_layout.addWidget(QtWidgets.QLabel("Base Mesh:"))
        mesh_layout.addWidget(self.base_mesh_label)
        mesh_layout.addWidget(self.replace_mesh_btn)
        mesh_layout.addStretch()
        
        module_edit_layout.addLayout(mesh_layout)
        
        # Blendshapes
        blend_frame = QtWidgets.QGroupBox("Blendshapes")
        blend_layout = QtWidgets.QVBoxLayout(blend_frame)
        #BLENDSHAPE LIST ======================================================
        self.blendshape_list = QtWidgets.QTableWidget()
        self.blendshape_list.setColumnCount(3)
        self.blendshape_list.setHorizontalHeaderLabels(["Name", "Weight", "Excluded"]) 
        self.blendshape_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.blendshape_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.blendshape_list.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        blend_layout.addWidget(self.blendshape_list)
        #======================================================================
        # Blendshape controls
        blend_controls = QtWidgets.QHBoxLayout()
        self.add_blendshape_btn = QtWidgets.QPushButton("Add Blendshape")
        self.add_blendshape_btn.clicked.connect(self.add_blendshape)
        blend_controls.addWidget(self.add_blendshape_btn)
        blend_controls.addStretch()
        
        blend_layout.addLayout(blend_controls)
        module_edit_layout.addWidget(blend_frame)
        
        # Save button
        save_layout = QtWidgets.QHBoxLayout()
        self.save_module_btn = QtWidgets.QPushButton("Save Module")
        self.save_module_btn.clicked.connect(self.save_module)
        save_layout.addStretch()
        save_layout.addWidget(self.save_module_btn)
        
        module_edit_layout.addLayout(save_layout)
        
        # Use a vertical splitter so the module list and edit area are resizable
        self.module_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.module_splitter.addWidget(module_select_frame)
        self.module_splitter.addWidget(self.module_edit_frame)
        self.module_splitter.setStretchFactor(0, 3)
        self.module_splitter.setStretchFactor(1, 2)
        # Initial sizes for better visibility
        self.module_splitter.setSizes([500, 700])
        layout.addWidget(self.module_splitter)
    
    def setup_style_tab(self):
        """Set up the style management tab"""
        layout = QtWidgets.QVBoxLayout(self.style_tab)
        
        # Style selection
        style_select_frame = QtWidgets.QGroupBox("Style Selection")
        style_select_layout = QtWidgets.QVBoxLayout(style_select_frame)
        
        # Style controls
        style_controls = QtWidgets.QHBoxLayout()
        self.generate_styles_btn = QtWidgets.QPushButton("Generate")
        self.add_valid_styles_btn = QtWidgets.QPushButton("Add Valid")
        self.cull_invalid_styles_btn = QtWidgets.QPushButton("Cull Invalid")
        
        self.generate_styles_btn.clicked.connect(self.generate_styles)
        self.add_valid_styles_btn.clicked.connect(self.add_valid_styles)
        self.cull_invalid_styles_btn.clicked.connect(self.cull_invalid_styles)
        
        style_controls.addWidget(self.generate_styles_btn)
        style_controls.addWidget(self.add_valid_styles_btn)
        style_controls.addWidget(self.cull_invalid_styles_btn)
        style_controls.addStretch()
        
        style_select_layout.addLayout(style_controls)
        
        # Style list
        self.style_list = QtWidgets.QTableWidget()
        self.style_list.setColumnCount(4)
        self.style_list.setHorizontalHeaderLabels(["Status", "Crown", "Tail", "Bang"]) 
        self.style_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.style_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.style_list.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.style_list.cellClicked.connect(self.on_style_row_clicked)
        self.style_list.currentItemChanged.connect(self.on_style_selected)
        style_select_layout.addWidget(self.style_list)
        
        # Edit Style (expandable)
        self.style_edit_frame = QtWidgets.QGroupBox("Edit Style")
        self.style_edit_frame.setCheckable(True)
        self.style_edit_frame.setChecked(False)
        self.style_edit_frame.setEnabled(False)
        
        style_edit_layout = QtWidgets.QVBoxLayout(self.style_edit_frame)
        
        # Timeline controls
        timeline_controls = QtWidgets.QHBoxLayout()
        self.regen_timeline_btn = QtWidgets.QPushButton("Regenerate Timeline")
        self.regen_timeline_btn.clicked.connect(self.regenerate_timeline)
        timeline_controls.addWidget(self.regen_timeline_btn)
        timeline_controls.addStretch()
        
        style_edit_layout.addLayout(timeline_controls)
        
        # Blendshape rules table
        rules_frame = QtWidgets.QGroupBox("Blendshape Rules")
        rules_layout = QtWidgets.QVBoxLayout(rules_frame)
        
        self.rules_list = QtWidgets.QTableWidget()
        self.rules_list.setColumnCount(7)
        self.rules_list.setHorizontalHeaderLabels([
            "Active","Type", "Name", "Blendshape", "Weight", "Max", "Exclude"
        ])
        self.rules_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.rules_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.rules_list.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        rules_layout.addWidget(self.rules_list)
        
        style_edit_layout.addWidget(rules_frame)
        
        # Save timeline button
        save_timeline_layout = QtWidgets.QHBoxLayout()
        self.save_timeline_btn = QtWidgets.QPushButton("Save Timeline")
        self.save_timeline_btn.clicked.connect(self.save_timeline)
        save_timeline_layout.addStretch()
        save_timeline_layout.addWidget(self.save_timeline_btn)
        
        style_edit_layout.addLayout(save_timeline_layout)
        
        # Use a vertical splitter so the style list and edit area are resizable
        self.style_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        self.style_splitter.addWidget(style_select_frame)
        self.style_splitter.addWidget(self.style_edit_frame)
        self.style_splitter.setStretchFactor(0, 3)
        self.style_splitter.setStretchFactor(1, 2)
        # Initial sizes for better visibility
        self.style_splitter.setSizes([500, 700])
        layout.addWidget(self.style_splitter)
    
    def setup_shortcuts(self):
        """Set up keyboard shortcuts"""
        # Tab switching
        tab_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Tab"), self)
        tab_shortcut.activated.connect(self.switch_tab)
        
        # Refresh data
        refresh_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("F5"), self)
        refresh_shortcut.activated.connect(self.refresh_data)
        
        # Regenerate timeline
        regen_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+R"), self)
        regen_shortcut.activated.connect(self.regenerate_timeline)
        
        # Save
        save_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_current)
    
    def switch_tab(self):
        """Switch between Module and Style tabs"""
        current_index = self.tab_widget.currentIndex()
        next_index = (current_index + 1) % self.tab_widget.count()
        self.tab_widget.setCurrentIndex(next_index)
    
    def refresh_data(self):
        """Refresh all data from USD files"""
        self.statusBar().showMessage("Refreshing data...")
        
        # TODO: Implement data refresh
        self.load_groups()
        
        self.statusBar().showMessage("Data refreshed", 2000)
    
    def load_groups(self):
        """Load groups from USD directory"""
        self.group_list.clear()
        
        if not config.usd_directory:
            return
        
        group_dir = config.usd_directory / "Group"
        if not group_dir.exists():
            return
        
        # Find all .usd files in Group directory
        for usd_file in group_dir.glob("*.usd"):
            group_name = usd_file.stem
            self.group_list.addItem(group_name)
    
    # Event handlers (placeholder implementations)
    def on_group_selected(self, row):
        """Handle group selection change"""
        if row >= 0:
            group_name = self.group_list.item(row).text()
            self.statusBar().showMessage(f"Selected group: {group_name}")
            # TODO: Load modules and styles for this group
    
    def on_module_selected(self, current_item, previous_item):
        """Handle module selection change"""
        if current_item:
            self.module_edit_frame.setEnabled(True)
            # TODO: Load module data into edit form
    
    def on_module_row_clicked(self, row, column):
        """Handle module row click selection"""
        self.module_list.selectRow(row)
        self.module_edit_frame.setEnabled(True)
    
    def on_style_selected(self, current_item, previous_item):
        """Handle style selection change"""
        if current_item:
            self.style_edit_frame.setEnabled(True)
            # TODO: Load style data and timeline
    
    def on_style_row_clicked(self, row, column):
        """Handle style row click selection"""
        self.style_list.selectRow(row)
        self.style_edit_frame.setEnabled(True)
    
    def add_group(self):
        """Add new group"""
        # TODO: Implement group creation
        pass
    
    def add_module(self):
        """Add new module"""
        # TODO: Implement module creation
        pass
    
    def add_blendshape(self):
        """Add blendshape to current module"""
        # TODO: Implement blendshape addition
        pass
    
    def replace_base_mesh(self):
        """Replace base mesh for current module"""
        # TODO: Implement mesh replacement
        pass
    
    def save_module(self):
        """Save current module to USD"""
        # TODO: Implement module saving
        pass
    
    def generate_styles(self):
        """Generate style combinations"""
        # TODO: Implement style generation
        pass
    
    def add_valid_styles(self):
        """Add all valid styles to disk"""
        # TODO: Implement valid style addition
        pass
    
    def cull_invalid_styles(self):
        """Remove all invalid styles"""
        # TODO: Implement invalid style removal
        pass
    
    def regenerate_timeline(self):
        """Regenerate timeline for current style"""
        # TODO: Implement timeline regeneration
        pass
    
    def save_timeline(self):
        """Save timeline to style USD"""
        # TODO: Implement timeline saving
        pass
    
    def save_current(self):
        """Save currently active item"""
        current_tab = self.tab_widget.currentIndex()
        if current_tab == 0:  # Module tab
            self.save_module()
        elif current_tab == 1:  # Style tab
            self.save_timeline()
    
    # Menu action handlers
    def change_usd_directory(self):
        """Change USD directory with validation and initialization"""
        from ..main import HairQCTool
        
        # Create a temporary tool instance to use its directory methods
        temp_tool = HairQCTool()
        temp_tool._browse_usd_directory()
        
        # Refresh data if directory was changed successfully
        self.refresh_data()
    
    def show_current_directory(self):
        """Show current USD directory path"""
        current_dir = config.usd_directory
        if current_dir:
            QtWidgets.QMessageBox.information(
                self,
                "Current USD Directory",
                f"Current USD directory:\n\n{current_dir}"
            )
        else:
            QtWidgets.QMessageBox.warning(
                self,
                "No Directory Set",
                "No USD directory is currently set.\n\nUse 'Change USD Directory' to set one."
            )
    
    def validate_directory(self):
        """Validate current directory structure"""
        validation_result, message = config.validate_usd_directory()
        
        if validation_result == True:
            QtWidgets.QMessageBox.information(
                self,
                "Directory Valid",
                f"Directory structure is valid!\n\n{message}"
            )
        elif validation_result == "empty":
            result = QtWidgets.QMessageBox.question(
                self,
                "Empty Directory",
                f"{message}\n\nWould you like to initialize it now?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            if result == QtWidgets.QMessageBox.Yes:
                self.initialize_current_directory()
        else:
            QtWidgets.QMessageBox.warning(
                self,
                "Directory Invalid",
                f"Directory structure is invalid:\n\n{message}"
            )
    
    def initialize_directory(self):
        """Initialize an empty directory"""
        # Browse for directory first
        directory = QtWidgets.QFileDialog.getExistingDirectory(
            self,
            "Select Directory to Initialize",
            str(config.usd_directory) if config.usd_directory else ""
        )
        
        if directory:
            # Temporarily set the directory
            old_directory = config.usd_directory
            config.usd_directory = directory
            
            # Check if it's empty and initialize
            validation_result, message = config.validate_usd_directory()
            if validation_result == "empty":
                result = QtWidgets.QMessageBox.question(
                    self,
                    "Initialize Directory",
                    f"Initialize directory with USD structure?\n\n{directory}\n\nThis will create:\n• Group/, module/, style/ directories\n• Sample group files\n• Required subdirectory structure",
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
                )
                
                if result == QtWidgets.QMessageBox.Yes:
                    success, init_message = config.initialize_usd_directory()
                    if success:
                        QtWidgets.QMessageBox.information(
                            self,
                            "Initialization Success",
                            f"Directory initialized successfully!\n\n{init_message}"
                        )
                        self.refresh_data()
                    else:
                        QtWidgets.QMessageBox.critical(
                            self,
                            "Initialization Failed",
                            f"Failed to initialize directory:\n\n{init_message}"
                        )
                        # Restore old directory
                        config.usd_directory = old_directory
                else:
                    # Restore old directory
                    config.usd_directory = old_directory
            else:
                QtWidgets.QMessageBox.warning(
                    self,
                    "Directory Not Empty",
                    f"Selected directory is not empty or has existing USD structure.\n\nUse 'Validate Directory Structure' to check the current directory."
                )
                # Restore old directory
                config.usd_directory = old_directory
    
    def initialize_current_directory(self):
        """Initialize the current USD directory"""
        success, message = config.initialize_usd_directory()
        
        if success:
            QtWidgets.QMessageBox.information(
                self,
                "Initialization Success",
                f"Directory initialized successfully!\n\n{message}"
            )
            self.refresh_data()
        else:
            QtWidgets.QMessageBox.critical(
                self,
                "Initialization Failed",
                f"Failed to initialize directory:\n\n{message}"
            )
    
    def show_preferences(self):
        """Show preferences dialog"""
        # TODO: Implement preferences dialog
        QtWidgets.QMessageBox.information(
            self,
            "Preferences",
            "Preferences dialog not yet implemented.\n\nCurrent settings are stored in:\n~/.hair_qc_tool_config.json"
        )
    
    def show_about(self):
        """Show about dialog"""
        QtWidgets.QMessageBox.about(
            self,
            "About Hair QC Tool",
            """<h3>Hair QC Tool v1.0</h3>
            <p>A comprehensive Maya tool for managing modular hair assets using USD-based data structures.</p>
            
            <p><b>Features:</b></p>
            <ul>
            <li>USD-based data management</li>
            <li>Modular hair system (scalp, crown, tail, bang)</li>
            <li>Blendshape QC and combination generation</li>
            <li>Cross-module rules and constraints</li>
            <li>Maya timeline integration</li>
            </ul>
            
            <p><b>Keyboard Shortcuts:</b></p>
            <ul>
            <li>Tab - Switch tabs</li>
            <li>F5 - Refresh data</li>
            <li>Ctrl+R - Regenerate timeline</li>
            <li>Ctrl+S - Save current</li>
            <li>Ctrl+O - Change directory</li>
            </ul>"""
        )