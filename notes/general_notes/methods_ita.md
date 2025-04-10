# List of Analyzed Methods

- `neigh_count` Matrix
- `change_neigh_counts()`
- `fill_sources()`
- `sourceMove()`
- `rand_adj()`
- `adj_helper()`
- `cycle_cells()`
- `rand_min()`
- `min_helper()`
- `diffuse()`
- `diffuse_helper()`
- `deleteDeadAndSort()`

# Matrice `neigh_count`
La matrice `neigh_counts` è un array che, per ogni pixel della griglia, memorizza il numero di cellule presenti nei pixel adiacenti escludendo quelle presenti nel pixel stesso. Viene usata per valutare la densità locale attorno a ciascun pixel (numero di cellule presenti nei pixel adiacenti).
## Voxel ai bordi 
I pixel al centro della griglia hanno potenzialmente 26 pixel adiacenti, mentre quelli ai bordi o agli angoli ne hanno di meno. Il codice aggiunge degli offset fissi ai bordi. In questo modo, si simula che ogni pixel abbia "virtualmente" 26 vicini, rendendo confrontabili i valori di densità indipendentemente dalla posizione nella griglia.
 
**Nota**: La correzione non ha l’obiettivo di aggiungere cellule virtuali, ma di normalizzare il valore del conteggio dei vicini.

### Conteggio voxel ai borrdi e vertici della matrice 
```
Layer 1             Layer 2
19 15 15 19         15  9  9 15
15  9  9 15          9  0  0  9
15  9  9 15          9  0  0  9
19 15 15 19         15  9  9 15

Layer 3             Layer 4
15  9  9 15         19 15 15 19
 9  0  0  9         15  9  9 15
 9  0  0  9         15  9  9 15
15  9  9 15         19 15 15 19

```

### Codice per l'offset ai bordi
Le seguenti righe di codice aggiungono l'offset ai bordi della griglia 3D. 
```cpp
    // Aggiunta off-set ai bordi della matrce
    for (int k = 0; k < zsize; k++) {         // Scorri i layer (asse z)
        for (int i = 0; i < xsize; i++) {     // Scorri le righe (asse x)
            for (int j = 0; j < ysize; j++) { // Scorri le colonne (asse y)
                // Determino le possibilità in base alla posizione
                int poss_z = (k == 0 || k == zsize - 1) ? 2 : 3;
                int poss_x = (i == 0 || i == xsize - 1) ? 2 : 3;
                int poss_y = (j == 0 || j == ysize - 1) ? 2 : 3;
                
                // Calcolo il prodotto delle possibilità:
                int prod = poss_z * poss_x * poss_y;
                // Calcolo il valore: valore = n_max - vicini = 27 - prod
                int valore = 27 - prod;
                
                // Poiché ogni elemento è inizializzato a 0, possiamo semplicemente assegnare:
                neigh_counts[k][i][j] = valore;
            }
        }
    }
```
## Aggiornamento di `neigh_count` quando viene aggiunta una cellula con `change_neigh_counts()`
Quando aggiungo una cellula in (x, y, z) con il metodo `addCell`, è necessario aggiornare `neigh_count`. Questo aggiornamento serve a riflettere il fatto che, posizionando una nuova cellula, tutti i pixel adiacenti vedranno aumentato di 1 il loro "conteggio dei vicini". Il metodo `change_neigh_counts()` si occupa di questo.
### Codice
```cpp
/**
 * Add a cell to a position on the grid
 *
 * @param x The x coordinate where we want to add the cell
 * @param y The y coordinate where we want to add the cell
 * @param z The z (layer) coordinate where we want to add the cell
 * @param cell The cell that we want to add to the CellList
 * @param type The type of the Cell
 */
void Grid::addCell(int x, int y, int z, Cell *cell, char type) {
    cells[z][x][y].add(cell, type,x, y, z);
    // Perchè change_neigh_counts? Vedi appunti
    change_neigh_counts(x, y, z, 1);
}
```
# Sources: **`fill_sources()`**, **`sourceMove()`**, **`rand_adj()`**, **`adj_helper()`**
Questi metodi si ocucpano di aggiungere una quantità di glucosio e ossigeno nei voxel in cui si trovano le sorgenti e spostare la fonti in altri voxel. 

