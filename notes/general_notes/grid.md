# Appunti grid

## Deallocazione memoria di un oggetto

Considerando in grid.h
```c++
struct CellNode
{
    int x, y;
    Cell * cell;
    CellNode *next;
    char type;
};

```
e in grid.cpp:
```c++
CellList::~CellList() {
    CellNode * current = head;
    CellNode * next;
    
    //Finché current non è nullptr (nullptr = puntatore nullo)
    while (current){ // Delete all the CellNodes and Cells in the CellList
        next = current -> next;

        delete current -> cell;
        
        delete current;
        current = next;
    }
}
```

La necessità di liberare sia la memoria associata al membro `cell` sia quella associata all'oggetto `CellNode` nasce dal modo in cui è strutturata la memoria in C++ e dalla relazione tra un oggetto e i suoi membri. In particolare:

1. **`CellNode` contiene un puntatore a un oggetto `Cell`**:
   - Il membro `cell` di `CellNode` è un puntatore, non un'istanza diretta di `Cell`.
   - Questo significa che la memoria per l'oggetto `Cell` (puntato da `cell`) viene allocata separatamente rispetto alla memoria per l'oggetto `CellNode`.

2. **Deallocare un oggetto non dealloca automaticamente ciò a cui i suoi puntatori fanno riferimento**:
   - Quando si elimina un oggetto (`delete current`), viene deallocata solo la memoria per l'oggetto stesso (cioè il nodo `CellNode`).
   - Tuttavia, i puntatori membri dell'oggetto (`cell` in questo caso) non vengono automaticamente seguiti e la memoria a cui essi puntano non viene automaticamente liberata.
   - Quindi, senza un `delete current->cell`, la memoria allocata per l'oggetto `Cell` a cui `cell` punta rimarrebbe occupata (causando un **memory leak**).

3. **Gestione separata della memoria**:
   - `CellNode` e `Cell` sono entità separate nella memoria.
   - Deallocare il nodo (`CellNode`) non libera automaticamente l'oggetto `Cell`, che è stato allocato separatamente e richiede un `delete` specifico.

## Creazione dinamica di un istanaza
Consideriamo le seguenti righe di codice nel file grid.cpp
```c++
void CellList::add(Cell *cell, char type) {
    CellNode * newNode = new CellNode;
    assert(cell);
    newNode -> cell = cell;
    newNode -> type = type;
    add(newNode, type);
}
```
L'espressione `new CellNode` crea dinamicamente un'istanza di un oggetto di tipo `CellNode`. Questo processo implica:
1. **Allocazione dinamica di memoria**: La parola chiave `new` alloca memoria sull'heap per l'oggetto di tipo `CellNode`. Questo permette che l'oggetto persista finché non viene esplicitamente deallocato usando `delete`.

2. **Inizializzazione dell'oggetto**: Una volta allocata la memoria, viene chiamato il costruttore predefinito per inizializzare i membri dell'oggetto, se necessario. In questo caso, `CellNode` è una struttura e non ha un costruttore esplicito, quindi i suoi membri non vengono inizializzati automaticamente (potrebbero contenere valori casuali a meno che non siano esplicitamente assegnati).

3. **Restituzione di un puntatore**: **L'OPERATORE `new` RESTITUISCE UN PUNTATORE ALL'OGGETTO APPENA CREATO**, che può essere utilizzato per accedere e manipolare i membri dell'oggetto.

Considerando la riga di codice
```c++
CellNode * newNode = new CellNode;
```
- `newNode` è un puntatore che punta all'istanza di `CellNode` creata sull'heap.
- Dopo la creazione, i membri di `CellNode` vengono inizializzati manualmente

## L'heap

L'heap è una regione della memoria di un programma utilizzata per l'allocazione dinamica di memoria. Quando un programma ha bisogno di memoria la cui dimensione o durata non è nota durante la compilazione, utilizza l'heap per ottenere spazio.

### Caratteristiche principali dell'heap

1.  Allocazione dinamica

    - La memoria viene allocata durante l'esecuzione del programma tramite operazioni come `new` in C++.
    - La durata dell'oggetto allocato dipende dal programma e non è legata al ciclo di vita di una funzione o di un blocco di codice.

2. Gestione manuale della memoria

    - L'heap richiede che il programmatore liberi esplicitamente la memoria allocata usando `delete` (in C++) o funzioni analoghe.
    - Se la memoria non viene liberata, si crea un **memory leak** (fuga di memoria), che può causare esaurimento della memoria disponibile.

3. Struttura gerarchica

    - Internamente, l'heap è organizzato come una struttura che consente di soddisfare richieste di memoria di dimensioni variabili. Spesso utilizza algoritmi per allocare e liberare blocchi di memoria in modo efficiente.


