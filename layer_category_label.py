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
    
    def initGui(self):
        """Inizializza il plugin quando viene abilitato"""
        # Connessioni ai segnali
        self.project.layerWasAdded.connect(self.on_layer_added)
        self.project.layerRemoved.connect(self.on_layer_removed)
        self.project.layersWillBeRemoved.connect(self.on_layers_will_be_removed)
        
        # Timer per monitorare simbolizzazione
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.check_all_layers)
        self.check_timer.start(500)  # Controlla ogni 500ms
        
    def on_layer_added(self, layer):
        """Quando un layer è aggiunto, salvane il nome originale"""
        if isinstance(layer, QgsVectorLayer):
            layer_id = layer.id()
            self.layer_original_names[layer_id] = layer.name()
            self.update_layer_name(layer)
    
    def on_layer_removed(self, layer_id):
        """Quando un layer è rimosso, ripulisci dai dizionari"""
        if layer_id in self.layer_original_names:
            del self.layer_original_names[layer_id]
    
    def on_layers_will_be_removed(self, layer_ids):
        """Preparati alla rimozione di più layer"""
        for layer_id in layer_ids:
            if layer_id in self.layer_original_names:
                del self.layer_original_names[layer_id]
    
    def check_all_layers(self):
        """Controlla periodicamente tutti i layer per cambiamenti di simbolizzazione"""
        for layer in self.project.mapLayers().values():
            if isinstance(layer, QgsVectorLayer):
                self.update_layer_name(layer)
    
    def update_layer_name(self, layer: QgsVectorLayer):
        """Aggiorna il nome del layer nel pannello Layers"""
        layer_id = layer.id()
        
        # Salva il nome originale se non l'hai ancora fatto
        if layer_id not in self.layer_original_names:
            self.layer_original_names[layer_id] = layer.name()
        
        original_name = self.layer_original_names[layer_id]
        
        # Controlla se il layer è categorizzato
        renderer = layer.renderer()
        
        if renderer and hasattr(renderer, 'classAttribute'):
            # È categorizzato
            category_field = renderer.classAttribute()
            if category_field:
                new_name = f"{original_name} ● [{category_field}]"
                if layer.name() != new_name:
                    layer.setName(new_name)
            else:
                # Categorizzazione senza campo (strano, ma gestisci)
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
