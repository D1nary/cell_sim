# Simulazione
La simulazione vuole replicare il comportamento di un ambiente cellulare 3D e gli effetti della radiazione ionizzante (radioterapia) su di esso. Il modello simula l' External Beam Radiotherapy (EBR). 
La simulazione è composta da diversi file:
- `cell.cpp` e `cell.h`: Implementano le classi delle celle dei diversi tipi di cellule e come queste reagiscono alle radiazioni.
- `grid_3d.cpp` e `grid_3d.h`: Implementano la classe per la lista di cellule presente all'interno di ciascun voxel della griglia. Integrano la simulazione del comportamento delle cellule (divisone, morte, risveglio) e la dinamica dei nutrienti e della radiazione.
- `controller_3d.cpp` e `controller_3d.h`: Coordinano l’inizializzazione, l’aggiornamento e il monitoraggio dell’intera simulazione, integrando sia la dinamica cellulare che la gestione dei trattamenti e della raccolta dati.

# `cell.cpp` file 
Il file cell.cpp Gestisce il comportametno delle singole cellule el'interazione di ciascuna di esse con la radiazione. Ogni cellula è rappresentata da una classe diversa:
- `HealthyCell`: Cellule sane
- `CancerCell`: Cellule cancerose
- `OARCell`: cellule Organ At Risk (OAR)

Vengono svolte le seguenti operazioni:
- **Simulazione del ciclo cellulare**: Gestione delle diverse fasi (quiescenza, Gap 1, Synthesis, Gap 2, Mitosi) per ciascun tipo di cellula.Verifica dei livelli critici di nutrienti (glucosio e ossigeno) e della densità cellulare per decidere il proseguimento o la morte cellulare.

- **Consumo di nutrienti**:Calcolo del consumo di glucosio e ossigeno basato su valori medi e variabilità simulata tramite distribuzioni casuali.

- **Effetti della radiazione**:Applicazione di modelli modificati (LQ) per determinare la probabilità di sopravvivenza dopo l’irradiamento, con meccanismi di riparazione attivati in base alla dose.

- **Parametri specifici**: Definizione di costanti critiche e coefficienti per il consumo e la risposta alla radiazione, differenziati per cellule sane, tumorali e OAR.


## Glucose/Oxygen efficiency
Durante il ciclo cellulare, ogni cellula consuma glucosio e ossigeno. L'efficienza con cui questi nutrienti vengono assorbiti è definita dai parametri `glu_efficiency` per il glucosio e `oxy_efficiency` per l'ossigeno. Tali parametri sono calcolati come segue:

- `glu_efficiency = factor * average_glucose_absorption;`
- `oxy_efficiency = factor * average_oxygen_consumption;`

Il valore di factor viene ottenuto estraendo un numero casuale da una **distribuzione normale**, al fine di simulare realisticamente la variabilità biologica. I valori medi utilizzati sono:

- average_glucose_absorption = $3,6 \cdot 10^{-9}\ \frac{mg}{cell \cdot hour}$ (O'Neil)
- average_oxygen_consumption = $2,16 \cdot 10^{-9}\ \frac{ml}{cell \cdot hour}$ (Jalalimanesh)

L'impiego della distribuzione normale consente di rappresentare accuratamente la variabilità naturale: molti fenomeni biologici, incluso l'assorbimento del glucosio, tendono a concentrarsi attorno a una media (in questo caso pari a `1,0`) con una certa dispersione determinata da una deviazione standard (`0,3333`). Tale distribuzione produce una curva a campana in cui la maggior parte delle cellule mostra comportamenti simili, mentre alcune presentano variazioni più marcate.

Per limitare l'assorbimento massimo, il valore massimo di efficienza è stato imposto come il doppio del valore massimo (doppio dell'assorbimento medio). Questo accorgimento previene l'insorgenza di valori estremi (negativi o eccessivamente elevati) che, in un contesto biologico, risulterebbero privi di significato e potrebbero compromettere la simulazione.

Per **HealthyCells** e le **OARCells** si ipotizza un comportamento metabolico stabile; pertanto, i coefficienti vengono fissati al momento dell'istanziazione della cellula (all'interno del costruttore) e rimangono invariati per tutta la durata della vita cellulare. Al contrario, per la classe **CancerCells** il metabolismo è considerato più dinamico e variabile. Di conseguenza, i parametri relativi all'efficienza metabolica (`glu_efficiency` e `oxy_efficiency`) vengono ricalcolati ad ogni ciclo vitale (all'interno del metodo `cycle()` definito in `cell.cpp`), al fine di riflettere le possibili variazioni nell'assorbimento di glucosio e ossigeno nel tempo.

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
Se la cellula non è in fase di riparazione (ovvero, se `repair` è pari a 0) viene incrementato il contatore dell'età (`age++`). Se invece la cellula è in riparazione (repair > 0), il contatore repair viene decrementato e l'età non viene aumentata durante quell'ora.