## Funzione `deleteDeadAndSort`

La funzione `deleteDeadAndSort` è progettata per **gestire una lista concatenata di nodi** (`CellNode`), con lo scopo di:

1. **Rimuovere i nodi contenenti celle morte** (ossia, nodi in cui il membro `cell->alive` è `false`).
2. **Riordinare i nodi rimanenti** garantendo che la lista collegata sia valida e i puntatori siano correttamente aggiornati.
3. **Aggiornare i contatori associati ai nodi** (come `oar_count`, `ccell_count`).
4. **Mantenere l'integrità della lista**, ovvero:
   - Il puntatore alla testa della lista (`head`) deve puntare al primo nodo valido.
   - Il puntatore alla coda della lista (`tail`) deve puntare all'ultimo nodo valido.
   - La lista deve terminare correttamente con `tail->next == nullptr`.


### **Logica passo-passo**

1. **Traversal della lista**
    La funzione itera attraverso tutti i nodi della lista concatenata utilizzando un puntatore (`current`) per scorrere da un nodo al successivo:
    ```cpp
    CellNode *current = head;
    ```

2. **Rimozione dei nodi con celle morte**
    Quando una cella nel nodo non è viva (`current->cell->alive == false`), il nodo viene rimosso:
    - **Liberazione della memoria**:
        - La memoria occupata dalla cella (`current->cell`) viene liberata con `delete current->cell`.
        - Anche il nodo stesso viene eliminato con `delete toDel`.
   
    - **Aggiornamento della lista**:
        - `current` viene spostato al nodo successivo con `current = current->next`.
        - Il contatore della dimensione della lista (`size`) viene decrementato.
   
    - **Aggiornamento dei contatori specifici per i tipi di cella**:
        - Se la cella era di tipo `'o'`, decrementa `oar_count`.
        - Se la cella era di tipo `'c'`, decrementa `ccell_count`.

    Questo processo assicura che tutte le celle morte vengano rimosse e che la memoria allocata dinamicamente sia deallocata correttamente, evitando **memory leaks**.

3. **Gestione della testa della lista**
    La funzione identifica il primo nodo valido (con una cella viva) per aggiornarlo come nuova testa della lista:
    ```cpp
    if (!found_head) {
        head = current;
        tail = current;
        previous_next_pointer = & (current -> next);
        ...
        found_head = true;
    }
    ```
    - `head` e `tail` vengono impostati al primo nodo valido trovato.
    - Questo assicura che, in caso di eliminazione di tutti i nodi precedenti, la lista inizi correttamente dal primo nodo valido.

    **NOTA: La condizione `if (!found_head)` serve a identificare il primo nodo valido utilizzando la variabile `found_head`. Essendo presente una struttura `else if`, solo una delle condizioni può essere verificata alla volta. In questo contesto, se la prima condizione non viene soddisfatta (cioè la cellula non è morta) e il nodo corrente è il primo valido (cellula viva e `found_head` falso), allora if (!`found_head`) risulterà vera, indicando che abbiamo trovato la prima cellula non morta.**


4. **Riordinamento della lista**
    Per ogni nodo valido successivo:
    - **Collegamenti corretti**:
        - Il puntatore `previous_next_pointer` viene aggiornato per puntare al membro `next` del nodo corrente.
        - Questo consente di aggiornare i collegamenti tra i nodi senza dover mantenere un puntatore esplicito al nodo precedente.
   
    - **Aggiornamento della coda**:
        - `tail` viene impostato al nodo corrente, rendendolo l'ultimo nodo valido.

5. **Lista vuota**
    Se tutti i nodi sono stati eliminati (nessuna cella viva trovata):
    ```cpp
    if (!found_head) {
        assert(size == 0);
        head = nullptr;
        tail = nullptr;
    }
    ```

6. **Fine della lista**
    Per garantire che la lista sia ben terminata:
    ```cpp
    tail->next = nullptr;
    ```
    Questo assicura che il nodo alla coda della lista non punti a memoria non valida.


### **Obiettivi della funzione**

1. **Gestione della memoria**:
   - Rimuove i nodi inutili (corrispondenti a celle morte) e libera la memoria associata.

2. **Integrità della lista**:
   - Mantiene i collegamenti tra i nodi validi, evitando riferimenti a memoria non valida o nodi eliminati.

3. **Semplicità del traversal**:
   - Usa un doppio puntatore (`previous_next_pointer`) per manipolare i collegamenti tra i nodi in modo elegante.

