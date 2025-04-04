# `grid_3d.cpp` file

Il file modella il comportamento di un ambiente cellulare nella griglia 3D e integra la dinamica dei nutrienti e della radiazione.

## Descrizione generale delle funzioni del file
### Gestione delle Cellule (CellList)
- **Creazione e distruzione**: Viene implementata una lista collegata (`CellList`) per gestire i nodi delle cellule (`CellNode`).

- **Aggiunta di cellule**:  
  - Funzioni `add` per inserire nuove cellule; le cellule cancerogene vengono aggiunte all'inizio, mentre quelle sane e OAR in coda. Si aggiornano i contatori interni per cellule cancerogene.

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
La radiazione inviata alle cellule segue una distribuzione gaussiana, con le cellule più vicine al centro di irradiazione che ricevono una dose maggiore rispetto a quelle più distanti, secondo un andamento a forma di campana.
Viene quindi regolata la quantita di dose inviata in funzione del centro di irradiazione.

Come centro di irradizione si considera il centro del tumore calcolato con il metodo  `compute_center()`. Questo calcola il centroide delle cellule cancerose presenti nella griglia 3D, cioè la posizione media pesata in base al numero di cellule cancerose in ciascun voxel.

La dose per ogni cellula in ciascun voxel viene calcolata con 
$$
\text{dose} = \text{multiplicator} \cdot \text{conv(rad, dist)} \cdot \text{omf} 
$$

### conv()
$\text{conv(rad, dist)}$ viene definita come $\text{erf}(\text{rad} - \text{x}) - \text{erf}(-\text{rad} - \text{x})$
- $\text{erf()}$: Funzione di errore gaussiana (strettamente legata alla distibuzione normale)
- $\text{rad}$: Raggio in cui si ha il 95% della radiazione totale
- $\text{x}$: Distanza **normalizzata** dal centro di irradiazione

Quello che si vuole ottenere è un valore di dose proporzionale alla distanza dal centro di irradiazione. Si vuole avere una dose più alta in posizioni vicine al centro e dosi basse in posizioni lontane. La funzione `conv()` permette di ottenere questo comportamento. Da notare che `conv()` non è un valore di dose ma una quantità che ci dice quanto deve essere alta o bassa la quantità di dose.

`dist` è la distanza normalizzata dal centro di irradaizione. Essa viene passata come parametro alla funzione `conv()` come:
$$
\frac{x \cdot 10}{radius}
$$
Dove $x$ è la distanza, in voxel, dal centro e $\text{radius}$ è il raggio del tumore calcolato con `tumor_radius()` il quale trova la posizione più lontana dal centro in cui si trova una cellula tumorare e ne calcola la distanza.

- Intervallo di valori di $x$ **prima della noramlizzazione**: $[0, 3 \cdot \text{radius}]$. In `irradiate()` (`grid_3d.cpp`) viene applicata radiazione alle cellule solo se è rispettata la condizione `if (cells[k][i][j].size && dist < 3 * radius)`.
- Intervallo di valori di $x$ **dopo la noramlizzazione**: $[0, 30]$ qualunque sia il valore di $\text{radius}$.

### multiplicator
Siccome `conv()` non fornisce un valore effettivo di dose, è necessario introdurre il parametro `multiplicator`. Esso viene determinato tramite il metodo `get_multiplicator()`, che calcola il rapporto tra il valore massimo della `dose` e il valore di `conv()` al centro della distribuzione. In questo modo, moltiplicando `multiplicator` per il valore di `conv()` a una certa distanza dalla distribuzione, si ottiene il valore corretto di dose da passare come parametro a `radiate()`.

### Oxygen Modification Factor (OMF)
Per ogni voxel nella grglia viene calcolato l'OMF. Esso rappresenta l'effetto potenziante dell’ossigeno sulla radiosensibilità dei tessuti tumorali. Quando il livello di ossigeno nei tessuti è alto, il danno indotto dalle radiazioni ionizzanti sul DNA delle cellule tumorali è amplificato. Viene calcolato con:
$$
\text{OMF} = \frac{\frac{\text{oxygen}}{100} \cdot \text{oer}_m + k_m}{\left(\frac{\text{oxygen}}{100} + k_m\right) \cdot \text{oer}_m}
$$
dove:
- $\text{oxygen}$ è il valore di ossigeno nel voxel (lettura da oxygen[k][i][j]),
- `oer_m` e `k_m` sono costanti impostate entrambe a `3.0`.

Questo fattore modifica la dose di radiazione applicata alle cellule:
- Con alta ossigenazione l'omf risulterà maggiore, aumentando l'efficacia della dose.
- Con bassa ossigenazione l'omf sarà minore, riflettendo la maggiore resistenza delle cellule ipossiche alla radiazione.