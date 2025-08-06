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
        self.resize(1000, 800)
        
        # Make window stay on top but not always
        self.setWindowFlags(QtCore.Qt.Window)
        
        self.setup_ui()
        self.setup_shortcuts()
        
        # Initialize with first refresh
        self.refresh_data()
    
    def setup_ui(self):
        """Set up the main UI layout"""
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
        
        hotkey_label = QtWidgets.QLabel("Shortcuts: Tab=Switch Tabs | F5=Refresh | Ctrl+R=Regen Timeline | Ctrl+S=Save")
        hotkey_label.setStyleSheet("font-size: 11px; color: #666;")
        
        hotkey_layout.addWidget(hotkey_label)
        hotkey_layout.addStretch()
        
        parent_layout.addWidget(hotkey_frame)
    
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
        self.module_list.currentRowChanged.connect(self.on_module_selected)
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
        self.style_list.currentRowChanged.connect(self.on_style_selected)
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
    
    def on_module_selected(self, row):
        """Handle module selection change"""
        if row >= 0:
            self.module_edit_frame.setEnabled(True)
            # TODO: Load module data into edit form
    
    def on_style_selected(self, row):
        """Handle style selection change"""
        if row >= 0:
            self.style_edit_frame.setEnabled(True)
            # TODO: Load style data and timeline
    
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