# Codici di test
## Matrice neigh_counts 2D
FUNZIONAMENTO CORRETTO ✅
### Test code
```cpp
// FILE NAME: test_grid.cpp
#include <iostream>
#include "grid.h"  // Assicurati che questo header contenga la dichiarazione della classe Grid

int main() {
    // Inizializza la griglia 4x4 senza fonti (sources_num = 0)
    Grid grid(4, 4, 0);


    // Stampiamo a schermo i valori di neigh_counts:
    std::cout << "Matrice neigh_counts:" << std::endl;
    for (int i = 0; i < 4; i++) {
        for (int j = 0; j < 4; j++) {
            std::cout << grid.neigh_counts[i][j] << " ";
        }
        std::cout << std::endl;
    }
    
    return 0;
}
```
### Output

```
Output (verificato):
5 3 3 5
3 0 0 3
3 0 0 3
5 3 3 5
```
### Nota 
Ogni elemento della matrice viene inizializzato a 0 grazie alle parentesi `()` nella seguente riga di codice nel file `grid.cpp`
```cpp
neigh_counts[i] = new int[ysize]();  // Le parentesi "()" inizializzano tutti gli elementi a 0
```
### Processi eseguiti
- Sostituzione di `grid_3d.cpp` con `grid.cpp` nel file `CMakeLists.txt`per evitare problemi di linking nel compilatore siccome il compilatore trovala la stessa classe definita due volte. 
- Spostata la definizione di `neigh_counts` da `private` a `public` nel file `grid.h` in modo da consentire al file `test_grid.cpp` di accederci.

## Matrice neigh_counts 3D
FUNZIONAMENTO CORRETTO ✅
### Test code
```cpp
int main() {
    // Matrice 4x4x4
    int zsize = 4;
    int xsize = 4;
    int ysize = 4;
    // Crea una griglia 3x3x3 senza sorgenti (sources_num = 0)
    Grid grid(zsize, zsize, ysize, 0);

    // Seleziona il layer da stampare: z = 1
    int z_layer = 3;
    cout << "Stampa della matrice neigh_counts per il layer z = " << z_layer << ":\n";
    
    // Itera sulle righe (x) e colonne (y) del layer scelto e stampa il valore di ciascun elemento
    for (int i = 0; i < xsize; i++) {
        for (int j = 0; j < ysize; j++) {
            cout << grid.neigh_counts[z_layer][i][j] << "\t";
        }
        cout << "\n";
    }

    return 0;
}
```
### Output
```
Layer z = 0 e z = 3

15  9  9 15
 9  0  0  9
 9  0  0  9
15  9  9 15

Layer z = 0 e z = 3

15  9  9 15
 9  0  0  9
 9  0  0  9
15  9  9 15
```
## Sources
FUNZIONAMENTO CORRETTO ✅
### Test code 
Stampa a schermo il numero size (pre-impostato) di oggetti Source in SourceList e le rispettive cordinate x, y, z.
```cpp
// test_grid.cpp
#include <iostream>
#include "grid_3d.h"  // Assicurarsi che il file grid_3d.h sia nella stessa directory o nel path di include

using namespace std;

int main() {
    int zsize = 4;
    int xsize = 4;
    int ysize = 4;

    int source_num = 4;

    Grid grid(zsize, zsize, ysize, source_num);

    // Stampo il numero di oggetti Source in SourceList
    cout << "size = " << grid.sources -> size << "\n\n";
    
    Source* current = grid.sources -> head;
    while (current != nullptr) {
        // Qui puoi accedere alle proprietà del nodo corrente, ad esempio:
        std::cout << "Source at:"  << "\n"
         << "z  = " << current -> z << ", "
         << "x =  " <<  current -> x << ", "
         << "y = " << current -> y << std::endl;

        // Passa al nodo successivo
        current = current->next;
    }
}
```
### Output
```
size = 4

Source at:
z  = 3, x =  1, y = 2
Source at:
z  = 3, x =  3, y = 1
Source at:
z  = 2, x =  1, y = 0
Source at:
z  = 1, x =  3, y = 2
```
### Processi eseguiti
- Spostato in `public` l'attributo `sources` di `SourceList` in `grid_3d.h` 

