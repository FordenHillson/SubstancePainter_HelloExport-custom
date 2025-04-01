from PySide6 import QtWidgets, QtGui
import substance_painter.ui
import substance_painter.export
import substance_painter.project
import substance_painter.textureset
import os

plugin_widgets = []
output_path = ""
texture_sizes_index = 2
texture_sizes = ["128x128", "256x256", "512x512", "1024x1024", "2048x2048", "4096x4096"]
def textureSize(size):
    if size == "128x128":
        return 7
    elif size == "256x256":
        return 8
    elif size == "512x512":
        return 9
    elif size == "1024x1024":
        return 10
    elif size == "2048x2048":
        return 11
    elif size == "4096x4096":
        return 12

def export_enfution(output_path, maps, selected_size):
    saveData(output_path)
    if not substance_painter.project.is_open():
        return

    stack = substance_painter.textureset.get_active_stack()
    material = stack.material()

    export_preset = substance_painter.resource.ResourceID(
        context="your_assets",
        name="Enfusion_template"
    )
    resolution = material.get_resolution()

    # Use the provided output path or the project file path
    if output_path:
        Path = output_path
    else:
        Path = substance_painter.project.file_path()
        Path = os.path.dirname(Path) + "/"

    #project_output_directory = substance_painter.project.get_output_path()

    config = {
        "exportShaderParams": False,
        "exportPath": Path,
        "exportList": [{"rootPath": str(stack),
            "filter" : {
            "outputMaps" : [maps]
            }}],
        "exportPresets": [{"name": "default", "maps": []}],  # Specify the desired map name (e.g., "Diffuse")
        "defaultExportPreset": export_preset.url(),
        "exportParameters": [
            {
                "parameters": {"paddingAlgorithm": "infinite", "sizeLog2":textureSize(selected_size)}
            }
        ]
    }
    export_list = substance_painter.export.list_project_textures(config)
    print(export_list)
    substance_painter.export.export_project_textures(config)
    
def export_single():
        # get name of TextureSet
        stack = substance_painter.textureset.get_active_stack()
        # get uid of selected nodes
        selected_nodes = substance_painter.layerstack.get_selected_nodes(stack)
        
        # Check if any nodes are selected
        if not selected_nodes:
            show_message_box("No layer is selected. Please select a layer to export.")
            return
            
        rootLayer = substance_painter.layerstack.get_root_layer_nodes(stack)
        # get name from uid
        groupLayers = substance_painter.layerstack.Node.get_name(selected_nodes[0])
        
        # Dictionary mapping layer names to their corresponding texture set identifiers
        layer_map = {
            "Global": "$textureSet_GLOBAL_MASK",
            "VFX": "$textureSet_VFX",
            "MCR": "$textureSet_MCR",
            "NMO": "$textureSet_NMO"
        }
        
        # Check if the selected layer is one of the supported types
        if groupLayers in layer_map:
            # Helper function to handle visibility
            def set_layer_visibility(node, visible):
                if substance_painter.layerstack.Node.is_visible(node) != visible:
                    substance_painter.layerstack.Node.set_visible(node, visible)
            
            # Hide all layers
            for x in rootLayer:
                set_layer_visibility(x, False)
                
            # Show only the selected layer
            set_layer_visibility(selected_nodes[0], True)
            
            # Export the texture
            export_enfution(output_path_input.text(), layer_map[groupLayers], size_dropdown.currentText())
        else:
            show_message_box(f"Selected stack '{groupLayers}' does not match Global, VFX, MCR or NMO")

def export_all():
        # get name of TextureSet
        stack = substance_painter.textureset.get_active_stack()
        # get root layer nodes
        rootLayer = substance_painter.layerstack.get_root_layer_nodes(stack)
        
        # Dictionary mapping layer names to their corresponding texture set identifiers
        layer_map = {
            "Global": "$textureSet_GLOBAL_MASK",
            "VFX": "$textureSet_VFX",
            "MCR": "$textureSet_MCR",
            "NMO": "$textureSet_NMO"
        }
        
        # Helper function to set visibility
        def set_visible_and_export(node, is_visible):
            substance_painter.layerstack.Node.set_visible(node, is_visible)
            
        # First hide all layers
        for node in rootLayer:
            set_visible_and_export(node, False)
            
        # Then process each layer one by one
        for node in rootLayer:
            groupNameLayer = substance_painter.layerstack.Node.get_name(node)
            
            if groupNameLayer in layer_map:
                print(f"Exporting {groupNameLayer}")
                set_visible_and_export(node, True)
                export_enfution(output_path_input.text(), layer_map[groupNameLayer], size_dropdown.currentText())
                set_visible_and_export(node, False)
            else:
                print(f"Skipping {groupNameLayer} - not in supported layers")
    
def show_message_box(message):
        msg_box = QtWidgets.QMessageBox()
        msg_box.setText(message)
        msg_box.setWindowTitle("Error")
        msg_box.setIcon(QtWidgets.QMessageBox.Warning)
        msg_box.exec_()
    

