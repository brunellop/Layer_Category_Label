# Layer Category Label

Automatically displays the categorization field in the layer name for categorized symbology.

## About This Plugin

This plugin is an **enhancement of QGIS core functionality**. QGIS 3.44 LTR includes the option "Display classification attributes in layer titles" (Settings → Options → Map & Legend), but it only reveals categorization field names when you expand the layer arrow in the Layers panel. This plugin makes those field names **immediately visible in the layer name itself**, saving clicks and making thematic layers instantly identifiable.

## Features

* Real-time monitoring of vector layers
* When you apply categorization, the layer name becomes: `LayerName ● [FieldName]`
* The bullet (●) quickly indicates which layers are categorized
* When you remove categorization, the original name is restored
* Works automatically, no configuration needed

## Installation

Download the `Layer_Category_Label.zip` file and install it via QGIS:

`Plugins → Manage and Install Plugins → Install from ZIP`

Select the ZIP file and confirm the installation.

After installation, activate the plugin from the **Installed plugins** section.

## Usage

The plugin works automatically:

1. Activate it from the Plugin Manager
2. Add a vector layer
3. Apply categorization (right-click on layer → Symbology)
4. You'll see the layer name updated automatically: `LayerName ● [CategorizationField]`
5. When you remove categorization, the name returns to the original

## Compatibility

* **QGIS**: 3.44 LTR (and later versions)
* **Python**: 3.9+
* **Operating Systems**: Windows, Linux, macOS

## Author

Paolo Brunello

## License

GPL 2.0 or later

## Changelog

### v1.0.2 (Initial Release)

* Automatic layer monitoring
* Display categorization field in layer name
* Bullet (●) as visual indicator

## Learn More

For in-depth QGIS tutorials and cartography tips, visit my YouTube channel:
[WebStoryMap - Tutorial QGIS](https://www.youtube.com/WebStoryMap)

---

## 🇮🇹 Istruzioni in Italiano

Visualizza automaticamente nel nome del layer il campo utilizzato nella simbologia categorizzata.

### Informazioni su questo Plugin

Questo plugin è un **miglioramento della funzionalità core di QGIS**. QGIS 3.44 LTR include l'opzione "Visualizza attributi di classificazione nei titoli del layer" (Impostazioni → Opzioni → Mappa & Legenda), ma mostra i nomi dei campi di categorizzazione solo quando espandi la freccia del layer nel pannello Layer. Questo plugin rende quei nomi di campo **immediatamente visibili nel nome del layer stesso**, eliminando clic inutili e rendendo i layer tematici istantaneamente identificabili.

### Installazione

Scarica il file `Layer_Category_Label.zip` e installalo tramite QGIS:

`Plugin → Gestisci e installa plugin → Installa da ZIP`

Seleziona il file ZIP e conferma l'installazione. Al termine, attiva il plugin dalla sezione **Plugin installati**.

### Utilizzo

Il plugin funziona automaticamente:

1. Attivalo dal Plugin Manager
2. Aggiungi un layer vettoriale
3. Applica una categorizzazione (clic destro sul layer → Simbolizzazione)
4. Vedrai il nome del layer aggiornato automaticamente: `NomeLayer ● [NomeCampo]`
5. Quando rimuovi la categorizzazione, il nome ritorna al nome originale

### Compatibilità

* **QGIS**: 3.44 LTR (e versioni successive)
* **Python**: 3.9+
* **Sistemi operativi**: Windows, Linux, macOS

### Approfondisci

Tutorial su QGIS disponibili sul canale YouTube:
[WebStoryMap - Tutorial QGIS](https://www.youtube.com/WebStoryMap)

### Autore

Paolo Brunello

### Licenza

GPL 2.0 o successive
