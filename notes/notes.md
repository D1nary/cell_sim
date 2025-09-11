## Compilazione libreria CellSimLib
1. Crea e usa una cartella di build:
    ```bash
    mkdir build
    cd build
    cmake ..
    ```
2. Compilazione:
    1. Utilizzando comando make:
        - Compilazione di libreria, demo e file di binding: `make`
        - Compilazione solo della libreria `CellSimLibz`: `make cell_sim`
        - Compilazione del demo (`main.cpp`): `make CellSimDemo`
        - Compilazione del binding (`binding.cpp`): `make cell_sim_py`
        
    
        I file risultanti verranno collocati in lib/ (libreria) e bin/ (eseguibile demo).
    
    2. Utilizzo comando cmake generico
        - Compilazione del solo target `cell_sim`: `cmake --build . --target cell_sim`
        - Compilazione del solo binding: cmake --build . --target cell_sim_py -j (da verificare)

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

---

# Deep Copy
Nel file grid.cpp la deep copy è stata implementata per le classe CellList, SourceList e Grid. DI seguito è spiegato il caso della classe CellList

## Cosa significa *deep copy* in questo contesto

* Una **shallow copy** (copia superficiale) copia solo i puntatori: sia l’oggetto originale che la copia puntano alle stesse celle in memoria → modificare uno modifica anche l’altro.
* Una **deep copy** invece crea **nuove istanze indipendenti**: la copia possiede le proprie `Cell`, perciò gli oggetti originali e copiati non condividono più i dati.


## Implementazioni tipiche viste nei file

Nel file `grid.h`, la classe `CellList` è stata modificata per includere:

* **Copy constructor**

  ```cpp
  CellList(const CellList& other);
  ```

* **Copy assignment operator**

  ```cpp
  CellList& operator=(const CellList& other);
  ```

* **Destructor** per liberare memoria allocata dinamicamente.


## Copy constructor (`CellList(const CellList& other)`)

Questo costruttore viene chiamato quando crei una nuova lista a partire da un’altra, ad esempio:

```cpp
CellList list2 = list1;   // chiama il copy constructor
```

Funzionamento:

* Alloca nuova memoria per ogni `Cell*` contenuta in `other`.
* Clona ogni cella (di solito con `new Cell(*otherCell)`).
* Inserisce i nuovi puntatori nella nuova lista.

➡ Risultato: `list2` ha celle nuove, non condivise con `list1`.


## Copy assignment operator (`operator=(const CellList& other)`)

Questo operatore entra in gioco quando assegni una lista già esistente ad un’altra:

```cpp
CellList list2;
list2 = list1;   // chiama operator=
```

Funzionamento:

1. **Protezione auto-assegnazione**: se stai facendo `list1 = list1;` non deve fare nulla.
   Tipico pattern:

   ```cpp
   if (this == &other) return *this;
   ```
2. **Pulizia risorse attuali**: libera la memoria delle celle già presenti in `this`.
3. **Copia profonda**: come nel copy constructor, clona tutte le celle da `other`.

➡ Risultato: dopo l’assegnazione, `list2` è indipendente da `list1`.


## Distruttore (`~CellList()`)

Serve a garantire che tutta la memoria allocata per le celle venga deallocata correttamente:

```cpp
~CellList() {
    for (Cell* c : cells) delete c;
}
```

In questo modo eviti **memory leak**.


## Schema riassuntivo

* **Costruttore di copia** → crea una nuova lista clonando celle da un’altra lista.
* **Operatore di assegnazione** → sostituisce le celle correnti con copie di un’altra lista.
* **Distruttore** → pulisce la memoria allocata.

Questi tre insieme implementano la cosiddetta **“Rule of Three”** in C++.


## Due vie per il deep copy

### 1. **Copy constructor**

Si attiva quando crei un nuovo oggetto a partire da uno già esistente:

```cpp
CellList a;         // lista originale
CellList b = a;     // copy constructor → deep copy
CellList c(a);      // stessa cosa
```

🔹 Qui viene invocato il **costruttore di copia**.
Risultato: `b` e `c` sono copie indipendenti di `a`.

### 2. **Copy assignment operator**

Si attiva quando assegni a un oggetto già esistente il contenuto di un altro:

```cpp
CellList a;
CellList b;
// ... magari b ha già delle celle dentro
b = a;  // copy assignment operator → deep copy
```

🔹 In questo caso:

1. `b` prima libera la memoria delle celle che già possiede.
2. Poi ricrea copie profonde delle celle di `a`.

