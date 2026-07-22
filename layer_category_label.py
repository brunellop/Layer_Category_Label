import json
from pathlib import Path
from qgis.core import (
    QgsProject, QgsVectorLayer, QgsCategorizedSymbolRenderer,
    Qgis, QgsMessageLog
)
from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import QObject, QTimer


class LayerCategoryLabel(QObject):

    SEPARATOR = " ● ["

    def __init__(self, iface: QgisInterface):
        super().__init__()
        self.iface = iface
        self.project = QgsProject.instance()
        self.layer_original_names = {}
        self.check_timer = None
        self.processing = False
        self.connected_layer_ids = set()

        plugin_dir = Path(__file__).parent
        self.config_file = plugin_dir / ".layer_names_backup.json"

    # ------------------------------------------------------------------
    # Entry point richiesto da QGIS
    # ------------------------------------------------------------------
    def initGui(self):
        self.layer_original_names = self.load_stored_names()

        self.project.layerWasAdded.connect(self.on_layer_added)
        self.project.layerRemoved.connect(self.on_layer_removed)
        self.project.layersWillBeRemoved.connect(self.on_layers_will_be_removed)
        self.project.readProject.connect(self.on_project_loaded)

        self.check_timer = QTimer(self)
        self.check_timer.setSingleShot(True)
        self.check_timer.timeout.connect(self.check_all_layers)
        self.check_timer.start(500)

    def unload(self):
        if self.check_timer:
            self.check_timer.stop()

        signals_slots = [
            (self.project.layerWasAdded, self.on_layer_added),
            (self.project.layerRemoved, self.on_layer_removed),
            (self.project.layersWillBeRemoved, self.on_layers_will_be_removed),
            (self.project.readProject, self.on_project_loaded),
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

    # ------------------------------------------------------------------
    # Persistenza nomi originali (evita accumulo del suffisso)
    # ------------------------------------------------------------------
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
        if self.SEPARATOR in current_name:
            return current_name.split(self.SEPARATOR)[0]
        return current_name

    # ------------------------------------------------------------------
    # Logica principale
    # ------------------------------------------------------------------
    def on_project_loaded(self):
        self.check_timer.start(500)

    def check_all_layers(self):
        if self.processing:
            return
        self.processing = True
        try:
            for layer in self.project.mapLayers().values():
                self.connect_layer_signals(layer)
                self.update_layer_label(layer)
        finally:
            self.processing = False
        self.save_stored_names()

    def connect_layer_signals(self, layer):
        if not isinstance(layer, QgsVectorLayer):
            return
        if layer.id() in self.connected_layer_ids:
            return
        try:
            layer.rendererChanged.connect(lambda target_layer=layer: self.update_layer_label(target_layer))
            self.connected_layer_ids.add(layer.id())
        except (TypeError, RuntimeError):
            pass

    def on_layer_added(self, layer):
        if not isinstance(layer, QgsVectorLayer):
            return
        self.connect_layer_signals(layer)
        QTimer.singleShot(300, lambda: self.update_layer_label(layer))

    def on_layer_removed(self, layer_id):
        self.connected_layer_ids.discard(layer_id)
        if layer_id in self.layer_original_names:
            del self.layer_original_names[layer_id]
            self.save_stored_names()

    def on_layers_will_be_removed(self, layer_ids):
        changed = False
        for layer_id in layer_ids:
            self.connected_layer_ids.discard(layer_id)
            if layer_id in self.layer_original_names:
                del self.layer_original_names[layer_id]
                changed = True
        if changed:
            self.save_stored_names()

    def update_layer_label(self, layer):
        if not isinstance(layer, QgsVectorLayer):
            return

        layer_id = layer.id()
        current_name = layer.name()
        original_name = self.extract_original_name(current_name)

        if layer_id not in self.layer_original_names:
            self.layer_original_names[layer_id] = original_name

        renderer = layer.renderer()
        if isinstance(renderer, QgsCategorizedSymbolRenderer):
            field_name = renderer.classAttribute()
            new_name = f"{self.layer_original_names[layer_id]}{self.SEPARATOR}{field_name}]"
        else:
            new_name = self.layer_original_names[layer_id]

        if new_name != current_name:
            layer.setName(new_name)
