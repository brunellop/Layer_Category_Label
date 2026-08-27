import json
from functools import partial
from pathlib import Path
from qgis.core import (
    QgsProject, QgsVectorLayer,
    QgsCategorizedSymbolRenderer, QgsGraduatedSymbolRenderer, QgsRuleBasedRenderer,
    Qgis, QgsMessageLog, QgsSettings
)
from qgis.gui import QgisInterface
from qgis.PyQt.QtCore import QObject, QTimer
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction


class LayerCategoryLabel(QObject):

    SEPARATOR = " ● ["
    RULES_LABEL = "Regole"
    SETTINGS_KEY = "LayerCategoryLabel/enabled"

    def __init__(self, iface: QgisInterface):
        super().__init__()
        self.iface = iface
        self.project = QgsProject.instance()
        self.layer_original_names = {}
        self.check_timer = None
        self.processing = False
        self.enabled = True
        self.action = None
        self.connected_layer_ids = set()
        self.layer_signal_slots = {}  # layer_id -> partial callable (riferimento forte)

        plugin_dir = Path(__file__).parent
        self.config_file = plugin_dir / ".layer_names_backup.json"
        self.icon_path = str(plugin_dir / "icons" / "icon.png")

    # ------------------------------------------------------------------
    # Entry point richiesto da QGIS
    # ------------------------------------------------------------------
    def initGui(self):
        self.layer_original_names = self.load_stored_names()

        # Stato ON/OFF persistente tra sessioni QGIS
        self.enabled = QgsSettings().value(self.SETTINGS_KEY, True, type=bool)

        self.action = QAction(QIcon(self.icon_path), "Layer Category Label", self.iface.mainWindow())
        self.action.setCheckable(True)
        self.action.setChecked(self.enabled)
        self.action.setToolTip("Attiva/disattiva Layer Category Label")
        self.action.toggled.connect(self.on_toggle)
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("Layer Category Label", self.action)

        self.project.readProject.connect(self.on_project_loaded)

        self.check_timer = QTimer(self)
        self.check_timer.setSingleShot(True)
        self.check_timer.timeout.connect(self.check_all_layers)

        if self.enabled:
            self.activate()

    def unload(self):
        self.deactivate(restore_names=True)

        try:
            self.project.readProject.disconnect(self.on_project_loaded)
        except (TypeError, RuntimeError):
            pass

        if self.action:
            self.iface.removePluginMenu("Layer Category Label", self.action)
            self.iface.removeToolBarIcon(self.action)
            self.action = None

    # ------------------------------------------------------------------
    # Toggle ON/OFF
    # ------------------------------------------------------------------
    def on_toggle(self, checked):
        self.enabled = checked
        QgsSettings().setValue(self.SETTINGS_KEY, checked)
        if checked:
            self.activate()
        else:
            self.deactivate(restore_names=True)

    def activate(self):
        self.project.layerWasAdded.connect(self.on_layer_added)
        self.project.layerRemoved.connect(self.on_layer_removed)
        self.project.layersWillBeRemoved.connect(self.on_layers_will_be_removed)
        self.check_timer.start(500)

    def deactivate(self, restore_names=False):
        if self.check_timer:
            self.check_timer.stop()

        signals_slots = [
            (self.project.layerWasAdded, self.on_layer_added),
            (self.project.layerRemoved, self.on_layer_removed),
            (self.project.layersWillBeRemoved, self.on_layers_will_be_removed),
        ]
        for signal, slot in signals_slots:
            try:
                signal.disconnect(slot)
            except (TypeError, RuntimeError):
                pass

        for layer_id, slot in list(self.layer_signal_slots.items()):
            layer = self.project.mapLayer(layer_id)
            if layer:
                try:
                    layer.rendererChanged.disconnect(slot)
                except (TypeError, RuntimeError):
                    pass
        self.layer_signal_slots.clear()
        self.connected_layer_ids.clear()

        if restore_names:
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
        if self.enabled:
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
        layer_id = layer.id()

        # Se esiste già una connessione precedente, la rimuoviamo prima di
        # ricrearla: evita sia i duplicati sia il rischio di restare con
        # una connessione "morta" senza più ritentare (bug della v1.0.7).
        old_slot = self.layer_signal_slots.get(layer_id)
        if old_slot is not None:
            try:
                layer.rendererChanged.disconnect(old_slot)
            except (TypeError, RuntimeError):
                pass

        slot = partial(self.update_layer_label, layer)
        try:
            layer.rendererChanged.connect(slot)
            self.layer_signal_slots[layer_id] = slot  # riferimento forte: evita garbage collection
            self.connected_layer_ids.add(layer_id)
        except (TypeError, RuntimeError) as e:
            QgsMessageLog.logMessage(
                f"Impossibile connettere il segnale per layer '{layer.name()}': {e}",
                "LayerCategoryLabel", Qgis.Warning
            )

    def on_layer_added(self, layer):
        if not isinstance(layer, QgsVectorLayer):
            return
        self.connect_layer_signals(layer)
        QTimer.singleShot(300, lambda: self.update_layer_label(layer))

    def on_layer_removed(self, layer_id):
        self.connected_layer_ids.discard(layer_id)
        self.layer_signal_slots.pop(layer_id, None)
        if layer_id in self.layer_original_names:
            del self.layer_original_names[layer_id]
            self.save_stored_names()

    def on_layers_will_be_removed(self, layer_ids):
        changed = False
        for layer_id in layer_ids:
            self.connected_layer_ids.discard(layer_id)
            self.layer_signal_slots.pop(layer_id, None)
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

        base_name = self.layer_original_names[layer_id]
        renderer = layer.renderer()

        if isinstance(renderer, (QgsCategorizedSymbolRenderer, QgsGraduatedSymbolRenderer)):
            field_name = renderer.classAttribute()
            new_name = f"{base_name}{self.SEPARATOR}{field_name}]"
        elif isinstance(renderer, QgsRuleBasedRenderer):
            new_name = f"{base_name}{self.SEPARATOR}{self.RULES_LABEL}]"
        else:
            new_name = base_name

        if new_name != current_name:
            layer.setName(new_name)