Risultato: `b` diventa una copia indipendente di `a`.

### 🔑 Differenza chiave

* **Copy constructor** → usato nella fase di **inizializzazione** (quando stai creando un oggetto nuovo).
* **Copy assignment** → usato nella fase di **assegnazione** (quando l’oggetto esiste già e deve diventare uguale a un altro).

---

## Differenza tra puntatore e alias
Prendiamo per esempio un oggetto `SourceList`
1. SourceList* (puntatore a SourceList)

    - È una variabile che contiene l’indirizzo di un oggetto di tipo `SourceList`.
    - Può essere `nullptr` (cioè non puntare a niente).
    - Può essere riassegnato per puntare a un altro oggetto.
    - Per accedere al contenuto serve la dereferenziazione *.

2. SourceList& (reference a SourceList)

    - È un alias (riferimento) a un oggetto esistente.
    - Deve essere inizializzata subito e non può essere "nulla".
    - Dopo l’inizializzazione, non può essere cambiata per riferirsi a un altro oggetto.
    - Si usa come se fosse l’oggetto stesso (non serve `*` né `->`).

3. Differenza chiave

- Puntatore (`*`) → variabile che contiene un indirizzo; gestione più "manuale".
- Reference (`&`) → un altro nome per l’oggetto; più sicura, non può essere nulla né riassegnata.

4. Dato un puntatore `a` (per esempio un puntatore ad un oggetto `SourceList*`) e una reference `b` (`SourceList&`), se scriviamo `&b` si ottiene l’indirizzo in memoria dell’oggetto referenziato da `b`, quindi il tipo è un puntatore (`SourceList*`) come `a`.

## "this" operator
```cpp
SourceList& SourceList::operator=(const SourceList& other){
    if(this != &other){
        clear_();
        copy_from_(other);
    }
    return *this;
}
```
`this` in C++ è un puntatore all’oggetto corrente, cioè dentro un metodo di istanza (SourceList::operator=) rappresenta l’indirizzo dell’oggetto su cui il metodo è stato invocato. Siccome `this` è un puntatore, il suo tipo è `SourceList*`.

- Se abbiamo due oggetti di tipo `SourceList`:
    '''cpp
    SourceList a;
    SourceList b;
    a = b;
    '''
    - `this` → è un puntatore all’oggetto su cui viene chiamato il metodo, cioè `a` in questo caso.
    - `other` → è il parametro passato, quindi una reference a `b`

- Come mai posso confrontare `this` e `&other` in `if(this != &other)`? Perchè `this` è un puntatore ad un oggetto `SourceList` (`SourceList*`) mentre `&other` è l’indirizzo in memoria (quindi un puntatore) dell’oggetto referenziato da `other` (`other` referenzia un oggetto di tipo `SourceList`), quindi il tipo è `SourceList*`.

- Come mai si fa `return *this` se il metodo deve ritornare una reference come specificato nella dichiarazione (`SourceList& SourceList::operator=(const SourceList& other)`)? 
    - Se scrivi solo `this`, avresti un `SourceList*` (puntatore) → incompatibile con `SourceList&`.
    - Se invece scrivi `*this`, stai dereferenziando il puntatore:
        - `this` → `SourceList*`
    `   - *this` → `SourceList&` (alias all’oggetto stesso)

---
## Struttura 
elemento z -> puntatore a puntatore a lista contenente oggetti CellList

elemento y -> puntatore a lista contenente oggetti CellList

elemento x -> oggetto CellList

Matrice 2D
[[x,x],[x,x]]

Matrice 3D
[[[x,x],[x,x]],[[x,x],[x,x]]]

[
[[x,x],[x,x]], // Piano 1
[[x,x],[x,x]]  // Piano 2
]

[
[[x,x],[x,x]], // Primo elemento: Puntatore alla prima matrice
[[x,x],[x,x]]  // Secondo elemento: Puntatore alla seconda matrice
]

Primo elemento (Primo piano):
[
[x,x], // Puntatore alla prima riga (i.e puntatore alla prima lista di oggetti CellList) 
[x,x]  // Puntatore alla seconda riga (i.e puntatore alla seconda lista di oggetti CellList)
]

Puntatore alla prima riga:
[x,x] Riga composta da oggetti CellList
---
## delete[] in free_all_ (grid.cpp)
Esempio:
```cpp
delete[] cells[k][i];
```

In C++ esistono due versioni di delete:

- delete ptr; → si usa quando la memoria è stata allocata con new (singolo oggetto).
- delete[] ptr; → si usa quando la memoria è stata allocata con new[] (array di oggetti).