L'idea è che, in media, la fonte si sposti una volta ogni 24 chiamate del metodo, il che, nel contesto della simulazione, equivale a spostarsi mediamente una volta al giorno (24 ore). 

## Codice

```cpp
void Grid::fill_sources(double glu, double oxy) {
    Source * current = sources -> head;
    while(current){ // We go through all sources
        glucose[current->z][current->x][current->y] += glu;
        oxygen[current->z][current->x][current->y] += oxy;
        if ((rand() % 24) < 1){ // The source moves on average once a day
            int newPos = sourceMove(current->x, current->y);
            current -> x = newPos / ysize;
            current -> y = newPos % ysize;
        }
        current = current -> next;
    }
}

int Grid::sourceMove(int x, int y, int z) {
    if (rand() % 50000 < CancerCell::count) { // Movimento verso il centro del tumore

        // Righe di codice
        ...
            
        // Codifica la nuova posizione in un singolo intero:
        // (z * xsize * ysize) + (x * ysize) + y
        return z * xsize * ysize + x * ysize + y;
    } else { 
        // Movimento in una direzione casuale (assicurarsi di avere la versione 3D di rand_adj)
        return rand_adj(x, y, z); // VEDI
    }
}
```
Dove: 
- `rand() % 24`: Genera un numero intero compreso tra 0 e 23.
- La condizione `(rand() % 24) < 1` è vera solo se il numero generato è `0`.
    - Questo accade con probabilità di $\frac{1}{24}$ (circa il 4.17% delle volte).
- Successivamente si ha l'**estrazione delle coordinate**.

## Estrazione delle nuove coordinate
La source può muoversi verso il centro del tumore oppure in una direzione casuale. La probabilità di muoversi verso il centro del tumore è data:
```cpp
if (rand() % 50000 < CancerCell::count)
```
Ad esempio:
- Se `CancerCell::count` è 1, la probabilità è $\frac{1}{50000} = 0.002%$
- Se `CancerCell::count` è 25000, la probabilità è $\frac{25000}{50000} = 0.5 = 50\%$

### Movimento verso il centro
Se questa condizione è rispettata, la nuova posizione (x, y, z) viene calcolata come segue:

```cpp
int newPos = sourceMove(current->x, current->y, current->z);
```
Le coordinate sono compattate in un unico numero intero `newPos` restituito dalla funzione `SourceMove()` il quale è nella forma:
```
(z * xsize * ysize) + (x * ysize) + y
```
Dove, le nuove coordinate x, y e z vengono estratte con:

```cpp
int newZ = newPos / (xsize * ysize);
int rem = newPos % (xsize * ysize);
int newX = rem / ysize;
int newY = rem % ysize;
```
- **Estrazione di z**:
    ```cpp
    int newZ = newPos / (xsize * ysize);
    ```
    $$
    \text{NewPos} = (z \cdot x_{\text{size}} \cdot y_{\text{size}}) + (x \cdot y_{\text{size}}) + y
    $$

    $$
    \text{newZ} = \frac{z \cdot x_{\text{size}} \cdot y_{\text{size}}}{x_{\text{size}} \cdot y_{\text{size}}} + \frac{x \cdot y_{\text{size}}}{x_{\text{size}} \cdot y_{\text{size}}} + \frac{y}{x_{\text{size}} \cdot y_{\text{size}}}
    $$
    I tre termini sono:

    - 
    
    $$
    \frac{z \cdot x_{\text{size}} \cdot y_{\text{size}}}{x_{\text{size}} \cdot y_{\text{size}}} = z
    $$
    - 
    $$
    \frac{x \cdot y_{\text{size}}}{x_{\text{size}} \cdot y_{\text{size}}} = \frac{x}{x_{\text{size}}} < 1
    $$ 

    siccome $x < x_{\text{size}}$
    
    - 
    $$
    \frac{y}{x_{\text{size}} \cdot y_{\text{size}}} < 1
    $$

    Il secondo e il terzo termini sono stati posti a 0 poichè sono entrambi < 1 e siamo in presenza di una divisione intera. Rimane quindi:

    $$
    \text{newZ} = z
    $$