def logX():
    for shelf in substance_painter.resource.Shelves.all():
        export_presets_dir = f"{shelf.path()}/export-presets"
        #print(shelf)
        if not os.path.isdir(export_presets_dir):
            continue
        for filename in os.listdir(export_presets_dir):
            if not filename.endswith(".spexp"):
                continue
            name = os.path.splitext(filename)[0]
            export_preset_id = substance_painter.resource.ResourceID(context=shelf.name(), name=name)
            export_preset = substance_painter.resource.Resource.retrieve(export_preset_id)[0]
            #print(export_preset.gui_name())
    # my_shelf = substance_painter.resource.Shelf("export") 
    # all_shelf_resources = my_shelf.resources() 
    # print(substance_painter)
    # for resource in all_shelf_resources: 
    #     print(resource.identifier().name) 
    #print("The name of the project is now: '{0}'".format(substance_painter.project.name())) 
    metadata = substance_painter.project.Metadata("PluginSaveData")
    save = ["testsavedata", 2]
    metadata.set("plugin_save_data", save)
    
    print("Save Data", metadata.get("plugin_save_data"))
    

def saveData(path):
    global size_dropdown
    metadata = substance_painter.project.Metadata("PluginSaveData")
    PluginSaveData = [path, size_dropdown.currentIndex()]
    metadata.set("plugin_save_data", PluginSaveData)
    print("Save Data", metadata.get("plugin_save_data"))

def my_callback(*args, **kwargs):
    global output_path, output_path_input, texture_sizes_index
    print(f'Callback: {substance_painter.project.file_path()}')

    metadata = substance_painter.project.Metadata("PluginSaveData")
    PluginSaveData = metadata.get("plugin_save_data")
    output_path = PluginSaveData[0]
    texture_sizes_index = PluginSaveData[1]
    print(PluginSaveData)
    output_path_input.setText(output_path)
    size_dropdown.setCurrentIndex(texture_sizes_index)
    
def saveTriggered(*args, **kwargs):
    print("S A V E")


def start_plugin():
    # Create a docked widget
    dev_label = QtWidgets.QLabel("Dev Tools")
    customExport_label = QtWidgets.QLabel("Custom Export")
    plugin_widget = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout()
    plugin_widget.setLayout(layout)
    plugin_widget.setWindowTitle("Hello Export") 
    
    substance_painter.event.DISPATCHER.connect(substance_painter.event.ProjectOpened, my_callback)
    #substance_painter.event.DISPATCHER.connect(substance_painter.event.ProjectSaved, saveTriggered)
    # Create a dropdown for selecting the texture size
    global size_dropdown
    size_label = QtWidgets.QLabel("Texture Size:")
    size_dropdown = QtWidgets.QComboBox()
    size_dropdown.addItems(texture_sizes)
    
    #size_dropdown.activated.conext(saveData(size_dropdown.currentIndex()))
    
    global output_path_input
    output_path_input = QtWidgets.QLineEdit()
    output_path_input.setPlaceholderText("Output Path")
    output_path_input.setText(output_path)
    output_path_input.textChanged.connect(lambda text = output_path_input.text(): saveData(text))
    

    # Create a button to trigger the export
    bt_export_mask = QtWidgets.QPushButton("Global Mask")
    bt_export_vfx = QtWidgets.QPushButton("VFX")
    bt_export_mcr = QtWidgets.QPushButton("MCR")
    bt_export_nmo = QtWidgets.QPushButton("NMO")

    bt_export_single = QtWidgets.QPushButton("Export Selection")
    bt_export_all = QtWidgets.QPushButton("Export All")
    bt_logX = QtWidgets.QPushButton("LogX")

    # Connect the button to the export_textures function with the output path as an argument
    bt_export_mask.clicked.connect(lambda: export_enfution(output_path_input.text(), "$textureSet_GLOBAL_MASK", size_dropdown.currentText()))
    bt_export_vfx.clicked.connect(lambda: export_enfution(output_path_input.text(), "$textureSet_VFX", size_dropdown.currentText()))
    bt_export_mcr.clicked.connect(lambda: export_enfution(output_path_input.text(), "$textureSet_MCR", size_dropdown.currentText()))
    bt_export_nmo.clicked.connect(lambda: export_enfution(output_path_input.text(), "$textureSet_NMO", size_dropdown.currentText()))

    bt_export_single.clicked.connect(export_single)
    bt_export_all.clicked.connect(export_all)
    bt_logX.clicked.connect(lambda: logX())

    

    # Add the label, input field, and button to the layout
    # layout.addWidget(label)
    layout.addWidget(output_path_input)
    layout.addWidget(size_label)
    layout.addWidget(size_dropdown)
    layout.addWidget(bt_export_mask)
    layout.addWidget(bt_export_vfx)
    layout.addWidget(bt_export_mcr)
    layout.addWidget(bt_export_nmo)

    layout.addWidget(customExport_label)
    layout.addWidget(bt_export_single)
    layout.addWidget(bt_export_all)    
    
    layout.addWidget(dev_label)
    layout.addWidget(bt_logX)   

    # Add the docked widget to the UI
    substance_painter.ui.add_dock_widget(plugin_widget)

    # Store the widget for proper cleanup later when stopping the plugin
    plugin_widgets.append(plugin_widget) 

def close_plugin():
    # Remove all widgets that have been added to the UI
    for widget in plugin_widgets:
        substance_painter.ui.delete_ui_element(widget)
    plugin_widgets.clear()

if __name__ == "__main__":
    start_plugin()