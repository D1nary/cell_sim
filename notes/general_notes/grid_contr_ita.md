# `grid_3d.cpp` file

Il file modella il comportamento di un ambiente cellulare nella griglia 3D e integra la dinamica dei nutrienti e della radiazione.

## Descrizione generale delle funzioni del file
### Gestione delle Cellule (CellList)
- **Creazione e distruzione**: Viene implementata una lista collegata (`CellList`) per gestire i nodi delle cellule (`CellNode`).

- **Aggiunta di cellule**:  
  - Metodo `add` per inserire nuove cellule; le cellule cancerogene vengono aggiunte all'inizio, mentre quelle sane e OAR in coda. Si aggiornano i contatori interni per cellule cancerogene.

- **Pulizia e ordinamento**: La funzione `deleteDeadAndSort()` scorre la lista eliminando le cellule morte e aggiornando i collegamenti per mantenere l’ordine.

### Gestione delle Fonti di Nutrienti (SourceList)

- **Creazione e aggiornamento**: Viene utilizzata una lista per gestire le fonti di nutrienti. Le fonti di nutrimento vengono posizionate casualmente all'interno della griglia.
### Gestione della Griglia 3D (Grid)
- **Allocazione e inizializzazione**: Vengono create tre griglie separate:
    - Una per le liste di cellule in ogni voxel.
    - Una per i livelli di glucosio (inizializzati a `100.0`) e ossigeno (inizializzati a `1000.0`).

- **Posizionamento e aggiornamento delle fonti**: Le fonti di nutrienti vengono posizionate casualmente e aggiornate tramite `fill_sources()`, la quale aggiunge i nutrimenti in corrisopndenza della posizione delle fonti e sposta giornalmente le loro posizioni. Si ha una probabilità di spostamento verso il centro del tumore data dalla condizione `if (rand() % 50000 < CancerCell::count)`.

- **Ciclo delle cellule**: La funzione `cycle_cells()` itera su tutti i voxel avanzando il ciclo delle cellule in base al consumo di nutrienti e alla densità locale. Gestisce la divisione cellulare e la creazione di nuove cellule se le condizioni lo permettono e pulisce le cellule morte dalla lista.

- **Diffusione dei nutrienti**. La funzione `diffuse()` modella la dispersione del glucosio e dell’ossigeno. Ogni voxel trattiene una parte del proprio contenuto, mentre una frazione viene diffusa equamente tra i 26 voxel adiacenti.

- **Irradiazione**: Implementata tramite la funzione `irradiate()` la quale:
    - Calcola il centro del tumore e il raggio basato sulla distanza massima delle cellule cancerogene.
    - Applica una dose di radiazione ai voxel contenenti cellule, modulando l’effetto in funzione della distanza dal centro (del tumore) e del livello di ossigeno (utilizzando formule e fattori correttivi).

## Irradiazione cellulare

La radiazione inviata alle cellule segue una distribuzione gaussiana, con le cellule più vicine al centro di irradiazione che ricevono una dose maggiore rispetto a quelle più distanti, secondo un andamento a forma di campana. Viene quindi regolata la quantità di dose inviata in funzione del centro di irradiazione.

Come centro di irradiazione si considera il centro del tumore calcolato con il metodo `compute_center()`. Questo calcola il centroide delle cellule cancerose presenti nella griglia 3D, cioè la posizione media pesata in base al numero di cellule cancerose in ciascun voxel.

La dose per ogni cellula in ciascun voxel viene calcolata con:

$$
\text{dose} = \text{multiplicator} \cdot \text{conv(rad, dist)} \cdot \text{omf}
$$

### conv()

$\text{conv(rad, dist)}$ viene definita come $\text{erf}(\text{rad} - \text{x}) - \text{erf}(-\text{rad} - \text{x})$

- $\text{erf()}$: Funzione di errore gaussiana (strettamente legata alla distribuzione normale)
- $\text{rad}$: Raggio in cui si ha il 95% della radiazione totale
- $\text{x}$: Distanza **normalizzata** dal centro di irradiazione

Quello che si vuole ottenere è un valore di dose proporzionale alla distanza dal centro di irradiazione. Si vuole avere una dose più alta in posizioni vicine al centro e dosi basse in posizioni lontane. La funzione `conv()` permette di ottenere questo comportamento. Da notare che `conv()` non è un valore di dose ma una quantità che ci dice quanto deve essere alta o bassa la quantità di dose.

`dist` è la distanza normalizzata dal centro di irradiazione. Essa viene passata come parametro alla funzione `conv()` come:

$$
\frac{x \cdot 10}{radius}
$$

Dove $x$ è la distanza, in voxel, dal centro e $\text{radius}$ è il raggio del tumore calcolato con `tumor_radius()`, il quale trova la posizione più lontana dal centro in cui si trova una cellula tumorale e ne calcola la distanza.

- Intervallo di valori di $x$ **prima della normalizzazione**: $[0, 3 \cdot \text{radius}]$. In `irradiate()` (`grid_3d.cpp`) viene applicata radiazione alle cellule solo se è rispettata la condizione `if (cells[k][i][j].size && dist < 3 * radius)`.
- Intervallo di valori di $x$ **dopo la normalizzazione**: $[0, 30]$ qualunque sia il valore di $\text{radius}$.