- **Estrazione di x**:

    ```cpp
    int rem = newPos % (xsize * ysize);
    int newX = rem / ysize;
    ```
    dove `%` è l'operazione modulo.
    - **rem**: 

        Definiamo:
        $$
        M = xsize \times ysize
        $$
        Possiamo riscrivere la formula di codifica come:
    
        $$
        \text{newPos} = z \times M + (x \times ysize + y)
        $$
    
        Ricordiamo la proprietà del modulo per somme:
    
        $$
        (a + b) \mod M = \left((a \mod M) + (b \mod M)\right) \mod M
        $$
    
        Nel nostro caso poniamo:
        - $a = z \times M$
        - $b = x \times \text{ysize} + y$
    
        Quindi:
    
        $$
        \text{newPos} = a + b
        $$
    
        Applicando la proprietà del modulo otteniamo:
    
        $$
        \text{newPos} \mod M = \left((a \mod M) + (b \mod M)\right) \mod M
        $$
    
        **Analizziamo i due termini:**
    
        1. **Termine $a = z \times M$:**
    
            Poiché a è un multiplo esatto di M, abbiamo:
    
            $$
            a \mod M = (z \times M) \mod M = 0
            $$
    
            In altre parole, data la divisione, abbiamo $\text{quoziente} = z$ e $\text{resto} = 0$. 
    
        2. **Termine $b = x \times \text{ysize} + y$:**
        
            Siccome $b < M$, la divisione fornirà $\text{quoziente} = 0$ e $\text{resto} = b$. Come accade quando si svolgono le operazioni in colonna.
    
            **Come mai $b < M$?**
    
            Il massimo valore che b può assumere si ottiene quando \( x = xsize - 1 \) e \( y = ysize - 1 \). In tal caso:
           
            $$
            (xsize - 1) \times ysize + (ysize - 1) = xsize \times ysize - 1 < M
            $$
        
        Combinando i due risultati:

        $$
        \text{newPos} \mod M = (0 + b) \mod M = b = x \times \text{ysize} + y
        $$

        
    - **newX**:
        $$
        \text{newX} = \frac{\text{Rem}}{y_{\text{size}}} = \frac{x \cdot y_{\text{size}}}{y_{\text{size}}} + \frac{y}{y_{\text{size}}}
        $$
        I due termini sono:
        
        1.
        $$
        \frac{x \cdot y_{\text{size}}}{y_{\text{size}}} = x
        $$
        2.
        $$
        \frac{y}{y_{\text{size}}} < 1 
        $$
        
        Il secondo termine viene posta a zero poichè abbaimo una divisione intera. Segue che:
        $$
        \text{newX} = x
        $$
    

- **Estrazione di y**: Il principio è lo stesso dei casi precedenti


### Movimento casuale
Se la condizione non viene rispettata, si ha un movimento casuale della fonte tramite la funzione `rand_adj()`.

La funzione `rand_adj()` cerca un voxel adiacente a quello corrente esplorando tutti i possibili 26 voxel circostanti (escludendo il voxel centrale). Per ogni possibile offset lungo gli assi z, x e y, la funzione helper `adj_helper()` verifica se le coordinate candidate rientrano nei limiti della griglia (0 ≤ x < xsize, 0 ≤ y < ysize, 0 ≤ z < zsize). Se le coordinate sono valide, vengono codificate in un unico intero con la formula (uguale alla precedente)
```cpp
index = z * (xsize * ysize) + x * ysize + y
```

e aggiunte a una lista di posizioni candidate. Infine, `rand_adj()` seleziona casualmente una delle posizioni valide, garantendo così un movimento casuale della fonte.
compilatore.

# `cycle_cells()`

La funzione `cycle_cells()` ha il compito di avanzare di un'ora il ciclo vitale di tutte le cellule presenti nella griglia tridimensionale. 

## Funzionamento