**Fasi cellulari**

La cellula ha 5 fasi: Quiescence (q), Mitosis (m), Gap 2 (2), Synthesis (s) e Gap 1 (1). Ogni volta che viene completata una fase, l'età viene resettata. 
Se le condizioni sono sempre favorevoli, la cellula trascorre in ciascuna fase il seguente numero di ore:
- **Gap 1**: 11 ore
- **Sintesi**: 8 ore
- **Gap 2**: 4 ore
- **Mitosi**: 1 ora

**TOTALE**: 24 ore

Se invece, le condizioni non sono favorevoli, la cellula può tornare alla fase di quiescienza solo se essa si trova nella fase Gap 1. In tutte le altre fasi non viene effettuata la verifica della bontà delle condizioni.

Le fasi sono:
- **Fase 'q' (Quiescenza)**:
    - La cellula consuma il 75% della sua capacità metabolica (`glu_efficiency` e `oxy_efficiency`).
    - Se le condizioni esterne **sono** favorevoli (glucosio > `quiescent_glucose_level`, ossigeno > `quiescent_oxygen_level` e numero di vicini inferiore a `critical_neighbors`), la cellula si "risveglia": si resetta l'età e passa alla fase '1' (Gap 1).

- **Fase '1' (Gap 1)**:
    - La cellula consuma la capacità metabolica completa.
    - Se le condizioni **non sono** favorevoli (glucosio < `quiescent_glucose_level`, ossigeno < `quiescent_oxygen_level` o troppo vicini ad altri nuclei cellulari), la cellula torna in quiescenza ('q') con età resettata.
    - Se, invece, le condizioni rimangono buone e l'età raggiunge almeno **11**, la cellula transita nella fase 's' (Sintesi) per prepararsi alla replicazione.
- **Fase 's' (Sintesi)**:
    - La cellula continua a consumare a pieno regime.
    - Quando l'età raggiunge **8**, la cellula completa la sintesi del DNA e passa alla fase '2' (Gap 2), resettando l'età.
- **Fase '2' (Gap 2)**:
    - Ancora una volta, la cellula utilizza pienamente le sue risorse metaboliche.
    - Se l'età arriva a **4**, la cellula si prepara per la divisione, resettando l'età e passando alla fase 'm' (Mitosi).
- **Fase 'm' (Mitosi)**:
    - Durante la mitosi, la cellula consuma le risorse complete.
    - Se l'età è pari a **1**, la divisione è completata: la cellula torna in Gap 1 (reset dell'età e cambio di stato) e viene segnalata la creazione di una nuova cellula sana (`result.new_cell` impostato a 'h').

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

## Radiazione
Ogni cellula possiede una determinata probabilità di sopravvivenza alla radiazione. Questa cambia se la cellula è sana o cancerosa. 

In entrambi i casi, l probabilità di sopravvivenza della cellula dopo l'irradiazione è calcolata utilizzando un modello **LQ** (**Linear-Quadratic**) modificato.



### Healthy Cells
$$
P_{sopravvivenza} = \exp\Big( \gamma \cdot \Big(-\alpha \cdot d - \beta \cdot d^2\Big) \Big)
$$

Dove:
- **$d$** è la dose di radiazione (in grays).
- **$\alpha$** corrisponde al parametro `alpha_norm_tissue` nel codice.
- **$\beta$** corrisponde al parametro `beta_norm_tissue`nel codice.
- **$\gamma$** è un fattore di modifica che dipende dallo **stadio** della cellula:
  - Se lo stadio è `'2'` o `'m'`$\gamma = 1.$
  - Se lo stadio è `'1'` (o in caso di default): $\gamma = 1$
  - Se lo stadio è `'q'` o `'s'`$\gamma = 0.$

### Cancer Cells

$$
P_{sopravvivenza} = \exp\Big( \gamma \cdot \big(-\alpha_{tumor} \cdot d - \beta_{tumor} \cdot d^2\big) \Big)
$$

Dove:
- **$d$** è la dose di radiazione (in grays).
- **$\alpha_{tumor}$** rappresenta il parametro `alpha_tumor`.
- **$\beta_{tumor}$** rappresenta il parametro `beta_tumor`.
- **$\gamma$** è un fattore modificatore che dipende dallo **stadio** della cellula:
  - Se lo stadio è `'2'` o `'m'`: $\gamma = 1.25$
  - Se lo stadio è `'1'` oppure si verifica il caso predefinito: $\gamma = 1.0$
  - Se lo stadio è$

### Parametri utilizzati:
- `alpha_tumor = 0.3` (Powathil)
- `beta_tumor = 0.03` (Powathil)
- `alpha_norm_tissue = 0.15`
- `beta_norm_tissue = 0.03`