## change_neigh_counts
FUNZIONAMENTO CORRETTO ✅
### test_code
```cpp
// test_grid.cpp
#include <iostream>
#include "grid_3d.h"  // Assicurarsi che il file grid_3d.h sia nella stessa directory o nel path di include

using namespace std;

int main() {
    int xsize = 4;
    int ysize = 4;
    int zsize = 4;
    int source_num = 4;

    // Costruiamo la griglia; attenzione all'ordine dei parametri:
    // Grid(int xsize, int ysize, int zsize, int sources_num)
    Grid grid(xsize, ysize, zsize, source_num);

    // Esempio: aggiorno i contatori dei vicini del voxel (2,2,2) incrementandoli di 1
    grid.change_neigh_counts(0, 3, 3, 1);

    // Stampo a schermo i layer (asse z) della matrice neigh_counts:
    for (int z = 0; z < zsize; z++) {
        cout << "Layer z = " << z << ":\n";
        for (int x = 0; x < xsize; x++) {
            for (int y = 0; y < ysize; y++) {
                cout << grid.neigh_counts[z][x][y] << "\t";
            }
            cout << "\n";
        }
        cout << "\n";
    }

    return 0;
}
```
### Output
Il codice stampa i vari layer della matrice 3D in modo da poter verificare ad occhio l'aggiunta del valore `val` nei voxel "vicini".
### Processi eseguiti
- Sostituzione di `grid_3d.cpp` con `grid.cpp` nel file `CMakeLists.txt`per evitare problemi di linking nel compilatore siccome il compilatore trovala la stessa classe definita due volte. 
- Spostata la definizione di `neigh_counts` e `neigh_counts` da `private` a `public` nel file `grid.h` in modo da consentire al file `test_grid.cpp` di accederci.
## fill_sources() and sourceMove()
Si considera una sola sorce (`SourceList` con un solo nodo) in modo da poter seguire il suo movimento all'interno della griglia di glucose o oxygen. 
L'algoritmo di test è il seguente:

```
Start
  |
  v
Stampo della posizione iniziale (In SourceList: add)
  |
  v
Calcolo centro del tumore
  |
  v
Esecuzione di fill_sources()
  |
  |-- Riempimento della matrice
  |-- Movimento della source
  |-- Movimento casuale o verso il centro del tumore
  |-- Calcolo delle nuove posizioni
  |
  v
Stampa dei nuovi valori della matrice
  |
  v
Stampa le nuove posizioni
  |
  v
End
```
**NOTA**: Siccome, prima riempio la matrice e poi calcolo le nuove posizioni, nella matrice di output, visualizzo il movimento precedente (o la posizione iniziale de `fill_source()` è il primo che viene eseguito). 

### Test code
```cpp
#include <iostream>
#include "grid_3d.h" 

#include <ctime> // DA RIMUOVERE

using namespace std;

// Funzione che stampa il layer "layer" della matrice 3D
// Parametri:
// - matrix: la matrice 3D (ad es. glucose o oxygen)
// - layer: il numero (indice) del layer da stampare
// - xsize: il numero di righe del layer
// - ysize: il numero di colonne del layer

void printMatrixLayer(double*** matrix, int layer, int xsize, int ysize) {
    cout << "Layer " << layer << ":\n";
    for (int i = 0; i < xsize; i++) {
        for (int j = 0; j < ysize; j++) {
            cout << matrix[layer][i][j] << "\t";
        }
        cout << "\n";
    }
    cout << "\n";
}

int main() {

    // Strand serve per poter generare numeri casuali con un seed diveso ogni volta
    // che si lancia il programma
    // Da inserire in una funzione (main in questo caso)
    std::srand(static_cast<unsigned int>(std::time(nullptr))); 

    int xsize = 4;
    int ysize = 4;
    int zsize = 4;
    int source_num = 1;

    // Creazione della griglia
    Grid grid(xsize, ysize, zsize, source_num);

    // Calcolo centro del tumore
    grid.compute_center();

    // Per quante volte muovo la source
    for (int i = 0; i<3; i++){
        // Esecuzione del metodo fill_sources (che internamente esegue anche sourceMove)
        grid.fill_sources(5.0, 10.0);

        // Stampa dopo l'aggiornamento
        cout << "Dopo fill_sources (prima del nuovo movimento):" << endl;
        for(int i = 0; i < zsize; i++){
            printMatrixLayer(grid.glucose, i, xsize, ysize);
        }
        
        // Scorro nella source list con un solo elemento per stampare
        // la nuova posizione della fonte
        Source * current = grid.sources->head;
        while (current) { 
            cout << "\nPosizione dopo movimeto" << endl;
            cout << "newX = " << current->x << endl;
            cout << "newY = " << current->y << endl;
            cout << "newZ = " << current->z << "\n" << endl;   

            current = current->next;
        }
    }

    return 0;
}
```

### Cambiamenti nel codice
- Sostituzione di `if ((rand() % 24) < 1)` con `if (true)` in `fill_sources()`. Siccome il movimento della fonte avviene una volta ogni 24 ore, imponendo la condizione a `true` ci assicuriamo che lo spostamento avvenga ogni volta che eseguiamo il programma e non con una probabilità di 1/7.

- Sostituzione della probabilità fornita dalla conzione `if (rand() % 50000 < CancerCell::count)` con `if (rand() % 2 == 0)` in modo che si abbia una probabilità del 50% sia per il movimetno verso il centro che per un movimento casuale.

- Aggiunta delle seguenti righe di codice in `SourceList::add` per la stampa della posizione iniziale della source:
    ```cpp
    cout << "Posizione iniziale" << endl;
    cout << "x = " << x << endl;
    cout << "y = " << y << endl;
    cout << "z = " << z << endl;
    ```
- Spostamento delle seguenti variabili da `private` a `public` nel file grid_3d.h 
    - `glucose`
    - `oxygen`
    - `sources`