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
        
        # Create scroll area as central widget
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.setCentralWidget(scroll_area)
        
        # Create the main content widget - size will be dynamic based on splitter content
        content_widget = QtWidgets.QWidget()
        scroll_area.setWidget(content_widget)
        
        # Store references for dynamic sizing
        self.scroll_area = scroll_area
        self.content_widget = content_widget
        
        # Main layout for content
        main_layout = QtWidgets.QVBoxLayout(content_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # Hotkey reference widget at top
        self.create_hotkey_widget(main_layout)
        
        # Create main splitter for resizable sections
        main_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        
        # Group selection section
        self.create_group_section_splitter(main_splitter)
        
        # Module/Style tab section
        self.create_tab_section_splitter(main_splitter)
        
        # Set initial splitter sizes (give more space to tabs)
        main_splitter.setSizes([300, 500])
        main_splitter.setCollapsible(0, False)
        main_splitter.setCollapsible(1, False)
        
        # Allow unlimited expansion by removing size constraints
        main_splitter.setMaximumHeight(16777215)  # Qt's QWIDGETSIZE_MAX
        size_policy = main_splitter.sizePolicy()
        size_policy.setVerticalPolicy(QtWidgets.QSizePolicy.Expanding)
        main_splitter.setSizePolicy(size_policy)
        
        # Store reference to main splitter for dynamic sizing
        self.main_splitter = main_splitter
        
        # Connect splitter moved signal to update content size
        main_splitter.splitterMoved.connect(self.update_content_size)
        
        main_layout.addWidget(main_splitter)
        
        # Status bar
        self.statusBar().showMessage("Ready")
        
        # Initial content size update
        QtCore.QTimer.singleShot(100, self.update_content_size)
    
    def create_hotkey_widget(self, parent_layout):
        """Create hotkey reference widget at top"""
        hotkey_frame = QtWidgets.QFrame()
        hotkey_frame.setFrameStyle(QtWidgets.QFrame.Box)
        hotkey_frame.setStyleSheet("QFrame { background-color: #f0f0f0; }")
        
        hotkey_layout = QtWidgets.QHBoxLayout(hotkey_frame)
        
        hotkey_label = QtWidgets.QLabel("Shortcuts: Tab=Switch Tabs | F5=Refresh | Ctrl+R=Regen Timeline | Ctrl+S=Save All | Ctrl+O=Change Directory")
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
    
    def create_group_section_splitter(self, parent_splitter):
        """Create group selection section with splitter support"""
        group_widget = QtWidgets.QWidget()
        self.create_group_section(group_widget)
        parent_splitter.addWidget(group_widget)
    
    def create_group_section(self, parent_widget):
        """Create group selection section"""
        # Create layout for parent widget
        parent_layout = QtWidgets.QVBoxLayout(parent_widget)
        parent_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create vertical splitter for group section components
        group_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        
        # Group selection frame
        group_select_frame = QtWidgets.QGroupBox("Select Group")
        group_select_layout = QtWidgets.QVBoxLayout(group_select_frame)
        
        # Group list
        self.group_list = QtWidgets.QListWidget()
        # Remove fixed height to allow resizing
        self.group_list.currentRowChanged.connect(self.on_group_selected)
        group_select_layout.addWidget(self.group_list)
        
        # Group controls
        group_controls = QtWidgets.QHBoxLayout()
        self.add_group_btn = QtWidgets.QPushButton("Add Group")
        self.add_group_btn.clicked.connect(self.add_group)
        group_controls.addWidget(self.add_group_btn)
        group_controls.addStretch()
        
        group_select_layout.addLayout(group_controls)
        
        # Add group selection frame to splitter
        group_splitter.addWidget(group_select_frame)
        
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
        
        # Add alpha whitelist to splitter
        group_splitter.addWidget(self.alpha_expander)
        
        # Set initial sizes for group splitter (group list smaller, alpha list larger)
        group_splitter.setSizes([120, 180])
        group_splitter.setCollapsible(0, False)
        group_splitter.setCollapsible(1, True)  # Alpha can be collapsed
        
        # Allow unlimited expansion for group splitter
        group_splitter.setMaximumHeight(16777215)
        size_policy = group_splitter.sizePolicy()
        size_policy.setVerticalPolicy(QtWidgets.QSizePolicy.Expanding)
        group_splitter.setSizePolicy(size_policy)
        
        # Connect group splitter to update content size
        group_splitter.splitterMoved.connect(self.update_content_size)
        
        # Add splitter to parent layout
        parent_layout.addWidget(group_splitter)
    
    def create_tab_section_splitter(self, parent_splitter):
        """Create module/style tab section with splitter support"""
        tab_widget = QtWidgets.QWidget()
        self.create_tab_section(tab_widget)
        parent_splitter.addWidget(tab_widget)
    
    def create_tab_section(self, parent_widget):
        """Create module/style tab section"""
        # Create layout for parent widget
        parent_layout = QtWidgets.QVBoxLayout(parent_widget)
        parent_layout.setContentsMargins(0, 0, 0, 0)
        
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
        
        # Create vertical splitter for module tab sections
        module_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        
        # Module selection
        module_select_frame = QtWidgets.QGroupBox("Module Selection")
        module_select_layout = QtWidgets.QVBoxLayout(module_select_frame)
        
        self.module_list = QtWidgets.QTableWidget()
        self.module_list.setColumnCount(3)
        self.module_list.setHorizontalHeaderLabels(["Type", "Name", "Status"])
        self.module_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.module_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.module_list.currentItemChanged.connect(self.on_module_selected)
        
        # Store column widths for restoration
        self.module_list_column_widths = [80, 150, 100]
        
        # Connect to save column widths when resized
        header = self.module_list.horizontalHeader()
        header.sectionResized.connect(self.save_module_list_column_widths)
        
        module_select_layout.addWidget(self.module_list)
        
        # Module controls
        module_controls = QtWidgets.QHBoxLayout()
        self.add_module_btn = QtWidgets.QPushButton("Add Module")
        self.add_module_btn.clicked.connect(self.add_module)
        module_controls.addWidget(self.add_module_btn)
        
        self.remove_module_btn = QtWidgets.QPushButton("Remove Module")
        self.remove_module_btn.clicked.connect(self.remove_module)
        self.remove_module_btn.setEnabled(False)  # Enabled when module selected
        module_controls.addWidget(self.remove_module_btn)
        
        module_controls.addStretch()
        
        module_select_layout.addLayout(module_controls)
        module_splitter.addWidget(module_select_frame)
        
        # Edit Module (expandable)
        self.module_edit_frame = QtWidgets.QGroupBox("Edit Module")
        self.module_edit_frame.setCheckable(True)
        self.module_edit_frame.setChecked(False)
        self.module_edit_frame.setEnabled(False)
        
        module_edit_layout = QtWidgets.QVBoxLayout(self.module_edit_frame)
        
        # Module properties
        props_layout = QtWidgets.QFormLayout()
        self.module_name_edit = QtWidgets.QLineEdit()
        self.module_name_edit.editingFinished.connect(self.on_module_name_changed)
        self.module_type_combo = QtWidgets.QComboBox()
        self.module_type_combo.addItems(["scalp", "crown", "tail", "bang"])
        self.module_type_combo.currentTextChanged.connect(self.on_module_type_changed)
        
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
        
        self.load_viewport_btn = QtWidgets.QPushButton("Load in Viewport")
        self.load_viewport_btn.clicked.connect(self.load_module_in_viewport)
        self.load_viewport_btn.setEnabled(False)  # Enabled when module is loaded
        mesh_layout.addWidget(self.load_viewport_btn)
        
        mesh_layout.addStretch()
        
        module_edit_layout.addLayout(mesh_layout)
        
        # Blendshapes
        blend_frame = QtWidgets.QGroupBox("Blendshapes (Weights = Viewport Preview Only)")
        blend_layout = QtWidgets.QVBoxLayout(blend_frame)
        
        self.blendshape_list = QtWidgets.QTableWidget()
        self.blendshape_list.setColumnCount(4)
        self.blendshape_list.setHorizontalHeaderLabels(["Name", "Weight", "Exclusions", ""])
        self.blendshape_list.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.blendshape_list.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.blendshape_list.currentItemChanged.connect(self.on_blendshape_selected)
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
        module_splitter.addWidget(self.module_edit_frame)
        
        # Set initial sizes for module splitter (selection smaller, edit larger)
        module_splitter.setSizes([200, 400])
        module_splitter.setCollapsible(0, False)
        module_splitter.setCollapsible(1, True)  # Edit section can be collapsed
        
        # Allow unlimited expansion for module splitter
        module_splitter.setMaximumHeight(16777215)
        size_policy = module_splitter.sizePolicy()
        size_policy.setVerticalPolicy(QtWidgets.QSizePolicy.Expanding)
        module_splitter.setSizePolicy(size_policy)
        
        # Connect module splitter to update content size
        module_splitter.splitterMoved.connect(self.update_content_size)
        
        layout.addWidget(module_splitter)
    
    def setup_style_tab(self):
        """Set up the style management tab"""
        layout = QtWidgets.QVBoxLayout(self.style_tab)
        
        # Create vertical splitter for style tab sections
        style_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        
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
        
        style_splitter.addWidget(style_select_frame)
        
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
        style_splitter.addWidget(self.style_edit_frame)
        
        # Set initial sizes for style splitter (selection smaller, edit larger)
        style_splitter.setSizes([200, 400])
        style_splitter.setCollapsible(0, False)
        style_splitter.setCollapsible(1, True)  # Edit section can be collapsed
        
        # Allow unlimited expansion for style splitter
        style_splitter.setMaximumHeight(16777215)
        size_policy = style_splitter.sizePolicy()
        size_policy.setVerticalPolicy(QtWidgets.QSizePolicy.Expanding)
        style_splitter.setSizePolicy(size_policy)
        
        # Connect style splitter to update content size
        style_splitter.splitterMoved.connect(self.update_content_size)
        
        layout.addWidget(style_splitter)
    
    def update_content_size(self):
        """Dynamically update content widget size based on splitter content"""
        try:
            # Use the main splitter's actual size hint to determine required height
            splitter_size_hint = self.main_splitter.sizeHint()
            
            # Add padding for hotkey widget, margins, and splitter handles
            hotkey_height = 40  # Approximate height of hotkey widget
            margins = 20  # Top and bottom margins
            
            # Calculate minimum required height based on size hint
            required_height = splitter_size_hint.height() + hotkey_height + margins
            
            # Ensure we have a reasonable minimum but allow unlimited expansion
            min_height = max(required_height, 400)
            
            # Update content widget size if it has changed significantly
            current_min_height = self.content_widget.minimumHeight()
            if abs(current_min_height - min_height) > 20:  # 20px tolerance to avoid excessive updates
                self.content_widget.setMinimumHeight(min_height)
                
                # Also set a minimum width to prevent horizontal scrolling issues
                self.content_widget.setMinimumWidth(780)
                
                # Force layout updates
                self.content_widget.updateGeometry()
                self.scroll_area.updateGeometry()
                
        except Exception as e:
            # Fail silently to avoid disrupting the UI
            pass
    
    def resizeEvent(self, event):
        """Handle window resize events"""
        super().resizeEvent(event)
        # Update content size when window is resized
        QtCore.QTimer.singleShot(50, self.update_content_size)
    
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
            # Clear USD stages when refreshing data (full cleanup)
            self.data_manager.clear_usd_stages()
            self.load_groups()
            self.load_alpha_whitelist()
            self.load_modules()
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
                # Clear USD stages when switching groups (full cleanup)
                self.data_manager.clear_usd_stages()
                # Update alpha whitelist UI
                self.load_alpha_whitelist()
                # Load modules for this group
                self.load_modules()
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
        """Add new alpha texture path using file browser"""
        from ..config import config
        
        if not config.usd_directory:
            QtWidgets.QMessageBox.warning(
                self, 
                "No USD Directory", 
                "Please set a USD directory first before adding alpha textures."
            )
            return
        
        # Define the alpha texture directory structure based on project docs
        module_dir = config.usd_directory / "module"
        if not module_dir.exists():
            QtWidgets.QMessageBox.warning(
                self, 
                "Module Directory Missing", 
                f"Module directory not found: {module_dir}\n\nPlease ensure your USD directory has the correct structure."
            )
            return
        
        # Start file browser from the module directory
        file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self,
            "Select Alpha Texture",
            str(module_dir),
            "PNG Images (*.png);;All Files (*.*)"
        )
        
        if not file_path:
            return  # User cancelled
        
        # Convert absolute path to relative path from module directory
        try:
            file_path = Path(file_path)
            relative_path = file_path.relative_to(module_dir)
            texture_path = str(relative_path).replace('\\', '/')  # Ensure forward slashes
            
            # Validate that this is actually an alpha texture path
            path_parts = relative_path.parts
            if len(path_parts) < 4 or path_parts[1] != "alpha":
                result = QtWidgets.QMessageBox.question(
                    self,
                    "Confirm Alpha Texture",
                    f"The selected file doesn't appear to be in a standard alpha texture location:\n{texture_path}\n\nExpected format: module_type/alpha/category/texture.png\n\nAdd it anyway?",
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                    QtWidgets.QMessageBox.No
                )
                if result != QtWidgets.QMessageBox.Yes:
                    return
            
        except ValueError:
            QtWidgets.QMessageBox.warning(
                self, 
                "Invalid Path", 
                f"Selected file must be within the module directory:\n{module_dir}"
            )
            return
        
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
    
    def restore_module_list_column_widths(self):
        """Restore column widths for module list"""
        try:
            for col, width in enumerate(self.module_list_column_widths):
                self.module_list.setColumnWidth(col, width)
        except:
            # If restoration fails, use default sizing
            self.module_list.resizeColumnsToContents()
    
    def save_module_list_column_widths(self):
        """Save current column widths"""
        try:
            self.module_list_column_widths = []
            for col in range(self.module_list.columnCount()):
                self.module_list_column_widths.append(self.module_list.columnWidth(col))
        except:
            pass
    
    def load_modules(self):
        """Load modules for current group"""
        self.module_list.setRowCount(0)
        
        current_group = self.data_manager.get_current_group()
        if not current_group:
            return
        
        # Get modules from data manager
        modules = self.data_manager.get_modules(force_refresh=True)
        
        # Get module types from group whitelist for display
        module_types = {}
        current_group = self.data_manager.get_current_group()
        if current_group and hasattr(self.data_manager.group_manager, 'group_data'):
            try:
                from ..config import config
                group_file = config.usd_directory / "Group" / f"{current_group}.usd"
                if group_file.exists():
                    from ..utils import USDGroupUtils
                    group_utils = USDGroupUtils(group_file)
                    module_whitelist = group_utils.get_module_whitelist()
                    if module_whitelist:
                        for mod_name, mod_info in module_whitelist.items():
                            module_types[mod_name] = mod_info.get('type', 'unknown')
            except Exception:
                pass
        
        # Populate module list
        row = 0
        for module_name in modules:
            self.module_list.insertRow(row)
            
            # Type - get from group whitelist or unknown
            module_type = module_types.get(module_name, "unknown")
            type_item = QtWidgets.QTableWidgetItem(module_type)
            type_item.setFlags(type_item.flags() & ~QtCore.Qt.ItemIsEditable)
            self.module_list.setItem(row, 0, type_item)
            
            # Name
            name_item = QtWidgets.QTableWidgetItem(module_name)
            name_item.setFlags(name_item.flags() & ~QtCore.Qt.ItemIsEditable)
            self.module_list.setItem(row, 1, name_item)
            
            # Status (will be updated when module is loaded)
            status_item = QtWidgets.QTableWidgetItem("Not loaded")
            status_item.setFlags(status_item.flags() & ~QtCore.Qt.ItemIsEditable)
            self.module_list.setItem(row, 2, status_item)
            
            row += 1
        
        # Restore column widths
        self.restore_module_list_column_widths()
        
        # Restore selection if we had a current module
        current_module = self.data_manager.get_current_module()
        if current_module:
            # Find the row with this module name
            for row in range(self.module_list.rowCount()):
                name_item = self.module_list.item(row, 1)  # Name is now in column 1
                if name_item and name_item.text() == current_module:
                    self.module_list.selectRow(row)
                    # Update status to show it's loaded
                    status_item = self.module_list.item(row, 2)
                    if status_item:
                        status_item.setText("Loaded")
                    break
    
    def save_current_group(self):
        """Save current group and module data"""
        # Check what needs saving
        has_group_changes = self.data_manager.has_unsaved_changes('group')
        has_module_changes = self.data_manager.has_unsaved_changes('modules')
        
        if not has_group_changes and not has_module_changes:
            self.statusBar().showMessage("No changes to save", 2000)
            return
        
        saved_items = []
        failed_items = []
        
        # Save group if needed
        if has_group_changes and self.data_manager.get_current_group():
            self.statusBar().showMessage("Saving group...")
            success, message = self.data_manager.save_current_group()
            
            if success:
                saved_items.append("group")
            else:
                failed_items.append(f"group: {message}")
        
        # Save module if needed
        if has_module_changes and self.data_manager.get_current_module():
            self.statusBar().showMessage("Saving module...")
            success, message = self.data_manager.save_current_module()
            
            if success:
                saved_items.append("module")
            else:
                failed_items.append(f"module: {message}")
        
        # Report results
        if saved_items and not failed_items:
            saved_text = " and ".join(saved_items)
            self.statusBar().showMessage(f"Saved {saved_text} successfully", 3000)
        elif saved_items and failed_items:
            saved_text = " and ".join(saved_items)
            failed_text = "; ".join(failed_items)
            self.statusBar().showMessage(f"Saved {saved_text}, but failed: {failed_text}", 5000)
            QtWidgets.QMessageBox.warning(self, "Partial Save Failed", f"Saved: {saved_text}\n\nFailed: {failed_text}")
        elif failed_items:
            failed_text = "; ".join(failed_items)
            self.statusBar().showMessage(f"Save failed: {failed_text}", 5000)
            QtWidgets.QMessageBox.warning(self, "Save Failed", f"Failed to save:\n\n{failed_text}")
    
    def on_module_selected(self, current_item, previous_item):
        """Handle module selection change"""
        if current_item:
            # Get module name from the selected row
            row = current_item.row()
            name_item = self.module_list.item(row, 1)  # Name is now in column 1
            
            if name_item:
                module_name = name_item.text()
                self.statusBar().showMessage(f"Loading module: {module_name}...")
                
                # Load module using data manager
                success, message = self.data_manager.load_module(module_name)
                
                if success:
                    self.statusBar().showMessage(f"Loaded module: {module_name}", 3000)
                    # Enable edit frame and load module data
                    self.module_edit_frame.setEnabled(True)
                    self.remove_module_btn.setEnabled(True)
                    self.load_module_edit_data()
                    
                    # Load geometry into Maya viewport if module has geometry
                    module_info = self.data_manager.get_current_module_info()
                    if module_info and module_info.get('has_geometry', False):
                        self.statusBar().showMessage(f"Loading geometry for {module_name} into viewport...")
                        geo_success, geo_message = self.data_manager.load_geometry_to_scene()
                        
                        if geo_success:
                            self.statusBar().showMessage(f"Loaded module and geometry: {module_name}", 3000)
                        else:
                            self.statusBar().showMessage(f"Loaded module but failed to load geometry: {geo_message}", 5000)
                            # Still consider the module load successful
                    
                    # Update status in the list
                    status_item = self.module_list.item(row, 2)
                    if status_item:
                        status_item.setText("Loaded")
                else:
                    self.statusBar().showMessage(f"Failed to load module: {message}", 5000)
                    QtWidgets.QMessageBox.warning(self, "Load Module Failed", f"Failed to load module '{module_name}':\n\n{message}")
                    self.module_edit_frame.setEnabled(False)
                    self.remove_module_btn.setEnabled(False)
                    
                    # Update status to show error
                    status_item = self.module_list.item(row, 2)
                    if status_item:
                        status_item.setText("Error")
            else:
                self.module_edit_frame.setEnabled(False)
                self.remove_module_btn.setEnabled(False)
        else:
            # No module selected - clear proxy shapes and disable edit frame
            self.data_manager.clear_module_proxy_shapes()
            self.module_edit_frame.setEnabled(False)
            self.remove_module_btn.setEnabled(False)
    
    def load_module_edit_data(self):
        """Load current module data into edit form"""
        current_module = self.data_manager.get_current_module()
        if not current_module:
            return
        
        # Update module properties
        self.module_name_edit.setText(current_module)
        
        # Get module type from module manager if available
        if hasattr(self.data_manager.module_manager, 'modules') and current_module in self.data_manager.module_manager.modules:
            module_info = self.data_manager.module_manager.modules[current_module]
            module_type = module_info.module_type
            
            # Set combo box to correct type
            type_index = self.module_type_combo.findText(module_type)
            if type_index >= 0:
                self.module_type_combo.setCurrentIndex(type_index)
            
            # Update base mesh status and enable viewport loading
            if module_info.geometry_loaded:
                self.base_mesh_label.setText("Geometry loaded")
                self.load_viewport_btn.setEnabled(True)
                # Automatically load in viewport when module is selected
                self.load_module_in_viewport()
            else:
                self.base_mesh_label.setText("No geometry loaded")
                self.load_viewport_btn.setEnabled(False)
                # No additional button to disable
        
        # Load blendshapes
        self.load_module_blendshapes()
    
    def load_module_blendshapes(self):
        """Load blendshapes for current module"""
        self.blendshape_list.setRowCount(0)
        
        current_module = self.data_manager.get_current_module()
        if not current_module:
            return
        
        # Get blendshapes and exclusions from data manager
        blendshapes = self.data_manager.get_module_blendshapes()
        exclusions = self.data_manager.get_module_exclusions()
        
        # Populate blendshape list
        row = 0
        for bs_name, weight in blendshapes.items():
            self.blendshape_list.insertRow(row)
            
            # Name (non-editable for now)
            name_item = QtWidgets.QTableWidgetItem(bs_name)
            name_item.setFlags(name_item.flags() & ~QtCore.Qt.ItemIsEditable)
            self.blendshape_list.setItem(row, 0, name_item)
            
            # Weight slider
            weight_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
            weight_slider.setRange(0, 100)
            weight_slider.setValue(int(weight * 100))
            weight_slider.valueChanged.connect(lambda val, name=bs_name: self.on_blendshape_weight_changed(name, val / 100.0))
            self.blendshape_list.setCellWidget(row, 1, weight_slider)
            
            # Exclusions - show as clickable list
            excluded_list = exclusions.get(bs_name, [])
            if excluded_list:
                exclusion_text = ", ".join(excluded_list)
            else:
                exclusion_text = "None"
            exclusion_item = QtWidgets.QTableWidgetItem(exclusion_text)
            exclusion_item.setFlags(exclusion_item.flags() & ~QtCore.Qt.ItemIsEditable)
            exclusion_item.setToolTip(f"Click to edit exclusions for {bs_name}")
            self.blendshape_list.setItem(row, 2, exclusion_item)
            
            # Remove button
            remove_btn = QtWidgets.QPushButton("Remove")
            remove_btn.clicked.connect(lambda checked, name=bs_name: self.remove_module_blendshape(name))
            self.blendshape_list.setCellWidget(row, 3, remove_btn)
            
            row += 1
        
        # Resize columns
        self.blendshape_list.resizeColumnsToContents()
    
    def on_blendshape_weight_changed(self, blendshape_name: str, weight: float):
        """Handle blendshape weight change (viewport preview only - not saved)"""
        success, message = self.data_manager.set_blendshape_weight(blendshape_name, weight)
        
        if success:
            # Show that this is viewport preview only
            self.statusBar().showMessage(f"Preview: {blendshape_name} = {weight:.2f} (not saved)", 2000)
        else:
            self.statusBar().showMessage(f"Failed to set weight: {message}", 3000)
    
    def on_blendshape_selected(self, current_item, previous_item):
        """Handle blendshape selection - show exclusion editing for selected blendshape"""
        if not current_item:
            return
            
        row = current_item.row()
        name_item = self.blendshape_list.item(row, 0)
        if not name_item:
            return
            
        selected_blendshape = name_item.text()
        
        # Get all blendshapes and current exclusions
        blendshapes = self.data_manager.get_module_blendshapes()
        exclusions = self.data_manager.get_module_exclusions()
        
        current_exclusions = exclusions.get(selected_blendshape, [])
        
        # Update exclusion column for all rows to show checkboxes relative to selected blendshape
        for check_row in range(self.blendshape_list.rowCount()):
            check_name_item = self.blendshape_list.item(check_row, 0)
            if not check_name_item:
                continue
                
            check_blendshape = check_name_item.text()
            
            if check_blendshape == selected_blendshape:
                # Selected blendshape - show as "SELECTED"
                selected_item = QtWidgets.QTableWidgetItem("SELECTED")
                selected_item.setFlags(selected_item.flags() & ~QtCore.Qt.ItemIsEditable)
                selected_item.setBackground(QtCore.Qt.yellow)
                self.blendshape_list.setItem(check_row, 2, selected_item)
            else:
                # Other blendshapes - show checkbox for exclusion
                checkbox = QtWidgets.QCheckBox()
                checkbox.setChecked(check_blendshape in current_exclusions)
                checkbox.stateChanged.connect(
                    lambda state, selected=selected_blendshape, target=check_blendshape: 
                    self.on_exclusion_changed(selected, target, state == QtCore.Qt.Checked)
                )
                
                # Create a widget to center the checkbox
                checkbox_widget = QtWidgets.QWidget()
                checkbox_layout = QtWidgets.QHBoxLayout(checkbox_widget)
                checkbox_layout.addWidget(checkbox)
                checkbox_layout.setAlignment(QtCore.Qt.AlignCenter)
                checkbox_layout.setContentsMargins(0, 0, 0, 0)
                
                self.blendshape_list.setCellWidget(check_row, 2, checkbox_widget)
        
        self.statusBar().showMessage(f"Editing exclusions for: {selected_blendshape}", 3000)
    
    def on_exclusion_changed(self, selected_blendshape: str, target_blendshape: str, is_excluded: bool):
        """Handle exclusion checkbox change"""
        success, message = self.data_manager.set_blendshape_exclusion(selected_blendshape, target_blendshape, is_excluded)
        
        if success:
            if is_excluded:
                self.statusBar().showMessage(f"Added exclusion: {selected_blendshape} excludes {target_blendshape}", 2000)
            else:
                self.statusBar().showMessage(f"Removed exclusion: {selected_blendshape} no longer excludes {target_blendshape}", 2000)
        else:
            self.statusBar().showMessage(f"Failed to update exclusion: {message}", 5000)
    
    def remove_module_blendshape(self, blendshape_name: str):
        """Remove blendshape from current module"""
        # Confirm removal
        result = QtWidgets.QMessageBox.question(
            self,
            "Remove Blendshape",
            f"Remove blendshape '{blendshape_name}' from module?\n\nThis will also remove any exclusions involving this blendshape.",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if result == QtWidgets.QMessageBox.Yes:
            success, message = self.data_manager.remove_blendshape(blendshape_name)
            
            if success:
                self.load_module_blendshapes()  # Refresh the list
                self.statusBar().showMessage(f"Removed blendshape: {blendshape_name}", 3000)
            else:
                QtWidgets.QMessageBox.warning(self, "Remove Blendshape Failed", message)
    
    def load_module_in_viewport(self):
        """Load current module as USD proxy shape in viewport"""
        current_module = self.data_manager.get_current_module()
        if not current_module:
            self.statusBar().showMessage("No module selected to load", 3000)
            return
        
        self.statusBar().showMessage(f"Loading {current_module} in viewport...")
        success, message = self.data_manager.load_geometry_to_scene(current_module)
        
        if success:
            self.statusBar().showMessage(f"Loaded {current_module} in viewport", 3000)
        else:
            self.statusBar().showMessage(f"Failed to load in viewport: {message}", 5000)
            QtWidgets.QMessageBox.warning(self, "Viewport Load Failed", f"Failed to load module in viewport:\n\n{message}")
    
    def on_module_name_changed(self):
        """Handle module name change"""
        if not self.data_manager.get_current_module():
            return
            
        new_name = self.module_name_edit.text().strip()
        if not new_name:
            return
        
        # Convert spaces to underscores for file naming
        new_name = new_name.replace(' ', '_')
        
        current_module = self.data_manager.get_current_module()
        if new_name == current_module:
            return  # No change
        
        # TODO: Implement module renaming
        # This would involve:
        # 1. Renaming the USD file
        # 2. Updating group whitelists 
        # 3. Moving file if type changed
        # 4. Updating internal references
        
        self.statusBar().showMessage("Module renaming not yet implemented", 3000)
        
        # Reset to current name for now
        self.module_name_edit.setText(current_module)
    
    def on_module_type_changed(self, new_type: str):
        """Handle module type change"""
        if not self.data_manager.get_current_module():
            return
            
        current_module = self.data_manager.get_current_module()
        
        # Get current module info
        try:
            module_info = self.data_manager.module_manager.modules.get(current_module)
            if not module_info:
                return
            
            current_type = module_info.module_type
            if new_type == current_type:
                return  # No change
            
            # TODO: Implement module type change
            # This would involve:
            # 1. Moving USD file to new type directory
            # 2. Updating module structure in USD
            # 3. Handling alpha blacklist changes
            
            self.statusBar().showMessage("Module type changing not yet implemented", 3000)
            
            # Reset to current type for now
            type_index = self.module_type_combo.findText(current_type)
            if type_index >= 0:
                self.module_type_combo.setCurrentIndex(type_index)
                
        except Exception as e:
            self.statusBar().showMessage(f"Error handling type change: {e}", 5000)
    
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
        if not self.data_manager.get_current_group():
            QtWidgets.QMessageBox.warning(
                self, 
                "No Group Selected", 
                "Please select a group before creating modules."
            )
            return
        
        # Create dialog for module creation
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Create New Module")
        dialog.setModal(True)
        dialog.resize(400, 200)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        # Module name
        name_layout = QtWidgets.QHBoxLayout()
        name_layout.addWidget(QtWidgets.QLabel("Module Name:"))
        name_edit = QtWidgets.QLineEdit()
        name_layout.addWidget(name_edit)
        layout.addLayout(name_layout)
        
        # Module type
        type_layout = QtWidgets.QHBoxLayout()
        type_layout.addWidget(QtWidgets.QLabel("Module Type:"))
        type_combo = QtWidgets.QComboBox()
        type_combo.addItems(["scalp", "crown", "tail", "bang"])
        type_layout.addWidget(type_combo)
        layout.addLayout(type_layout)
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        create_btn = QtWidgets.QPushButton("Create")
        cancel_btn = QtWidgets.QPushButton("Cancel")
        
        create_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        
        button_layout.addWidget(create_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        # Show dialog
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            module_name = name_edit.text().strip()
            module_type = type_combo.currentText()
            
            if not module_name:
                QtWidgets.QMessageBox.warning(self, "Invalid Name", "Please enter a module name.")
                return
            
            # Create module using data manager
            self.statusBar().showMessage(f"Creating module: {module_name}...")
            success, message = self.data_manager.create_module(module_name, module_type)
            
            if success:
                self.statusBar().showMessage(f"Created module: {module_name}", 3000)
                # Refresh modules list and select the new module
                self.load_modules()
                
                # Find and select the new module
                for row in range(self.module_list.rowCount()):
                    name_item = self.module_list.item(row, 1)  # Name is now in column 1
                    if name_item and name_item.text() == module_name:
                        self.module_list.selectRow(row)
                        break
            else:
                self.statusBar().showMessage(f"Failed to create module: {message}", 5000)
                QtWidgets.QMessageBox.warning(self, "Create Module Failed", f"Failed to create module '{module_name}':\n\n{message}")
    
    def remove_module(self):
        """Remove the currently selected module"""
        current_module = self.data_manager.get_current_module()
        if not current_module:
            return
        
        # Confirm deletion
        reply = QtWidgets.QMessageBox.question(
            self,
            "Remove Module",
            f"Remove module '{current_module}' permanently?\n\nThis will:\n- Delete the USD file\n- Remove from group whitelist\n- Remove all references\n\nThis action cannot be undone.",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            # TODO: Implement module deletion
            # This would involve:
            # 1. Removing USD file from disk
            # 2. Removing from group whitelist
            # 3. Cleaning up any references
            # 4. Refreshing UI
            
            self.statusBar().showMessage("Module deletion not yet implemented", 3000)
            QtWidgets.QMessageBox.information(
                self,
                "Not Implemented",
                "Module deletion functionality will be implemented in a future update."
            )
    
    def add_blendshape(self):
        """Add blendshape to current module"""
        if not self.data_manager.get_current_module():
            QtWidgets.QMessageBox.warning(
                self, 
                "No Module Selected", 
                "Please select a module before adding blendshapes."
            )
            return
        
        # Get selected object in Maya scene
        import maya.cmds as cmds
        selected = cmds.ls(selection=True)
        
        if not selected:
            QtWidgets.QMessageBox.warning(
                self, 
                "No Selection", 
                "Please select a mesh object in the Maya scene to use as a blendshape."
            )
            return
        
        maya_object = selected[0]
        
        # Get blendshape name from user (optional)
        blendshape_name, ok = QtWidgets.QInputDialog.getText(
            self,
            "Add Blendshape",
            f"Enter blendshape name for '{maya_object}':\n(Leave empty to use object name)",
            QtWidgets.QLineEdit.Normal,
            maya_object
        )
        
        if not ok:
            return
        
        # Use object name if no name provided
        if not blendshape_name.strip():
            blendshape_name = maya_object
        else:
            blendshape_name = blendshape_name.strip()
        
        # Add blendshape using data manager
        self.statusBar().showMessage(f"Adding blendshape: {blendshape_name}...")
        success, message = self.data_manager.add_blendshape_from_scene(maya_object, blendshape_name)
        
        if success:
            self.statusBar().showMessage(f"Added blendshape: {blendshape_name}", 3000)
            # Refresh blendshapes list
            self.load_module_blendshapes()
        else:
            self.statusBar().showMessage(f"Failed to add blendshape: {message}", 5000)
            QtWidgets.QMessageBox.warning(self, "Add Blendshape Failed", f"Failed to add blendshape '{blendshape_name}':\n\n{message}")
    
    def replace_base_mesh(self):
        """Replace base mesh for current module"""
        if not self.data_manager.get_current_module():
            QtWidgets.QMessageBox.warning(
                self, 
                "No Module Selected", 
                "Please select a module before replacing geometry."
            )
            return
        
        # Get selected object in Maya scene
        import maya.cmds as cmds
        selected = cmds.ls(selection=True)
        
        if not selected:
            QtWidgets.QMessageBox.warning(
                self, 
                "No Selection", 
                "Please select a mesh object in the Maya scene to use as base geometry."
            )
            return
        
        maya_object = selected[0]
        
        # Confirm replacement
        result = QtWidgets.QMessageBox.question(
            self,
            "Replace Base Mesh",
            f"Replace base geometry with '{maya_object}'?\n\nThis will overwrite the existing geometry in the module.",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if result == QtWidgets.QMessageBox.Yes:
            # Import geometry using data manager
            self.statusBar().showMessage(f"Importing geometry: {maya_object}...")
            success, message = self.data_manager.import_geometry_from_scene(maya_object)
            
            if success:
                self.statusBar().showMessage(f"Imported geometry: {maya_object}", 3000)
                # Refresh module data to update geometry status
                self.load_module_edit_data()
            else:
                self.statusBar().showMessage(f"Failed to import geometry: {message}", 5000)
                QtWidgets.QMessageBox.warning(self, "Import Geometry Failed", f"Failed to import geometry from '{maya_object}':\n\n{message}")
    
    def load_geometry_to_scene(self):
        """Load current module's geometry into Maya viewport (legacy method - redirects to viewport loading)"""
        self.load_module_in_viewport()
    
    def save_module(self):
        """Save current module to USD"""
        if not self.data_manager.get_current_module():
            self.statusBar().showMessage("No module selected to save", 3000)
            return
        
        if not self.data_manager.has_unsaved_changes('modules'):
            self.statusBar().showMessage("No changes to save", 2000)
            return
        
        self.statusBar().showMessage("Saving module...")
        success, message = self.data_manager.save_current_module()
        
        if success:
            self.statusBar().showMessage("Module saved successfully", 3000)
        else:
            self.statusBar().showMessage(f"Save failed: {message}", 5000)
            QtWidgets.QMessageBox.warning(self, "Save Failed", f"Failed to save module:\n\n{message}")
    
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