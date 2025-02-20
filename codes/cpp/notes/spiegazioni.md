# Matrice neigh_count
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

### Esempio
Condiderando un caso 2D per semplicità, in cui ogni pixel contiene 5 cellule
- Pixel interno:
    - 8 pixel adiacenti × 5 cellule = **40**
- Pixel sul Bordo (non angolare, es. posizione (0,1)): 
    - **Calcolo senza correzione** : 5 pixel adiacenti × 5 cellule = **25** 
    - **Offset applicato:** +3 
    - **Totale:** 25 + 3 = **28**
- Pixel in Angolo (es. posizione (0,0))
    - **Calcolo senza correzione:** 3 pixel adiacenti × 5 cellule = **15** 
    - **Offset applicato:** +3 (per il bordo sinistro), +3 (per il bordo superiore)
    - Totale intermedio: 15 + 3 + 3 = **21** 
    - **Correzione per doppia compensazione:** -1 
    - **Totale Finale:** 21 - 1 = **20**

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
## Aggiornamento di neigh_count quando viene aggiunta una cellula
Quando aggiungo una cellula in (x, y, z) con il metodo `addCell`, è necessario aggiornare il valore di `neigh_count`. Questo aggiornamento serve a riflettere il fatto che, posizionando una nuova cellula, tutti i pixel adiacenti vedranno aumentato di 1 il loro "conteggio dei vicini".
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
# Sources: **fill_sources()**, **sourceMove()**, **rand_adj()**, **adj_helper()**
Aggiungere una quantità di glucosio e ossigeno al pixel di ogni sorgente e con una certa probabilità sposta la fonte di un pixel. 

L'idea è che, in media, la fonte si sposti una volta ogni 24 chiamate del metodo, il che, nel contesto della simulazione, equivale a spostarsi mediamente una volta al giorno. 

## Codice
Per ottenere questo potenziale spostamento ogni 24 si utilizzano le seguenti righe di codice:

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
- Successivamente si ha l'estrazione delle coordinate.

## Estrazione delle nuove coordinate
La source può muoversi verso il centro del tumore oppure in una direzione casuale. La probabilità di muoversi verso il centro del tumore è data:
```cpp
if (rand() % 50000 < CancerCell::count)
```
Ad esempio:
Se `CancerCell::count` è 1, la probabilità è $\frac{1}{50000} = 0.002%$
Se `CancerCell::count` è 25000, la probabilità è $\frac{25000}{50000} = 0.5 = 50%$

### Movimento verso il centro
Se questa condizione è rispettata, la nuova posizione (x, y, z) viene calcolata come segue:
Le coordinate sono compattate in un unico numero intero `newPos`
```cpp
int newPos = sourceMove(current->x, current->y, current->z);
```
il quale è nella forma
```
(z * xsize * ysize) + (x * ysize) + y
```
Le coordinate x, y e z vengono estratte con:

```cpp
int newZ = newPos / (xsize * ysize);
int rem = newPos % (xsize * ysize);
int newX = rem / ysize;
int newY = rem % ysize;
```
- Estrazione di z:
    ```cpp
    int newZ = newPos / (xsize * ysize);
    ```
    $$
    \text{NewPos} = (z \cdot x_{\text{size}} \cdot y_{\text{size}}) + (x \cdot y_{\text{size}}) + y
    $$

    $$
    z = \frac{z \cdot x_{\text{size}} \cdot y_{\text{size}}}{x_{\text{size}} \cdot y_{\text{size}}} + \frac{x \cdot y_{\text{size}}}{x_{\text{size}} \cdot y_{\text{size}}} + \frac{y}{x_{\text{size}} \cdot y_{\text{size}}}
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

    Il secondo e il terzo termini sono stati posti a 0 poichè sono entrambi < 1 e siamo in presenza di una divisione intera

- Estrazione di x

    ```cpp
    int rem = newPos % (xsize * ysize);
    int newX = rem / ysize;
    ```
    dove `%` è l'operazione modulo
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
    

- Estrazione di y: Il principio è lo stesso dei casi precedenti

#### coumpute_center()
Il metodo `compute_center()` calcola il centro del tumore come il **centro di massa** delle cellule cancerose presenti nella griglia. Ogni voxel contribuisce al centro calcolato in proporzione al numero di cellule cancerose che contiene e alla sua posizione nella griglia.

### Movimento casuale
Se la condizione non viene rispettata, si ha un movimento casuale della fonte tramite la funzione `rand_adj()`.

La funzione `rand_adj()` cerca un voxel adiacente a quello corrente esplorando tutti i possibili 26 voxel circostanti (escludendo il voxel centrale). Per ogni possibile offset lungo gli assi z, x e y, la funzione helper `adj_helper()` verifica se le coordinate candidate rientrano nei limiti della griglia (0 ≤ x < xsize, 0 ≤ y < ysize, 0 ≤ z < zsize). Se le coordinate sono valide, vengono codificate in un unico intero con la formula (uguale alla precedente):
```cpp
index = z * (xsize * ysize) + x * ysize + y
```

e aggiunte a una lista di posizioni candidate. Infine, `rand_adj()` seleziona casualmente una delle posizioni valide, garantendo così un movimento casuale affidabile della fonte quando non si muove verso il centro del tumore.

#### **`int& counter`** e **`pos[rand() % counter]`**
- `int& counter`: Stiamo definendo un alias, cioè un nome alternativo per un'altra variabile già esistente. In questo modo l'incremento è visibile anche nella funzione rand_adj che ha passato la variabile originale. Se lo passassimo per valore, la funzione opererebbe su una copia locale e le modifiche non verrebbero propagate all'esterno.

- `pos[rand() % counter]`: La funzione rand() restituisce un numero intero casuale compreso tra 0 e un valore massimo (tipicamente definito da RAND_MAX). Utilizzando l'operatore modulo % counter, otteniamo il resto della divisione del numero casuale per counter. Questo ci garantisce un valore compreso nell'intervallo [0, counter - 1], che è esattamente l'intervallo degli indici validi per l'array pos (che contiene counter elementi).

# cycle_cells()

### Iterazione con o senza for multipli
Nel file 2d, iterando su tutti i pixel della griglia per otternere le coordinate, si utilizza un singolo `for` per poi ottenere le coordinate utlizzando divisioni e moduli
```cpp
for (int x = 0; x < xsize * ysize; x++){
    int i = x / ysize; // Coordinates of the pixel
    int j = x % ysize;
```
Questo metodo è efficiente pure in 3D o è meglio usare tre `for`?
```cpp
// Iteriamo su tutti i voxel: k -> layer (z), i -> righe (x), j -> colonne (y)
for (int k = 0; k < zsize; k++) {
    for (int i = 0; i < xsize; i++) {
        for (int j = 0; j < ysize; j++) {
```
Dal punto di vista puramente computazionale, la differenza in termini di efficienza è generalmente trascurabile se il compilatore ottimizza bene il codice. Tuttavia, ci sono alcuni aspetti da considerare:

- Usare un ciclo che itera su un indice "appiattito" richiede di calcolare, ad ogni iterazione, la divisione e il modulo per ottenere le coordinate Queste operazioni aritmetiche, specialmente la divisione, possono essere relativamente costose se eseguite in milioni di iterazioni.

- Utilizzare tre cicli annidati esplicita direttamente le dimensioni della griglia, riducendo la necessità di calcoli aritmetici per la decodifica delle coordinate. Anche se ci sono più livelli di loop, il loro overhead è spesso compensato dal fatto che non devi eseguire divisioni e moduli in ogni iterazione, e il codice risulta più facilmente ottimizzabile dal compilatore.