- Viene creata una lista temporanea `toAdd` per memorizzare le nuove cellule generate nel ciclo.
    ```cpp
    void Grid::cycle_cells() {
        CellList *toAdd = new CellList();
    ```
- La funzione itera attraverso tutti i voxel della griglia nelle tre dimensioni `(z, x, y)`.
- Il puntatore `current` viene inizializzato alla testa della lista di cellule presenti nel voxel corrente.
    ```cpp
        for (int k = 0; k < zsize; k++) {
            for (int i = 0; i < xsize; i++) {
                for (int j = 0; j < ysize; j++) {
                    CellNode *current = cells[k][i][j].head;
    ```

- Ogni cellula del voxel esegue il proprio ciclo con il metodo `cycle()`, che restituisce la quantità di nutrienti consumata e il possibile tipo di nuova cellula.
    ```cpp
                    while (current) {
                        cell_cycle_res result = current->cell->cycle(
                            glucose[k][i][j],
                            oxygen[k][i][j],
                            neigh_counts[k][i][j] + cells[k][i][j].size
                        );
    ```

- I valori di glucosio e ossigeno nel voxel vengono aggiornati sottraendo i consumi della cellula.

    ```cpp
                        glucose[k][i][j] -= result.glucose;
                        oxygen[k][i][j] -= result.oxygen;

    ```
- Se il ciclo ha generato una nuova cellula sana (`'h'`), viene determinata una posizione adatta con `rand_min()` e la nuova cellula viene aggiunta alla lista `toAdd`.
- Se non c'è spazio disponibile, la cellula entra in stato di quiescenza (`sleep()`).
    ```cpp
                        if (result.new_cell == 'h') {
                            int downhill = rand_min(i, j, k, 5);
                            if (downhill >= 0) {
                                int newZ = downhill / (xsize * ysize);
                                int rem = downhill % (xsize * ysize);
                                int newX = rem / ysize;
                                int newY = rem % ysize;
                                toAdd->add(new HealthyCell('q'), 'h', newX, newY, newZ);
                            } else {
                                current->cell->sleep();
                            }
                        }
    ```

- Se la cellula generata è cancerosa (`'c'`), viene posizionata in un voxel adiacente usando `rand_adj()`.
    ```cpp
                        if (result.new_cell == 'c') {
                            int downhill = rand_adj(i, j, k);
                            if (downhill >= 0) {
                                int newZ = downhill / (xsize * ysize);
                                int rem = downhill % (xsize * ysize);
                                int newX = rem / ysize;
                                int newY = rem % ysize;
                                toAdd->add(new CancerCell('1'), 'c', newX, newY, newZ);
                            }
                        }
    ```
- Si passa alla cellula successiva nella lista del voxel.
    ```cpp
                        current = current->next;
                    }
    ```
- Dopo aver processato tutte le cellule nel voxel:
  - Le cellule morte vengono eliminate con `deleteDeadAndSort()`.
  - Il conteggio dei vicini viene aggiornato con `change_neigh_counts()`.
    ```cpp
                    int init_count = cells[k][i][j].size;
                    cells[k][i][j].deleteDeadAndSort();
                    change_neigh_counts(i, j, k, cells[k][i][j].size - init_count);
                }
            }
        }
    ```
- Infine, tutte le nuove cellule vengono aggiunte alla griglia con `addToGrid(toAdd)`.
    ```cpp
        addToGrid(toAdd);
    }
    ```
## `rand_min()` and `min_helper()`
Quando una cellula si divide o deve spostarsi, bisogna trovare un nuovo voxel nella griglia 3D dove posizionarla.
L'idea è scegliere un voxel vicino che abbia il minor numero di cellule, così la nuova cellula avrà spazio per crescere.

Questo viene fatto in due passaggi:

- `rand_min()` scansiona i 26 voxel vicini per trovare quelli con meno cellule.
- `min_helper()` verifica se un singolo voxel è un buon candidato e aggiorna la lista dei candidati.

