import json
import os
from pathlib import Path
from qgis.core import QgsProject, QgsVectorLayer
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
        
        # File di configurazione per persistenza
        plugin_dir = Path(__file__).parent
        self.config_file = plugin_dir / ".layer_names_backup.json"
    
    def load_stored_names(self):
        """Carica i nomi originali salvati precedentemente"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def save_stored_names(self):
        """Salva i nomi originali su disco"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.layer_original_names, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def extract_original_name(self, current_name: str) -> str:
        """Estrae il nome originale rimuovendo il marker ● e tutto dopo"""
        # Se il nome contiene ●, prende solo la parte prima
        if " ●" in current_name:
            return current_name.split(" ●")[0].strip()
        return current_name
    
    def initGui(self):
        """Inizializza il plugin quando viene abilitato"""
        # Carica i nomi originali salvati
        stored = self.load_stored_names()
        
        # Per ogni layer che esiste già, determina il nome originale
        for layer_id, layer in self.project.mapLayers().items():
            if isinstance(layer, QgsVectorLayer):
                # Priorità: nome salvato > nome estratto da layer corrente
                if layer_id in stored:
                    self.layer_original_names[layer_id] = stored[layer_id]
                else:
                    self.layer_original_names[layer_id] = self.extract_original_name(layer.name())
        
        # Connessioni ai segnali
        self.project.layerWasAdded.connect(self.on_layer_added)
        self.project.layerRemoved.connect(self.on_layer_removed)
        self.project.layersWillBeRemoved.connect(self.on_layers_will_be_removed)
        
        # Salva i nomi non appena il plugin si carica
        self.save_stored_names()
        
        # Timer per monitorare simbolizzazione
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_all_layers)
        self.check_timer.start(500)  # Controlla ogni 500ms
    
    def on_layer_added(self, layer):
        """Quando un layer è aggiunto, salvane il nome originale"""
        if isinstance(layer, QgsVectorLayer):
            layer_id = layer.id()
            # Estrai il nome originale dal nome corrente (potrebbe già avere il marker)
            original = self.extract_original_name(layer.name())
            self.layer_original_names[layer_id] = original
            self.save_stored_names()
            self.update_layer_name(layer)
    
    def on_layer_removed(self, layer_id):
        """Quando un layer è rimosso, ripulisci dai dizionari"""
        if layer_id in self.layer_original_names:
            del self.layer_original_names[layer_id]
            self.save_stored_names()
    
    def on_layers_will_be_removed(self, layer_ids):
        """Preparati alla rimozione di più layer"""
        for layer_id in layer_ids:
            if layer_id in self.layer_original_names:
                del self.layer_original_names[layer_id]
        self.save_stored_names()
    
    def check_all_layers(self):
        """Controlla periodicamente tutti i layer per cambiamenti di simbolizzazione"""
        if self.processing:
            return
        
        self.processing = True
        try:
            for layer in self.project.mapLayers().values():
                if isinstance(layer, QgsVectorLayer):
                    self.update_layer_name(layer)
        finally:
            self.processing = False
    
    def update_layer_name(self, layer: QgsVectorLayer):
        """Aggiorna il nome del layer nel pannello Layers"""
        layer_id = layer.id()
        
        # Se non conosco il nome originale, estrailo
        if layer_id not in self.layer_original_names:
            self.layer_original_names[layer_id] = self.extract_original_name(layer.name())
            self.save_stored_names()
        
        original_name = self.layer_original_names[layer_id]
        
        # Controlla se il layer è categorizzato
        renderer = layer.renderer()
        
        if renderer and hasattr(renderer, 'classAttribute'):
            category_field = renderer.classAttribute()
            if category_field:
                new_name = f"{original_name} ● [{category_field}]"
                if layer.name() != new_name:
                    layer.setName(new_name)
            else:
                # Categorizzazione senza campo
                if layer.name() != original_name:
                    layer.setName(original_name)
        else:
            # Non è categorizzato, ripristina il nome originale
            if layer.name() != original_name:
                layer.setName(original_name)
    
    def unload(self):
        """Cleanup quando il plugin viene disabilitato"""
        if self.check_timer:
            self.check_timer.stop()
        
        try:
            self.project.layerWasAdded.disconnect(self.on_layer_added)
        except:
            pass
        try:
            self.project.layerRemoved.disconnect(self.on_layer_removed)
        except:
            pass
        try:
            self.project.layersWillBeRemoved.disconnect(self.on_layers_will_be_removed)
        except:
            pass
        
        # Ripristina i nomi originali di tutti i layer
        for layer_id, original_name in self.layer_original_names.items():
            layer = self.project.mapLayer(layer_id)
            if layer and layer.name() != original_name:
                layer.setName(original_name)