### multiplicator

Siccome `conv()` non fornisce un valore effettivo di dose, è necessario introdurre il parametro `multiplicator`. Esso viene determinato tramite il metodo `get_multiplicator()`, che calcola il rapporto tra il valore massimo della `dose` e il valore di `conv()` al centro della distribuzione. In questo modo, moltiplicando `multiplicator` per il valore di `conv()` a una certa distanza dalla distribuzione, si ottiene il valore corretto di dose da passare come parametro a `radiate()`.

### Oxygen Modification Factor (OMF)

Per ogni voxel nella griglia viene calcolato l'OMF. Esso rappresenta l'effetto potenziante dell’ossigeno sulla radiosensibilità dei tessuti tumorali. Quando il livello di ossigeno nei tessuti è alto, il danno indotto dalle radiazioni ionizzanti sul DNA delle cellule tumorali è amplificato. Viene calcolato con:

$$
\text{OMF} = \frac{\frac{\text{oxygen}}{100} \cdot \text{oer}_m + k_m}{\left(\frac{\text{oxygen}}{100} + k_m\right) \cdot \text{oer}_m}
$$

dove:

- $\text{oxygen}$ è il valore di ossigeno nel voxel (lettura da oxygen[k][i][j]),
- `oer_m` e `k_m` sono costanti impostate entrambe a `3.0`.

Questo fattore modifica la dose di radiazione applicata alle cellule:

- Con alta ossigenazione l'OMF risulterà maggiore, aumentando l'efficacia della dose.
- Con bassa ossigenazione l'OMF sarà minore, riflettendo la maggiore resistenza delle cellule ipossiche alla radiazione.


# `controller_3d.cpp` file

Il file gestisce l'interazione e la dinamica complessiva della simulazione, orchestrando le azioni eseguite sulla griglia 3D (`Grid`).

## Funzionamento generale

### Creazione e riempimento griglia

- Creazione di una griglia iniziale: (`grid_creation(cradius, hradius)`):

  Viene generata una griglia iniziale `noFilledGrid` che servirà come base per creare la grigila con le cellule. Essa classifica ogni voxel secondo la distanza dal centro:
  - `-1`: voxel interno (entro raggio tumorale `cradius`).
  - `1`: voxel intermedio (tra `cradius` e `hradius`).
  - `0`: voxel esterno.

- Popolamento della griglia: (`fill_grid(hcells, ccells, noFilledGrid)`):
 Viene creata la griglia 3D contenente le celluele seguendo la configurazione di `noFilledGrid`:
  - Aggiunge `hcells` cellule sane nei voxel classificati con `1` o `-1`.
  - Aggiunge `ccells` cellule cancerogene esclusivamente nei voxel classificati con `-1`.

### Evoluzione cellulare e irradiazione

- Simulazione di un'ora di evoluzione (`go()`):
  - Riempimento sorgenti nutrienti (`fill_sources()`).
  - Ciclo cellulare (`cycle_cells()`).
  - Diffusione nutrienti (`diffuse()`).
  - Calcolo giornaliero del centro tumorale (`compute_center()`).

- Irradiazione (`irradiate(dose)`):
  - Applica radiazione al tumore secondo una dose specificata.

### Salvataggio dati
I dati venogno salvati in due tipologie di file:
- **Grid data files**: Sono nella forma `tx_gd.txt` dove `x` corrisponde all'ora di simulazione in cui si sono salvati i dati (tick). Essi contengono le seguenti informazioni della griglia 3D disposte lungo una riga:
  - Tick
  - Coordinate del voxel: x, y, z
  - Contatori di cellule nel voxel: cellule sane, cancerose e OAR
  - Livello dei nutrimenti: ossigeno e glucosio
  - Tipo del voxel: `-1` se il voxel contiene almeno una cellula cancerosa, `1` se contiene solo cellule sane e `0` se non contiene cellule 

  Questi file venogno salvati ad intervalli (tick) precisi. Intevalli creati con `get_intervals()` e contenuti nella variabile `intervals1` per la fase di growth e in `intervals2` per la fase di treatment.

- **Cell counter files**: Questi file contengono le seguenti informazioni:
  - Tick
  - Numero **totale** di cellule sane, cancerose e OAR presenti nell'intera griglia.

  Si hanno due file diversi: 
    - `cell_counts_gr.txt`: Per i dati durante la fase di growth
    - `cell_counts_gtr.txt`: Per i dati durante la fase di tratment
  
  Nella fase di growth le informazioni vengono salvate ad ogni tick mentre nella fase di treatment ogni 24 ore.

### Piano terapeutico
Il trattamento terapeutico è gestito dal metodo `treatment()`. E' definito da diversi parametri:
- `week = 2`: Weeks of tratments
- `rad_days = 5`: Number of days in which we send radiation
- `rest_days = 2`: Number of days without radiation
- `dose = 2.0`: Dose per day