Se usi delete al posto di delete[], viene chiamato il distruttore solo del primo elemento dell’array, mentre gli altri elementi non vengono distrutti correttamente → comportamento indefinito.

## condizione ? valore_se_vero : valore_se_falso
Questa forma di condizione è presente in grid.cpp:

```cpp
sources = other.sources ? new SourceList(*other.sources) : nullptr;
```
- other.sources → è un puntatore a SourceList.

- La condizione other.sources ? ... : ... significa:
"Se other.sources non è nullptr allora fai ..., altrimenti fai ...".

- new SourceList(*other.sources) → crea un nuovo oggetto SourceList sullo heap, usando il costruttore di copia di SourceList.
In pratica fa una deep copy: duplica i contenuti della lista delle sorgenti dell’altro Grid.

- : nullptr → se invece other.sources era nullptr, allora anche sources diventa nullptr (quindi niente copia, non esiste lista sorgenti).

## Deep copy in binding.cpp
Come mai i costruttori di deep copy in binding.cpp non vengono costruiti come accade per gli altri metodi presenti (per esempio come venogono costruiti i metodi per la classe grid)?

1. Il costruttore di copia non è un metodo da esporre con .def
    - I normali metodi li esponi così: .def("step", &Grid::step), passando un member function pointer.
    - Il costruttore di copia invece è una special member function e non esiste come &Grid::qualcosa; per esporre un costruttore si usa .def(py::init<...>()), non .def("nome", ...).

2. Python usa __copy__/__deepcopy__, non il costruttore
    - In Python, copy.copy(obj) chiama obj.__copy__() e copy.deepcopy(obj, memo) chiama obj.__deepcopy__(memo).
    - Pybind11 non collega automaticamente il costruttore di copia C++ a questi special methods Python.
    - Per integrarti col protocollo Python, devi definire esplicitamente __copy__ e __deepcopy__ nel binding. Da qui le lambda
    
### Differenze tra copy, deepcopy e clone
1. copy.copy(obj) → __copy__ 
    - Livello Python: chiama obj.__copy__().
    - Nel binding: ritorna Grid(self).
    - Deve produrre una nuova istanza, ma può fare una copia “superficiale”: in Python, per oggetti mutabili complessi, questo significa copiare solo il contenitore e condividere riferimenti interni.
    - Nel tuo caso, dato che il costruttore di copia C++ fa già una deep copy dei buffer, copy.copy e deepcopy si comportano allo stesso modo (entrambe copiano a fondo la griglia).

2. copy.deepcopy(obj, memo) → __deepcopy__
    - Livello Python: chiama obj.__deepcopy__(memo).
    - memo è un dizionario usato da Python per gestire riferimenti ciclici o condivisi durante una copia profonda:
    - Se copi un grafo di oggetti con riferimenti incrociati, Python salva in memo gli oggetti già copiati per non duplicarli più volte e per evitare ricorsioni infinite.
    - Nel binding lo puoi ignorare se il tuo Grid è autosufficiente

3. clone() (metodo esplicito)
    - Non fa parte del protocollo Python: è solo una comodità che hai deciso di esporre.
    - Permette a un utente Python di scrivere:
        ```cpp
        g2 = g1.clone()
        ```
    senza importare copy.
    - Internamente fa lo stesso (Grid(self)), quindi nel tuo caso equivale a deepcopy, ma è più esplicito e leggibile per chi usa la libreria.

In sintesi: Dato che il costruttore di copia C++ è già profondo, tutte e tre le chiamate creano una copia indipendente identica. L’unica differenza funzionale è che deepcopy fornisce il memo per situazioni più complesse e fa parte del protocollo standard di Python per copie profonde, mentre clone è una scelta di design per chiarezza d’uso.

### Utilizzo
```cpp
import copy

# Crea una griglia di partenza
g1 = Grid(width=5, height=5)   # esempio: costruttore della griglia

# ---- 1) Shallow copy (copy.copy) ----
g2 = copy.copy(g1)             # Chiama __copy__ → Grid(self)

# ---- 2) Deep copy (copy.deepcopy) ----
g3 = copy.deepcopy(g1)         # Chiama __deepcopy__ → Grid(self), usa memo interno di Python

# ---- 3) Clone esplicito ----
g4 = g1.clone()                # Chiama il metodo clone definito nel binding

# Ora g2, g3 e g4 sono istanze indipendenti di Grid,
# ciascuna con il proprio contenuto copiato dal costruttore di copia C++.
```