4. **Correttezza strutturale**:
   - Aggiorna correttamente `head`, `tail`, e assicura che la lista sia ben terminata.


## Doppio puntatore (`glucose = new double*[xsize];`)
All'interno dell'implementazione del costruttore `Grid`, si ha la seguente righa di codice:
```cpp
glucose = new double*[xsize];
```
Questo è solo uno dei casi, all'interno del costruttore `Grid`. Un altro esempio è `cells = new CellList*[xsize];`.

`glucose` è un puntatore doppio. Infatti nel file `grid.h` viene definito con `double ** glucose;`.

Quella che stiamo eseguendo è un'operazione di **allocazione dinamica della memoria**.
Con `new double*[xsize]` allochiamo dinamicamente un array di puntatori con dimensione `xsize` nell'heap. Viene riservata memoria per un array di dimensione `xsize`, in cui ogni elemento è un puntatore a `double`.
Il risultato è un array unidimensionale di puntatori inizialmente non assegnati (contenenti valori indefiniti). Questo è un primo passo per costruire una matrice bidimensionale dinamica.

Successivamente, rimuovendo le righe di codice non utili per l'esempio, nel codice del file `grid.cpp` abbiamo:
```cpp
for (int i = 0; i < xsize; i++) {
    glucose[i] = new double[ysize];
    std::fill_n(glucose[i], ysize, 100.0); // 1E-6 mg O'Neil
}
```

Con `glucose[i] = new double[ysize];`, ad ogni elemento `glucose[i]`, si alloca dinamicamente un array di ysize elementi di tipo `double`. Ogni `glucose[i]` punta a questo array, che rappresenta una riga della matrice.
### Cosa ottieni alla fine?
- `cells`: Varibile che punta ad una matrice bidimensionale con `xsize` righe.
- `cells[i]`: Ogni riga della matrice è un puntatore ad un array di `ysize` "oggetti" `double`. 

La struttura risultante in memoria è simile a questa:
```scss
glucose (puntatore doppio)
|
|- glucose[0] --> [100.0, 100.0, 100.0, ..., 100.0]  (ysize elementi)
|- glucose[1] --> [100.0, 100.0, 100.0, ..., 100.0]  (ysize elementi)
|- ...
|- glucose[xsize-1] --> [100.0, 100.0, 100.0, ..., 100.0]  (ysize elementi)
```
Ogni riga (array unidimensionale) è indipendente e ha `ysize` elementi, tutti inizializzati a `100.0`.

### Nota sulla gestione della memoria
Per evitare fughe di memoria (memory leaks), è importante liberare tutta la memoria allocata dinamicamente alla fine del programma.


### Perché si alloca dinamicamente la memoria?

L'allocazione dinamica della memoria in C++ viene scelta rispetto all'allocazione statica o automatica per **flessibilità**, **controllo** e **adattabilità**. Nel caso della matrice `glucose`, la scelta di allocare dinamicamente la memoria (tramite `new`) invece di usare un'allocazione statica è motivata da alcune ragioni chiave:


1. **Dimensioni variabili**
    - **Allocazione statica**:
      - Le dimensioni di un array devono essere note **a tempo di compilazione**. Ad esempio:
        ```cpp
        double glucose[10][10]; // Dimensioni fissate a 10x10
        ```
        Questo approccio è rigido e non consente di adattare le dimensioni della matrice in base ai dati o alle esigenze del programma.

    - **Allocazione dinamica**:
      - Con `new`, puoi decidere le dimensioni di `glucose` durante l'esecuzione, in base ai valori di `xsize` e `ysize`, che possono essere calcolati o letti da input:
        ```cpp
        double** glucose = new double*[xsize];
        for (int i = 0; i < xsize; i++) {
            glucose[i] = new double[ysize];
        }
        ```
      - **Vantaggio**: Ti permette di creare una griglia di dimensioni personalizzate, ad esempio, in base alla risoluzione di una simulazione.

2. **Risparmio di memoria**
    - L'allocazione dinamica utilizza **l'heap**, che ha una dimensione molto maggiore rispetto allo **stack**.
      - **Allocazione automatica (stack)**:
        - Se dichiari grandi matrici, come `double glucose[1000][1000];`, potresti esaurire lo stack, che è limitato (tipicamente pochi MB).
      - **Allocazione dinamica (heap)**:
        - Permette di utilizzare memoria su larga scala (potenzialmente centinaia di MB o più), che è utile per simulazioni complesse come nel tuo caso.


