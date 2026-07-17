import json
import os
from pathlib import Path
from qgis.core import QgsProject, QgsVectorLayer, Qgis, QgsMessageLog
from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import QObject, QTimer

class LayerCategoryLabel(QObject):
    def __init__(self, iface: QgisInterface):
        super().__init__()
        self.iface = iface
        self.project = QgsProject.instance()
        self.layer_original_names = {}
        self.check_timer = None
        self.processing = False
        
        plugin_dir = Path(__file__).parent
        self.config_file = plugin_dir / ".layer_names_backup.json"
    
    def load_stored_names(self):
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (IOError, ValueError):
                return {}
        return {}
    
    def save_stored_names(self):
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.layer_original_names, f, ensure_ascii=False, indent=2)
        except (IOError, OSError) as e:
            QgsMessageLog.logMessage(f"Impossibile salvare i nomi: {e}", "LayerCategoryLabel", Qgis.Warning)
    
    def extract_original_name(self, current_name: str) -> str:
        if " ● [" in current_name:
            return current_name.split(" ● [")[0]
        return current_name

    def unload(self):
        if self.check_timer:
            self.check_timer.stop()
        
        signals_slots = [
            (self.project.layerWasAdded, self.on_layer_added),
            (self.project.layerRemoved, self.on_layer_removed),
            (self.project.layersWillBeRemoved, self.on_layers_will_be_removed)
        ]
        for signal, slot in signals_slots:
            try:
                signal.disconnect(slot)
            except (TypeError, RuntimeError):
                pass
        
        for layer_id, original_name in self.layer_original_names.items():
            layer = self.project.mapLayer(layer_id)
            if layer and layer.name() != original_name:
                layer.setName(original_name)
