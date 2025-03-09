# Evoluzione cellulare
## Glucose/Oxygen efficiency
Durante il ciclo cellulare, ogni cellula consuma glucosio e ossigeno. L'efficienza con cui questi nutrienti vengono assorbiti è definita dai parametri glu_efficiency per il glucosio e oxy_efficiency per l'ossigeno. Tali parametri sono calcolati come segue:

- `glu_efficiency = factor * average_glucose_absorption;`
- `oxy_efficiency = factor * average_oxygen_consumption;`
Il valore di factor viene ottenuto estraendo un numero casuale da una distribuzione normale, al fine di simulare realisticamente la variabilità biologica. I valori medi utilizzati sono:

- average_glucose_absorption = $3,6 \cdot 10^{-9}\ \frac{mg}{cell \cdot hour}$ (O'Neil)
- average_oxygen_consumption = $2,16 \cdot 10^{-9}\ \frac{ml}{cell \cdot hour}$ (Jalalimanesh)

L'impiego della distribuzione normale consente di rappresentare accuratamente la variabilità naturale: molti fenomeni biologici, incluso l'assorbimento del glucosio, tendono a concentrarsi attorno a una media (in questo caso pari a 1,0) con una certa dispersione determinata da una deviazione standard (0,3333). Tale distribuzione produce una curva a campana in cui la maggior parte delle cellule mostra comportamenti simili, mentre alcune presentano variazioni più marcate.

Per limitare l'assorbimento massimo, il valore massimo di efficienza è stato imposto come il doppio del valore massimo (doppio dell'assorbimento medio). Questo accorgimento previene l'insorgenza di valori estremi (negativi o eccessivamente elevati) che, in un contesto biologico, risulterebbero privi di significato e potrebbero compromettere la simulazione.

Per **HealthyCells** e le **OARCells** si ipotizza un comportamento metabolico stabile; pertanto, i coefficienti vengono fissati al momento dell'istanziazione della cellula (all'interno del costruttore) e rimangono invariati per tutta la durata della vita cellulare. Al contrario, per la classe **CancerCells** il metabolismo è considerato più dinamico e variabile. Di conseguenza, i parametri relativi all'efficienza metabolica (glu_efficiency e oxy_efficiency) vengono ricalcolati ad ogni ciclo vitale (all'interno del metodo cycle() definito in cell.cpp), al fine di riflettere le possibili variazioni nell'assorbimento di glucosio e ossigeno nel tempo.