3. **Durata della memoria**
    - **Allocazione automatica**:
      - Una matrice dichiarata in modo automatico (ad esempio, all'interno di una funzione) esiste solo durante il ciclo di vita della funzione. Una volta che la funzione termina, la memoria viene automaticamente deallocata.
      - Esempio:
        ```cpp
        void func() {
            double glucose[100][100]; // Allocato nello stack
            // Alla fine della funzione, la memoria viene rilasciata
        }
        ```

    - **Allocazione dinamica**:
      - La memoria allocata dinamicamente sull'heap **persiste finché non viene deallocata esplicitamente**. Questo è utile se i dati devono essere accessibili in altre parti del programma o se la durata della memoria non è legata al ciclo di vita di una funzione.
      - Esempio:
        ```cpp
        double** glucose = new double*[xsize]; // Persiste finché non fai delete[]
        ```

4. **Strutture dati avanzate**
    L'allocazione dinamica è essenziale per strutture dati più complesse (come matrici, alberi o grafi) che richiedono una gestione flessibile della memoria:
    - Una griglia come `glucose` rappresenta una matrice di dimensioni variabili, che può essere adattata dinamicamente.
    - Inoltre, puoi persino ridimensionare o riconfigurare parte della griglia (ad esempio, espandendo alcune righe o modificando singole dimensioni) in base alle esigenze di calcolo.

5. **Modularità e riutilizzo del codice**
    L'allocazione dinamica consente di scrivere codice più generale e modulare:
    - Puoi passare `xsize` e `ysize` come parametri, permettendo al tuo programma di gestire diverse configurazioni di simulazione.
    - Le funzioni possono essere progettate per lavorare con qualsiasi matrice dinamica, indipendentemente dalle sue dimensioni.

### **Quando usare l'allocazione statica**
L'allocazione statica può essere utile in alcuni scenari:
1. **Dimensioni fisse e piccole**:
   - Se le dimensioni della matrice sono sempre costanti e piccole, come `double glucose[10][10]`.
2. **Prestazioni**:
   - L'allocazione statica (o automatica) è leggermente più veloce rispetto all'allocazione dinamica, perché non coinvolge l'heap.
3. **Semplicità**:
   - Non è necessario gestire manualmente la deallocazione.

Tuttavia, in contesti come simulazioni complesse, dove le dimensioni sono variabili e la memoria richiesta è significativa, l'allocazione dinamica è la scelta migliore.

### **Sintesi**
In sintesi, si preferisce l'allocazione dinamica della memoria per la matrice `glucose` perché:
- Le dimensioni non sono note a tempo di compilazione.
- È necessario gestire una grande quantità di memoria.
- I dati devono persistere oltre il ciclo di vita di una singola funzione.
- Permette maggiore flessibilità e adattabilità del programma.


## Matrici dichiarate come puntatori. Come mai?
La matrice glucose viene creata utilizzando puntatori e doppi puntatori anziché in modo "tradizionale" ad esempio, con un array bidimensionale double `glucose[xsize][ysize];` poichè in quest'ultimo caso si richiederebbe  che le dimensioni `xsize` e `ysize` siano note a tempo di compilazione. Queato implicherebbe l'uso della memoria **stack** e non quella nell'**heap** (**memoria dinamica**). Per i vantaggi della memoria dinamica consulta la sezione "*Perché si alloca dinamicamente la memoria?*" nel sottocapitolo di questo "*## Doppio puntatore (`glucose = new double*[xsize];`)*" file.

## Chaining dei costruttori
Considerando l'implementazione del costruttore
```cpp
Grid::Grid(int xsize, int ysize, int sources_num, OARZone * oar_zone):Grid(xsize, ysize, sources_num)
```
Abbiamo il primo costruttore a 4 parametri ed il secondo a 3 parametri.  Il costruttore a 4 parametri sta delegando parte del suo lavoro al costruttore a 3 infatti è quest'ultimo che inizializza la griglia.

L'uso del costruttore delegato permette di riutilizzare il codice e di evitare duplicazioni. In questo modo, la maggior parte delle inizializzazioni viene gestita dal costruttore di base a 3 parametri.

### Flusso dell'esecuzione
Quando viene invocato il costruttore `Grid(int xsize, int ysize, int sources_num, OARZone * oar_zone)`:

1. **Chaining**: Viene chiamato il costruttore `Grid(int xsize, int ysize, int sources_num)` per inizializzare la struttura della griglia.
2. **Assegnazione**: La variabile membro `oar` viene inizializzata con il valore di `oar_zone` passato come parametro.
3. Il costruttore termina e l'oggetto `Grid` è pronto per essere utilizzato.

# Creazione matrici 2D e 3D mediante puntatori
## 2D
`double **glucose` 
(Nota: glucose è definito come puntatore)


`glucose = new double*[xsize];`
glucose (già definito in precedenza come un puntatore) punta ad un array di xsize puntatori.

```cpp
for(int i = 0; i < xsize; i++){  //Itero su tutti i glucose[i]
glucose[i] = new double[ysize];
}
```

Associo ogni elemento glucose[i] (già definito essere un puntatore) ad un array di ysize oggetti ti tipo double.

### PERCHÈ CHIAMIAMO glucose UN PUNTATORE DOPPIO?
Perchè glucose punta ad un array contenente altri puntatori 

### COME MAI LA CREAZIONE DI UN PUNTATORE DOPPIO IN QUESTO MODO COSTRUISCE UNA MATRICE?
Il concetto della matrice costruita con i puntatori non è diverso dalla costruzione di una matrice in maniera "tradizionale". L'unica cosa che cambia è che non si accede direttametne alla matrice tramite la variabile che la contiene ma tramite il corrispondente puntatore. Per esempio:
- In python: Se abbiamo una matrice m (lista di liste) ed eseguo `print(m)`, quello che ottengo è un risultato del tipo:
```python
[[1,2,3],[4,5,6],[7,8,9]]
```
in cui ogni elemento m[i] corrisponderà ad un array di valori per esempio: `m[0] = [1,2,3]`
- In c++: Se abbiamo un puntatore ad una matrice bidimensiomale m_p ed vado a printare tale matrice quello che ottengo è:
```cpp
[ptr1, ptr2, ptr3, ptr4]
```
cioè una lista di puntatori. Ognuno di questi puntatori punta ad una lista cioè alle vere e proprie righe della matrice contenenti i valori. 

## 3D
Lo stesso ragionamento vale per le matrici 3d. 
- In python una matrice 3d ha la seguente forma:

    ```python
    [
        [
            [1, 2, 3], 
            [4, 5, 6], 
            [7, 8, 9]
        ],
        [
            [10, 11, 12], 
            [13, 14, 15], 
            [16, 17, 18]
        ]
    ]

    ```
    oppure (stessa cosa)
    ```python
    matrix_3d = [[[1, 2, 3], [4, 5, 6], [7, 8, 9]], [[10, 11, 12], [13, 14, 15], [16,   17, 18]]]
    ```
- In c++, se andiamo a printare la matrice puntata dal puntatore corrispondente otteniamo: 

    ```c++
    [ptr1, ptr2, ptr3, ptr4]
    ```
    Mentre nel caso bidimensionale ogni puntatore era assegnato ad una lista di valori, nel caso 3D ogni puntatore è assegnato ad un'altra lista di puntatori. 
    Quindi, per esempio,  `prt1` è assegnato ad una lista del tipo:

    ```c++
    [ptr1_1, ptr1_2, ptr1_3, ptr1_4]
    ```
    A loro volta ciascun puntatore sarà assegnato ad una lista contenente i veri valori della matrice. In altre parole ptr1_1, ptr1_2 ecc.. saranno puntatori associati alle righe della matrice 3D (fissato un piano di essa).

# Orientazione delle matrici in un array tridimensionale.
Consideriamo la matrice:
```c++
[
    [
        [0, 0, 0], 
        [0, 1, 0], 
        [0, 0, 0]
    ],
    [
        [0, 0, 0], 
        [0, 0, 0], 
        [0, 0, 0]
    ]
]
```
Le singole matrici, non hanno una vera e propria direzione ma sono io che decido il posizionamento dei piani in base a come voglio che la simulazione si evolva. 
Se per esempio ho la prima matrice 
```cpp
000
010
000
```
e la seconda 
```cpp
000
000
000
```

e volgio che l'1 si muova verso l'alto, scelgo che le segunti righe di codice rappresentino un movimento verso l'alto
```cpp
m[0][1][1] = 0
m[1][1][1] = 1
``` 

La prima matrice diventa 
```cpp
000
000
000
```
e la seconda 
```cpp
000
010
000
```
In questo caso ho interpretato le due matrici come poste una sopra l'altra e regolerò di conseguneza tutti gli altri movimenti tenendo conto della "convenzione" appena scelta del movimento in avanti.

Posso usare le stesse righe di codice
```cpp
m[0][1][1] = 0
m[1][1][1] = 1 
```
per indicare uno spostamento in avanti. Come nel caso precedente, la prima matrice sarà
```cpp
000
000
000
```
e la seconda 
```cpp
000
010
000
```
ma in questo caso interpreto le matrici come una dietro l'altra. 
In conclusione, date delle righe di codice che spostano gli elementi da una matrice all'altra, è il modo di interpretare gli spostamenti che decide se le matrici vanno interpretate una sopra l'altra o una dietro l'altra.

