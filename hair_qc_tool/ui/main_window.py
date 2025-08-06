"""
Main window for Hair QC Tool

Provides the primary user interface with group/module/style management tabs.
"""

from PySide2 import QtWidgets, QtCore, QtGui
import maya.cmds as cmds
from pathlib import Path

from ..config import config
from ..managers import DataManager


class HairQCMainWindow(QtWidgets.QMainWindow):
    """Main window for Hair QC Tool"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Hair QC Tool v1.0")
        self.setMinimumSize(800, 600)
        self.resize(1000, 800)
        
        # Make window stay on top but not always
        self.setWindowFlags(QtCore.Qt.Window)
        
        # Initialize data manager
        self.data_manager = DataManager()
        
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
        
        # Main layout
        main_layout = QtWidgets.QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Hotkey reference widget at top
        self.create_hotkey_widget(main_layout)
        
        # Group selection section
        self.create_group_section(main_layout)
        
        # Module/Style tab section
        self.create_tab_section(main_layout)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def create_hotkey_widget(self, parent_layout):
        """Create hotkey reference widget at top"""
        hotkey_frame = QtWidgets.QFrame()
        hotkey_frame.setFrameStyle(QtWidgets.QFrame.Box)
        hotkey_frame.setStyleSheet("QFrame { background-color: #f0f0f0; }")
        
        hotkey_layout = QtWidgets.QHBoxLayout(hotkey_frame)
        
        hotkey_label = QtWidgets.QLabel("Shortcuts: Tab=Switch Tabs | F5=Refresh | Ctrl+R=Regen Timeline | Ctrl+S=Save Group | Ctrl+O=Change Directory")
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
    
    def create_group_section(self, parent_layout):
        """Create group selection section"""
        # Group section frame
        group_frame = QtWidgets.QGroupBox("Select Group")
        group_layout = QtWidgets.QVBoxLayout(group_frame)
        
        # Group list
        self.group_list = QtWidgets.QListWidget()
        self.group_list.setMaximumHeight(120)
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
        alpha_layout.addWidget(self.alpha_list)
        
        # Alpha controls
        alpha_controls = QtWidgets.QHBoxLayout()
        self.add_alpha_btn = QtWidgets.QPushButton("Add")
        self.add_alpha_btn.clicked.connect(self.add_alpha_texture)
        alpha_controls.addWidget(self.add_alpha_btn)
        alpha_controls.addStretch()
        
        alpha_layout.addLayout(alpha_controls)
        
        group_layout.addWidget(self.alpha_expander)
        
        parent_layout.addWidget(group_frame)
    
    def create_tab_section(self, parent_layout):
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
        
        parent_layout.addWidget(self.tab_widget)
    
    def setup_module_tab(self):
        """Set up the module management tab"""
        layout = QtWidgets.QVBoxLayout(self.module_tab)
        
        # Module selection
        module_select_frame = QtWidgets.QGroupBox("Module Selection")
        module_select_layout = QtWidgets.QVBoxLayout(module_select_frame)
        
        self.module_list = QtWidgets.QTableWidget()
        self.module_list.setColumnCount(4)
        self.module_list.setHorizontalHeaderLabels(["Selection", "Type", "Name", ""])
        self.module_list.currentItemChanged.connect(self.on_module_selected)
        module_select_layout.addWidget(self.module_list)
        
        # Module controls
        module_controls = QtWidgets.QHBoxLayout()
        self.add_module_btn = QtWidgets.QPushButton("Add Module")
        self.add_module_btn.clicked.connect(self.add_module)
        module_controls.addWidget(self.add_module_btn)
        module_controls.addStretch()
        
        module_select_layout.addLayout(module_controls)
        layout.addWidget(module_select_frame)
        
        # Edit Module (expandable)
        self.module_edit_frame = QtWidgets.QGroupBox("Edit Module")
        self.module_edit_frame.setCheckable(True)
        self.module_edit_frame.setChecked(False)
        self.module_edit_frame.setEnabled(False)
        
        module_edit_layout = QtWidgets.QVBoxLayout(self.module_edit_frame)
        
        # Module properties
        props_layout = QtWidgets.QFormLayout()
        self.module_name_edit = QtWidgets.QLineEdit()
        self.module_type_combo = QtWidgets.QComboBox()
        self.module_type_combo.addItems(["scalp", "crown", "tail", "bang"])
        
        props_layout.addRow("Name:", self.module_name_edit)
        props_layout.addRow("Type:", self.module_type_combo)
        
        module_edit_layout.addLayout(props_layout)
        
        # Base mesh
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
        
        self.blendshape_list = QtWidgets.QTableWidget()
        self.blendshape_list.setColumnCount(5)
        self.blendshape_list.setHorizontalHeaderLabels(["Selection", "Name", "Weight", "Excluded", ""])
        blend_layout.addWidget(self.blendshape_list)
        
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
        layout.addWidget(self.module_edit_frame)
    
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
        self.style_list.setColumnCount(6)
        self.style_list.setHorizontalHeaderLabels(["Selection", "Status", "Crown", "Tail", "Bang", ""])
        self.style_list.currentItemChanged.connect(self.on_style_selected)
        style_select_layout.addWidget(self.style_list)
        
        layout.addWidget(style_select_frame)
        
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
        self.rules_list.setColumnCount(8)
        self.rules_list.setHorizontalHeaderLabels([
            "Active", "Selection", "Type", "Name", "Blendshape", "Weight", "Max", "Exclude"
        ])
        rules_layout.addWidget(self.rules_list)
        
        style_edit_layout.addWidget(rules_frame)
        
        # Save timeline button
        save_timeline_layout = QtWidgets.QHBoxLayout()
        self.save_timeline_btn = QtWidgets.QPushButton("Save Timeline")
        self.save_timeline_btn.clicked.connect(self.save_timeline)
        save_timeline_layout.addStretch()
        save_timeline_layout.addWidget(self.save_timeline_btn)
        
        style_edit_layout.addLayout(save_timeline_layout)
        layout.addWidget(self.style_edit_frame)
    
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
        
        # Save current group
        save_shortcut = QtWidgets.QShortcut(QtGui.QKeySequence("Ctrl+S"), self)
        save_shortcut.activated.connect(self.save_current_group)
    
    def switch_tab(self):
        """Switch between Module and Style tabs"""
        current_index = self.tab_widget.currentIndex()
        next_index = (current_index + 1) % self.tab_widget.count()
        self.tab_widget.setCurrentIndex(next_index)
    
    def refresh_data(self):
        """Refresh all data from USD files"""
        self.statusBar().showMessage("Refreshing data...")
        
        # Refresh data using data manager
        success, message = self.data_manager.refresh_all_data()
        
        if success:
            self.load_groups()
            self.load_alpha_whitelist()
            self.statusBar().showMessage("Data refreshed", 2000)
        else:
            self.statusBar().showMessage(f"Refresh failed: {message}", 5000)
            QtWidgets.QMessageBox.warning(self, "Refresh Failed", message)
    
    def load_groups(self):
        """Load groups from USD directory"""
        self.group_list.clear()
        
        # Get groups from data manager
        groups = self.data_manager.get_groups(force_refresh=True)
        
        for group_name in groups:
            self.group_list.addItem(group_name)
        
        # Restore selection if we had a current group
        current_group = self.data_manager.get_current_group()
        if current_group:
            items = self.group_list.findItems(current_group, QtCore.Qt.MatchExactly)
            if items:
                self.group_list.setCurrentItem(items[0])
    
    # Event handlers
    def on_group_selected(self, row):
        """Handle group selection change"""
        if row >= 0:
            group_name = self.group_list.item(row).text()
            self.statusBar().showMessage(f"Loading group: {group_name}...")
            
            # Load group using data manager
            success, message = self.data_manager.load_group(group_name)
            
            if success:
                self.statusBar().showMessage(f"Loaded group: {group_name}", 3000)
                # Update alpha whitelist UI
                self.load_alpha_whitelist()
                # TODO: Load modules and styles for this group
            else:
                self.statusBar().showMessage(f"Failed to load group: {message}", 5000)
                QtWidgets.QMessageBox.warning(self, "Load Group Failed", f"Failed to load group '{group_name}':\n\n{message}")
        else:
            self.statusBar().showMessage("No group selected")
    
    def load_alpha_whitelist(self):
        """Load alpha whitelist for current group"""
        self.alpha_list.setRowCount(0)
        
        current_group = self.data_manager.get_current_group()
        if not current_group:
            return
        
        # Get alpha whitelist from data manager
        alpha_whitelist = self.data_manager.get_group_alpha_whitelist()
        available_textures = self.data_manager.get_available_alpha_textures()
        
        # Populate alpha list
        row = 0
        for texture_path, enabled in alpha_whitelist.items():
            self.alpha_list.insertRow(row)
            
            # Checkbox for whitelisted status
            checkbox = QtWidgets.QCheckBox()
            checkbox.setChecked(enabled)
            checkbox.stateChanged.connect(lambda state, path=texture_path: self.on_alpha_toggled(path, state == QtCore.Qt.Checked))
            self.alpha_list.setCellWidget(row, 0, checkbox)
            
            # Texture path
            path_item = QtWidgets.QTableWidgetItem(texture_path)
            path_item.setFlags(path_item.flags() & ~QtCore.Qt.ItemIsEditable)  # Read-only
            self.alpha_list.setItem(row, 1, path_item)
            
            # Remove button
            remove_btn = QtWidgets.QPushButton("Remove")
            remove_btn.clicked.connect(lambda checked, path=texture_path: self.remove_alpha_texture(path))
            self.alpha_list.setCellWidget(row, 2, remove_btn)
            
            row += 1
        
        # Resize columns
        self.alpha_list.resizeColumnsToContents()
    
    def on_alpha_toggled(self, texture_path: str, enabled: bool):
        """Handle alpha texture toggle"""
        self.data_manager.update_alpha_whitelist(texture_path, enabled)
        
        # Update status to show unsaved changes
        if self.data_manager.has_unsaved_changes('group'):
            self.statusBar().showMessage("Group has unsaved changes", 2000)
    
    def add_alpha_texture(self):
        """Add new alpha texture path"""
        # Get texture path from user
        texture_path, ok = QtWidgets.QInputDialog.getText(
            self,
            "Add Alpha Texture",
            "Enter texture path (relative to module directory):\nExample: scalp/alpha/fade/newTexture.png",
            QtWidgets.QLineEdit.Normal,
            ""
        )
        
        if not ok or not texture_path.strip():
            return
        
        texture_path = texture_path.strip()
        
        # Add texture path using data manager
        success, message = self.data_manager.add_alpha_texture_path(texture_path, True)
        
        if success:
            self.load_alpha_whitelist()  # Refresh the list
            self.statusBar().showMessage(f"Added texture: {texture_path}", 3000)
        else:
            QtWidgets.QMessageBox.warning(self, "Add Texture Failed", message)
    
    def remove_alpha_texture(self, texture_path: str):
        """Remove alpha texture path"""
        # Confirm removal
        result = QtWidgets.QMessageBox.question(
            self,
            "Remove Alpha Texture",
            f"Remove texture path '{texture_path}' from whitelist?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if result == QtWidgets.QMessageBox.Yes:
            success, message = self.data_manager.remove_alpha_texture_path(texture_path)
            
            if success:
                self.load_alpha_whitelist()  # Refresh the list
                self.statusBar().showMessage(f"Removed texture: {texture_path}", 3000)
            else:
                QtWidgets.QMessageBox.warning(self, "Remove Texture Failed", message)
    
    def save_current_group(self):
        """Save current group data"""
        if not self.data_manager.get_current_group():
            self.statusBar().showMessage("No group selected to save", 3000)
            return
        
        if not self.data_manager.has_unsaved_changes('group'):
            self.statusBar().showMessage("No changes to save", 2000)
            return
        
        self.statusBar().showMessage("Saving group...")
        success, message = self.data_manager.save_current_group()
        
        if success:
            self.statusBar().showMessage("Group saved successfully", 3000)
        else:
            self.statusBar().showMessage(f"Save failed: {message}", 5000)
            QtWidgets.QMessageBox.warning(self, "Save Failed", f"Failed to save group:\n\n{message}")
    
    def on_module_selected(self, current_item, previous_item):
        """Handle module selection change"""
        if current_item:
            self.module_edit_frame.setEnabled(True)
            # TODO: Load module data into edit form
    
    def on_style_selected(self, current_item, previous_item):
        """Handle style selection change"""
        if current_item:
            self.style_edit_frame.setEnabled(True)
            # TODO: Load style data and timeline
    
    def add_group(self):
        """Add new group"""
        # Get group name from user
        group_name, ok = QtWidgets.QInputDialog.getText(
            self,
            "Create New Group",
            "Enter group name:",
            QtWidgets.QLineEdit.Normal,
            ""
        )
        
        if not ok or not group_name.strip():
            return
        
        group_name = group_name.strip()
        
        # Create group using data manager
        self.statusBar().showMessage(f"Creating group: {group_name}...")
        success, message = self.data_manager.create_group(group_name)
        
        if success:
            self.statusBar().showMessage(f"Created group: {group_name}", 3000)
            # Refresh groups list and select the new group
            self.load_groups()
            items = self.group_list.findItems(group_name, QtCore.Qt.MatchExactly)
            if items:
                self.group_list.setCurrentItem(items[0])
        else:
            self.statusBar().showMessage(f"Failed to create group: {message}", 5000)
            QtWidgets.QMessageBox.warning(self, "Create Group Failed", f"Failed to create group '{group_name}':\n\n{message}")
    
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