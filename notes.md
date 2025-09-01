## Compilazione libreria CellSimLib
1. Crea e usa una cartella di build:
    ```bash
    mkdir build
    cd build
    cmake ..
    ```
2. Compilazione:
    1. Utilizzando comando make:
        - Compilazione di libreria e demo: `make`
        - Compilazione solo della libreria `CellSimLib`: `make cell_sim`
        - Compilazione del demo (`main.cpp`): `make CellSimDemo`
    
        I file risultanti verranno collocati in lib/ (libreria) e bin/ (eseguibile demo).
    
    2. Compilazione del solo target `cell_sim`: 
    `cmake --build . --target cell_sim`

Differenza tra i comandi: Entrambi i comandi compilano il target cell_sim, ma lo fanno in modo diverso:
- `cmake --build . --target cell_sim`: Make agisce da “wrapper” e invoca il sistema di build corretto per la piattaforma e il generatore scelti (Make, Ninja, MSBuild, ecc.). È quindi portabile e usa automaticamente le impostazioni di configurazione di CMake.
- `make cell_sim`: Chiama direttamente make e richiede che nella directory di build ci sia un Makefile generato con il generatore “Unix Makefiles”. Funziona solo se il generatore è Make; su altri generatori (Ninja, Visual Studio, …) non funzionerebbe.

In pratica, con Makefile già generati il risultato della compilazione è lo stesso; cmake --build è semplicemente più portabile e indipendente dal sistema di build sottostante.

### getattr()
`getattr(obj, nome_attr, valore_default)` è una funzione built-in di Python che permette di accedere dinamicamente a un attributo di un oggetto:

- obj → l’oggetto su cui cercare l’attributo (qui self, cioè l’ambiente).

- nome_attr → il nome (stringa) dell’attributo da leggere.

- valore_default (opzionale) → il valore da restituire se l’attributo non esiste.

Se l’attributo c’è → viene restituito il suo valore.
Se non c’è → viene restituito il valore_default passato.

### np.asarray()
`numpy.asarray(obj, dtype=..., order=...)` è una funzione di NumPy che converte l’oggetto obj in un array NumPy (ndarray).

- Se obj è già un array NumPy → lo restituisce quasi “così com’è” (senza fare una copia inutile).

- Se obj è una lista, tupla, ecc. → lo converte in un array NumPy.

- Con dtype puoi forzare il tipo degli elementi (qui np.float32).

# Possibili errori
Nel distruttore dell'oggetto controller in controller.cpp
```cpp
/**
 * Destructor of the controller
 */
Controller::~Controller() {
    if (self_grid)
        delete grid;
    if(oar)
        delete oar;
}
```
FORSE da sostituire self_grid con grid