**Tutte le posizioni sono codificate nella formula `z * xsize * ysize + x * ysize + y`.** **`pos[]` conterrà la posizione del voxel avente il minor numero di cellule e altre posizioni avente lo stesso numero minimo di cellule.**

### `rand_min()`
Dato un singolo voxel, la funzione analizza tutti i vicini di quest'ultimo (escludendo il voxel stesso). Per ognuno dei vicini viene eseguita la funzione `min_helper()`. 

Quello che si ottiene alla fine è un vettore `pos` contenente tutti i possibili candidati. Se `curr_min < max`, cioè se la densità cellulare è minore di un threshold, viene scelto casualmente uno degli elementi di `pos` altrimenti la funzione returna `-1`.

### Variabili
- `max`: Soglia di densità (threshold) massima da considerare per poter scegliere casualmente una delle posizioni.
- `counter`: Serve a contare e gestire il numero di posizioni valide trovate nella funzione `min_helper()`, in modo che `rand_min()` possa selezionarne una casualmente. 

- `pos`: Memorizza le posizione dei voxel con densità minima. `pos` è dichiarato in `rand_min()` e passato come puntatore in `min_helper()`.
 

### `min_helperI()`
- Controlla se il vicino al voxel consiederato dalla funzione `rand_min()`, si trova all'interno della griglia
- Se il voxel ha una densità minore della precedente `curr_min`, counter viene azzerato e impostato a 1, perché il voxel diventa il nuovo miglior candidato.
- Se il voxel ha la stessa densità di `curr_min`, viene aggiunto all'array `pos[]` e `counter` viene incrementato.

# `diffuse()` and `diffuse_helper()` 
## `diffuse()`
Simula la diffusione di ossigeno e glucosio all'interno della griglia, eseguendo due chiamate alla funzione `diffuse_helper()`, una per ciascuna sostanza. Successivamente, vengono scambiate le matrici `glucose` e `glucose_helper` (e analogamente `oxygen` con `oxygen_helper`). Questo passaggio è necessario perché, al termine della diffusione, le matrici di supporto contengono i valori aggiornati. Pertanto, è essenziale effettuare lo swap affinché le matrici principali (`glucose` e `oxygen`) riflettano i nuovi dati.

## `diffuse_helper()` 
Esegue la simulazione effettiva della diffusione di una sostanza, aggiornando i valori di glucosio e ossigeno in ogni voxel. Ogni voxel contiene una quantità della sostanza, e a ogni iterazione una frazione di tale quantità viene trasferita ai voxel adiacenti, simulando così il processo di diffusione.

Il metodo accetta in ingresso i seguenti parametri:

- `diff_factor`: coefficiente di diffusione che determina la frazione di sostanza da distribuire ai voxel adiacenti;
- `src`: matrice contenente i valori iniziali della sostanza in ciascun voxel;
- `dest`: matrice in cui verranno memorizzati i nuovi valori dopo la diffusione.

In pratica, per ogni voxel, una parte della sostanza viene trattenuta localmente, mentre il resto viene distribuito ai vicini, tenendo conto del coefficiente di diffusione `diff_factor`.

### Processo di diffusione
Si itera su ogni voxel della griglia e per ciscuno di essi:
1. Ogni voxel trattiene una frazione della sua quantità iniziale. Questo viene calcolato come:
   ```cpp
   dest[k][i][j] = (1.0 - diff_factor) * src[k][i][j];
   ```
   Se, ad esempio, `diff_factor` è `0.4`, il voxel conserva il 60% della quantità iniziale.

2. La parte che non viene trattenuta viene suddivisa equamente nei 26 vicni. Quindi fissato un voxel, si itera sui vicini in modo da controllare la diffusione in questi ultimi.
    - Ogni vicino contribuisce con:
        ```cpp
        (diff_factor / 26.0) * src[neighbor]
        ```
3. Somma dei contributi. Il valore finale in ogni voxel `dest[k][i][j]` è dato dalla somma di:
    - Il residuo del voxel stesso, cioè $(1- \text{diff-factor})\cdot \text{src[k][i][j]}$
    - Tutti i contributi diffusi dai suoi 26 vicini, ognuno dei quali fornisce un valore di $\frac{\text{diff-factor}}{26}\cdot \text{src}_{\text{neighbor}}$

