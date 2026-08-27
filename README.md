# Layer Category Label

Automatically displays the classification field (or "Rules") in the layer name for Categorized, Graduated and Rule-based symbology.

## About This Plugin

This plugin is an **enhancement of QGIS core functionality**. QGIS 3.44 LTR includes the option "Display classification attributes in layer titles" (Settings → Options → Map & Legend), but it only reveals classification field names when you expand the layer arrow in the Layers panel. This plugin makes that information **immediately visible in the layer name itself**, saving clicks and making thematic layers instantly identifiable.

## Features

* Real-time monitoring of vector layers
* Supports three symbology types:
  * **Categorized** → `LayerName ● [FieldName]`
  * **Graduated** → `LayerName ● [FieldName]`
  * **Rule-based** → `LayerName ● [Regole]`
* The bullet (●) quickly indicates which layers use one of these symbology types
* When you remove the symbology (back to Single Symbol), the original name is restored
* **Toolbar icon** to enable/disable the plugin at any time, without uninstalling it — your choice is remembered between QGIS sessions
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
3. Apply Categorized, Graduated or Rule-based symbology (right-click on layer → Symbology)
4. You'll see the layer name updated automatically, e.g.: `LayerName ● [ClassificationField]` or `LayerName ● [Regole]`
5. When you remove the symbology, the name returns to the original
6. Click the plugin's toolbar icon to turn it ON/OFF at any time. When OFF, layer names are restored and no longer monitored

## Compatibility

* **QGIS**: 3.44 LTR (and later versions)
* **Python**: 3.9+
* **Operating Systems**: Windows, Linux, macOS

## Author

Paolo Brunello

## License

GPL 2.0 or later

## Changelog

### v1.1.0

* Added support for **Graduated** symbology
* Added support for **Rule-based** symbology (shown as `[Regole]`)
* Added a **toolbar icon** to enable/disable the plugin, with the state remembered between sessions

### v1.0.8

* Fixed a silent signal-loss bug: connections are now self-healing and use `functools.partial` to avoid garbage collection

### v1.0.2 (Initial Release)

* Automatic layer monitoring
* Display categorization field in layer name
* Bullet (●) as visual indicator

## Learn More

For in-depth QGIS tutorials and cartography tips, visit my YouTube channel:
[WebStoryMap - Tutorial QGIS](https://www.youtube.com/WebStoryMap)

---

## 🇮🇹 Istruzioni in Italiano

Visualizza automaticamente nel nome del layer il campo di classificazione (o "Regole") per simbologia Categorizzata, Graduata e Basata su regole.

### Informazioni su questo Plugin

Questo plugin è un **miglioramento della funzionalità core di QGIS**. QGIS 3.44 LTR include l'opzione "Visualizza attributi di classificazione nei titoli del layer" (Impostazioni → Opzioni → Mappa & Legenda), ma mostra queste informazioni solo quando espandi la freccia del layer nel pannello Layer. Questo plugin le rende **immediatamente visibili nel nome del layer stesso**, eliminando clic inutili e rendendo i layer tematici istantaneamente identificabili.

### Funzionalità

* Monitoraggio in tempo reale dei layer vettoriali
* Supporta tre tipi di simbologia:
  * **Categorizzato** → `NomeLayer ● [NomeCampo]`
  * **Graduato** → `NomeLayer ● [NomeCampo]`
  * **Tramite regole** → `NomeLayer ● [Regole]`
* Il pallino (●) indica a colpo d'occhio quali layer usano una di queste simbologie
* Quando rimuovi la simbologia (torni a Simbolo unico), il nome originale viene ripristinato
* **Icona in toolbar** per attivare/disattivare il plugin in qualsiasi momento, senza disinstallarlo — la scelta viene ricordata tra una sessione di QGIS e l'altra
* Funziona automaticamente, nessuna configurazione richiesta

### Installazione

Scarica il file `Layer_Category_Label.zip` e installalo tramite QGIS:

`Plugin → Gestisci e installa plugin → Installa da ZIP`

Seleziona il file ZIP e conferma l'installazione. Al termine, attiva il plugin dalla sezione **Plugin installati**.

### Utilizzo

Il plugin funziona automaticamente:

1. Attivalo dal Plugin Manager
2. Aggiungi un layer vettoriale
3. Applica una simbologia Categorizzata, Graduata o Tramite regole (clic destro sul layer → Simbolizzazione)
4. Vedrai il nome del layer aggiornato automaticamente, es.: `NomeLayer ● [CampoClassificazione]` oppure `NomeLayer ● [Regole]`
5. Quando rimuovi la simbologia, il nome ritorna a quello originale
6. Clicca l'icona del plugin in toolbar per attivarlo/disattivarlo in qualsiasi momento. Quando è OFF, i nomi vengono ripristinati e non più monitorati

### Compatibilità

* **QGIS**: 3.44 LTR (e versioni successive)
* **Python**: 3.9+
* **Sistemi operativi**: Windows, Linux, macOS

### Changelog

#### v1.1.0

* Aggiunto supporto per simbologia **Graduata**
* Aggiunto supporto per simbologia **Tramite regole** (mostrata come `[Regole]`)
* Aggiunta **icona in toolbar** per attivare/disattivare il plugin, con stato ricordato tra le sessioni

#### v1.0.8

* Corretto un bug di perdita silenziosa dei segnali: le connessioni ora sono self-healing e usano `functools.partial` per evitare il garbage collection

### Approfondisci

Tutorial su QGIS disponibili sul canale YouTube:
[WebStoryMap - Tutorial QGIS](https://www.youtube.com/WebStoryMap)

### Autore

Paolo Brunello

### Licenza

GPL 2.0 o successive