### Valori per l'assorbimento di ossigeno e glucosio:
- Glucosio:
    - Healthy Cells: **`average_glucose_absorption = 0.36`** ($\frac{mg}{cell \cdot hour}$. O'Neil)
    - Cancer Cells: **`average_cancer_glucose_absorption = 0.54`** ($\frac{mg}{cell \cdot hour}$. O'Neil)
- Ossigeno:
    - Healthy Cells: **`average_oxygen_consumption = 20.0`** ($\frac{ml}{cell \cdot hour}$. Jalalimanesh)
    - Cancer Cells: **`average_oxygen_consumption = 20.0`** ($\frac{ml}{cell \cdot hour}$. Jalalimanesh)

### Valori per le soglie di morte e quirscienzs:
- Glucosio: 
    - Morte: **`critical_glucose_level = 6.48`** ($\frac{mg}{cell}$. O'Neil)
    - Quiescienza: **`quiescent_glucose_level = 17.28`** ($\frac{mg}{cell}$. O'Neil)
- Ossigeno: 
    - Morte: **`critical_oxygen_level = 360.0`** ($\frac{ml}{cell \cdot hour}$. Jalalimanesh)
    - Quiescienza: **`quiescent_oxygen_level = 960.0`** ($\frac{ml}{cell \cdot hour}$. Jalalimanesh)



## cell cycle (one hour)
### Healthy Cells
Se la cellula non è in fase di riparazione (ovvero, se repair è pari a 0) viene incrementato il contatore dell'età (age++). Se invece la cellula è in riparazione (repair > 0), il contatore repair viene decrementato e l'età non viene aumentata durante quell'ora.

#### Fasi cellulari
La cellula ha 5 fasi: Quiescence (q), Mitosis (m), Gap (2), Synthesis (s) e Gap 1 (1). Ogni volta che viene completata una fase, l'età viene resettata. 
Se le condizioni sono sempre favorevoli, la cellula trascorre in ciascuna fase il seguente numero di ore:
- **Gap 1**: 11 ore
- **Sintesi**: 8 ore
- **Gap 2**: 4 ore
- **Mitosi**: 1 ora

**TOTALE**: 24 ore

Se invece, le condizioni non sono favorevoli, la cellula può tornare alla fase di quiescienza solo se essa si trova nella fase Gap 1. In tutte le altre fasi non viene effettuata la verifica della bontà delle condizioni.

Le fasi sono:
- **Fase 'q' (Quiescenza)**:
    - La cellula consuma il 75% della sua capacità metabolica (glu_efficiency e oxy_efficiency).
    - Se le condizioni esterne **sono** favorevoli (glucosio > quiescent_glucose_level, ossigeno > quiescent_oxygen_level e numero di vicini inferiore a critical_neighbors), la cellula si "risveglia": si resetta l'età e passa alla fase '1' (Gap 1).

- **Fase '1' (Gap 1)**:
    - La cellula consuma la capacità metabolica completa.
    - Se le condizioni **non sono** favorevoli (glucosio < quiescent_glucose_level, ossigeno < quiescent_oxygen_level o troppo vicini altri nuclei cellulari), la cellula torna in quiescenza ('q') con età resettata.
    - Se, invece, le condizioni rimangono buone e l'età raggiunge almeno **11**, la cellula transita nella fase 's' (Sintesi) per prepararsi alla replicazione.
- **Fase 's' (Sintesi)**:
    - La cellula continua a consumare a pieno regime (gli stessi valori di glu_efficiency e oxy_efficiency).
    - Quando l'età raggiunge **8**, la cellula completa la sintesi del DNA e passa alla fase '2' (Gap 2), resettando l'età.
- **Fase '2' (Gap 2)**:
    - Ancora una volta, la cellula utilizza pienamente le sue risorse metaboliche.
    - Se l'età arriva a **4**, la cellula si prepara per la divisione, resettando l'età e passando alla fase 'm' (Mitosi).
- **Fase 'm' (Mitosi)**:
    - Durante la mitosi, la cellula consuma le risorse complete.
    - Se l'età è pari a **1**, la divisione è completata: la cellula torna in Gap 1 (reset dell'età e cambio di stato) e viene segnalata la creazione di una nuova cellula sana (result.new_cell impostato a 'h').

### CancerCells (Differenze con HealthyCells)  
- Come accennato nella sezione *Glucose/Oxygen efficiency*, a differenza delle healthy cells, le cancer cells calcolano ad ogni ciclo (ogni ora) i fattori di efficienza per il consumo di glucosio e ossigeno al fine di riflettere le possibili variazioni nell'assorbimento di glucosio e ossigeno nel tempo. 
- Non è presente la fase quiescieza. 
- Diverso valore di consumo di glucosio `average_cancer_glucose_absorption`.


## Crescita più rapida delle cancer cells

Nella realtà le cellule cancerose di riproducono più velocemente di quelle sane. Questo comportamento è replicato anche nella simulazione grazie a diverse caratteristiche del codice
1. **Ordine in CellList**: Ogni voxel della griglia contiene un oggetto `CellList`, il quale contiene tutte le cellule presenti. All'interno di questa lista, le cellule cancerose (`CancerCells`) sono posizionate prima delle cellule sane (`HealthyCells`).
Di conseguenza, quando si itera su tutte le cellule della lista, le cellule cancerose consumano per prime i nutrienti disponibili nel voxel. Questo meccanismo riduce la quantità di risorse residue per le cellule sane, aumentando la probabilità che i livelli di ossigeno e glucosio scendano sotto la soglia critica, causando lo stato di quiescenza o la morte cellulare.
2. **Quiesceinza**: Gli oggetti `HealthyCells`, quando si trovano nella fase `G1`, possono entrare in uno stato di quiescienza se una delle seguenti condizioni è rispettate:
    - Gluocsio nel voxel minore di un certo livello
    - Ossigeno nel voxel minore di un certo livello
    - Il **numero delle cellule** vicine è maggiore di un valore critico:
        - Nel modello 2D è stato scenlto un numero critico pari a `9`.
        - Per rimanere coerenti, ho scelto il valore scritico pari a `27` nel modello 3D 


    In questo stato le cellule non procedono con l'evoluzione cioè non procedono con le fasi del ciclo cellulare quindi perdono la possibilità di dividersi creando nuove cellule. La loro età, se non si trovano in stato di riparazione vinene comunque aggiornata. 
3. **Condizione di passaggio a fasi sucessive**: La condizione per il passaggio di una cellula alla fase successiva è più restrittiva nelle cellule sane. In particolare, per queste ultime, il requisito è che l'età sia strettamente uguale (`==`) a un valore specifico. Al contrario, per le cellule cancerose, la condizione è più flessibile, consentendo il passaggio anche se l'età è maggiore o uguale (`>=`) a tale valore. (DA VERIFICARE VERIFICA)
4. **Consumo maggiore di nutrimento**:Le cellule cancerose consumano una quantità di glucosio superiore rispetto a quelle sane. Questo, combinato con il loro posizionamento prioritario nella lista, comporta una riduzione significativa dei nutrienti disponibili per le cellule sane. Di conseguenza, le cellule sane hanno una maggiore probabilità di trovarsi in condizioni di carenza nutrizionale, che può portarle alla morte o a entrare in stato di quiescenza.
## Morte cellulare
La morte cellulare avviene se i livelli di ossigeno **o** glucosio scendono al di sotto di un livello critico. I livelli sono uguali sia per le `HealthyCells` che per `CancerCells`.

- **Glucosio**: **`critical_glucose_level = 6.48`** ($\frac{mg}{cell}$. O'Neil)
- **Ossigeno**: **`critical_oxygen_level = 360.0`** ($\frac{ml}{cell \cdot hour}$. Jalalimanesh)

## Processo di consumo in cycle_cells (grid)
L'algoritmo scorre attraverso ogni voxel della griglia e, per ciascun voxel, itera su ogni cellula contenuta al suo interno.
Per ogni cellula viene calcolato il consumo di nutrienti all'interno del file cell.cpp. Questo valore viene successivamente sottratto al totale disponibile nel voxel, operazione che avviene nel file grid_3d.cpp.
Questa sequenza di operazioni garantisce che le cellule modifichino progressivamente la disponibilità di risorse nel proprio ambiente, influenzando così il comportamento e la sopravvivenza delle altre cellule presenti nella griglia.