# `grid_3d.cpp` file

Il file modella il comportamento di un ambiente cellulare nella griglia 3D e integra la dinamica dei nutrienti e della radiazione.

## Descriuzione generale delle funzioni del file
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

Come centro di irradizione di considera il centro del tumore ottenuto con il metodo  `compute_center()`. Questo calcola il centroide delle cellule cancerose presenti nella griglia 3D, cioè la posizione media (centro del tumore) pesata in base al numero di cellule cancerose in ciascun voxel.

La dose per ogni cellula in ciascun voxel viene calcolata con 
$$
\text{multiplicator} \cdot \text{conv(centro)} = \frac{\text{dose}}{\text{conv(centro)}} \cdot \text{conv(centro)} = \text{dose}
$$