# `deleteDeadAndSort()`

Il metodo `deleteDeadAndSort()` si occupa di "ripulire" la lista delle cellule, eliminando i nodi contenenti cellule morte e riorganizzando la lista in modo che i nodi con cellule vive siano correttamente collegati. In particolare, il ciclo `while(current)` analizza ogni nodo della lista ed esegue operazioni differenti a seconda dello stato della cellula:

## Operazioni nel ciclo `while(current)`

1. **Nodo con cellula morta:**  
   - Se `current->cell->alive` è falso, la cellula è morta.  
   - La cellula e il relativo nodo vengono eliminati (con `delete`), e si aggiornano i contatori (ad esempio, per le cellule di tipo 'o' o 'c').  
   - Il puntatore `current` viene aggiornato al nodo successivo.

2. **Primo nodo vivo (head non ancora impostata):**  
   - Quando viene incontrato il primo nodo con una cellula viva, viene impostato come **testa** della lista (`head = current`) e anche come **coda** (`tail = current`).  
   - Si imposta `previous_next_pointer` per riferirsi al campo `next` di questo nodo, in modo da poter collegare agevolmente i successivi nodi vivi.  
   - Si segna che la testa è stata trovata (`found_head = true`) e si passa al nodo successivo.

3. **Nodi vivi successivi:**  
   - Per ogni ulteriore nodo con cellula viva, il metodo aggiorna la **coda** (`tail = current`) e collega il nodo corrente al precedente vivo tramite `*previous_next_pointer = current`.  
   - Il `previous_next_pointer` viene aggiornato per puntare al campo `next` del nodo corrente, così da preparare il collegamento per il prossimo nodo vivo.  
   - Infine, si passa al nodo successivo.

Al termine del ciclo, se nessun nodo vivo è stato trovato (ossia, la lista è completamente vuota), il metodo imposta `head` e `tail` a `nullptr` e verifica che il contatore `size` sia 0. Se almeno un nodo vivo è stato trovato, il campo `next` dell'ultimo nodo (tail) viene impostato a `nullptr` per terminare correttamente la lista.

## Esempio Pratico

Immaginiamo una lista di 4 nodi con le seguenti cellule:

- **Nodo A:** Cellula viva  
- **Nodo B:** Cellula morta  
- **Nodo C:** Cellula viva  
- **Nodo D:** Cellula morta

### Iterazione 1:
- **Nodo A (vivo):**
  - Poiché è il primo nodo vivo incontrato (`found_head` è false), **A** diventa la nuova testa e la coda della lista.
  - Viene impostato `previous_next_pointer` per puntare a `A->next`.
  - Si segna `found_head = true` e si passa al nodo successivo.

### Iterazione 2:
- **Nodo B (morto):**
  - La cellula di **B** è morta, quindi il nodo **B** viene eliminato.
  - Il puntatore `current` passa al nodo successivo, **C**.

### Iterazione 3:
- **Nodo C (vivo):**
  - Siccome la testa è già stata trovata, si collega il nodo **C** al precedente nodo vivo.  
  - L'istruzione `*previous_next_pointer = C` fa sì che `A->next` punti a **C**.
  - Si aggiorna `tail = C` e `previous_next_pointer` viene puntato a `C->next`.
  - Si passa al nodo successivo, **D**.

### Iterazione 4:
- **Nodo D (morto):**
  - La cellula di **D** è morta, quindi **D** viene eliminato.
  - Il ciclo termina poiché non ci sono altri nodi.

**Risultato finale:**  
La lista viene riorganizzata in modo tale da contenere solo i nodi vivi, collegati come **A → C**. L’aggiornamento dei puntatori garantisce che la lista sia corretta e che non rimangano "buchi" nella catena.

Questo meccanismo, grazie all'uso di `previous_next_pointer`, permette di gestire in maniera efficiente e sicura la rimozione dei nodi, evitando la necessità di scorrere nuovamente l'intera lista per ricollegare i nodi vivi.