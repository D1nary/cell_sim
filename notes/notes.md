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
        - Compilazione del binding (`cpp_bridge/binding.cpp`): `make cell_sim_py`
        
    
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

4. Abbiamo un ulteriore metodo: Controller.set_grid(grid) → deep copy “in place” dentro ctrl.grid (non crea un nuovo oggetto Grid)

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
# Errors
## setter
Cercando di eseguire una deep copy di ctrl.grid:
```cpp
g2 = copy.deepcopy(ctrl.grid)
...
ctrl.grid = copy.deepcopy(g2)
```

```bash
Traceback (most recent call last):
  File "/home/ale/Documenti/prog/cell_sim/rein/control_test.py", line 104, in <module>
    ctrl.grid = copy.deepcopy(g2)
    ^^^^^^^^^
AttributeError: property of 'Controller' object has no setter
```
In pybind, Controller.grid era esposto come property read-only: def_property_readonly("grid", ...) che restituisce un riferimento alla Grid interna (return_value_policy::reference), senza setter.
Quando fai ctrl.grid = ..., Python tenta di assegnare alla property, ma non essendoci un setter pybind solleva: “property of 'Controller' object has no setter”.

Ho aggiunto un metodo Controller.set_grid(grid) che esegue una deep copy “in place” dentro la griglia posseduta dal Controller.

Perché “in place”? La Controller possiede una Grid*. Sostituire il puntatore (swap) sarebbe rischioso per l’ownership e la distruzione. Copiare i contenuti nell’istanza esistente evita leak/dangling.

## Funzione reset() rl_env.py
```cpp
        # Handle seeding for reproducibility
        if seed is not None:
            try:
                super().reset(seed=seed)
            except Exception:
                # Older Gym versions may not support super().reset(seed=...)
                pass
            try:
                # Seed the underlying C++ RNG as well (best-effort)
                cell_sim.seed(int(seed) & 0xFFFFFFFF)
            except Exception:
                pass
```

- Condizione seed: se seed non è None, si tenta di inizializzare i generatori casuali per garantire riproducibilità.
- super().reset(seed=seed): invoca il reset della classe base Gym passando il seed (supportato nelle versioni Gym più recenti) per sincronizzare lo stato casuale lato Python.
Compatibilità Gym: il try/except attorno a super().reset(...) evita errori con versioni più vecchie di Gym che non accettano il parametro seed; in tal caso si ignora l’errore.
- cell_sim.seed(int(seed) & 0xFFFFFFFF): setta anche il PRNG lato C++ (binding a std::srand). Il bitmask & 0xFFFFFFFF converte il seed in un intero non negativo a 32 bit, adatto all’API C/C++ e coerente tra piattaforme. In altre parole: sincronizza il generatore casuale lato C++ del simulatore, così Python e C++ usano lo stesso seed.
- Best-effort robusto: anche qui il try/except impedisce che un’assenza o errore del binding C++ interrompa il reset.
- Risultato: sia la parte Python sia quella C++ usano lo stesso seed, rendendo gli esperimenti riproducibili; se seed è None, non si modifica lo stato dei PRNG.

## hasattr
```cpp
if hasattr(self.ctrl, "clear_tempDataTab"):
    self.ctrl.clear_tempDataTab()
```

“hasattr(..., 'clear_tempDataTab')”: verifica a runtime se l’oggetto self.ctrl espone il metodo clear_tempDataTab. Serve per compatibilità: in build/versioni dove il metodo non esiste, si evita un AttributeError saltando la chiamata.

self.ctrl.clear_tempDataTab(): se presente, svuota il buffer temporaneo dei dati voxel accumulati (usato per salvare tabulati durante la simulazione). In reset() garantisce che i dati temporanei non “contaminino” il nuovo episodio.

Contesto: questi metodi vengono esposti nei binding C++ → Python del controller, vedi rein/cpp_bridge/binding.cpp.

## Scopo funzione close() rl_env.py

Scopo
- Liberare risorse esterne che il GC non rilascia subito (window, file, engines).
- Portare l’ambiente in stato “spento”; chiamate multiple devono essere sicure.

Cosa Pulire
- Rendering: chiudere finestre e contesti (pyglet/pygame/matplotlib).
- Registrazione: stop/flush di RecordVideo o writer di video/log.
- Simulatori: disconnettere physical engines (Mujoco/Bullet), rilasciare contesti GPU/GL.
- Processi/thread: fermare timer, fare join dei worker, terminare subprocessi.
- File/socket/tmp: chiudere file descriptor, socket, rimuovere cartelle/file temporanei.
- Binding nativi: rimuovere riferimenti a oggetti C/C++ perché girino i distruttori.

Linee Guida
- Idempotente: non deve fallire se chiamata più volte.
- Best‑effort: proteggere/ignorare eccezioni non critiche durante il cleanup.
- Propagare: chiamare super().close() perché wrapper/classi base puliscano.
- Effetti minimi: non modificare stato di apprendimento, non chiamare reset() implicitamente.
- Documentare: specificare se l’env è riutilizzabile dopo close() (spesso serve reset()).

Errori Comuni
- Dimenticare join di thread/subprocessi (processo che non termina).
- Perdere viewer o writer limitandosi ad azzerare riferimenti senza close().
- Alzare errori su chiamate ripetute, rompendo catene di wrapper.

Esempio
- Una buona close(): svuota buffer temporanei, chiude renderer/recorder, fa join dei worker, rimuove - riferimenti a oggetti nativi pesanti, imposta _closed = True, e chiama super().close().

## @dataclass

Esempio nel codice:
```cpp
@dataclass
class TrainConfig:
    # Reproducibility and bookkeeping
    seed: int = 42
    project_dir: Path = Path("results/rl")
    run_name: str = "debug"
    ...
```
@dataclass è un decoratore fornito dal modulo dataclasses (introdotto in Python 3.7) che semplifica la creazione di classi usate principalmente come contenitori di dati.

Quando applichi @dataclass a una classe:

- Genera automaticamente metodi speciali basati sui campi dichiarati, come:
    - __init__ → costruttore che accetta i campi come argomenti.
    - __repr__ → rappresentazione leggibile dell’oggetto, utile per il debug.
    - __eq__ → confronto di uguaglianza basato sui valori dei campi.
    - (Facoltativi) __lt__, __le__, __gt__, __ge__ se specifichi order=True.
- Mantiene il codice più conciso e leggibile, senza dover scrivere manualmente boilerplate (vedi dopo) come i costruttori.

Esempio
```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float

p1 = Point(3.0, 4.0)
p2 = Point(3.0, 4.0)

print(p1)        # ➡ Point(x=3.0, y=4.0)  (__repr__ automatico)
print(p1 == p2)  # ➡ True                 (__eq__ automatico)
```
Senza @dataclass, avresti dovuto definire manualmente __init__, __repr__, e __eq__.

## Boilerplate
In programmazione, boilerplate indica porzioni di codice ripetitivo e standard che devi scrivere quasi sempre allo stesso modo, ma che non contengono logica nuova o interessante.

Sono parti “meccaniche” del codice, spesso necessarie per motivi tecnici o di sintassi, ma che non aggiungono valore concettuale.

Esempio senza @dataclass (tanto boilerplate):
```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point(x={self.x}, y={self.y})"

    def __eq__(self, other):
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y
        return False
```
Con @dataclass (meno boilerplate):
```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
```
In una sola dichiarazione ottieni automaticamente costruttore, __repr__, __eq__ ecc., eliminando il codice standard.wait_values

## Pylance
Pylance è un estensione di Visual Studio Code sviluppata da Microsoft che fornisce un motore di analisi e completamento del codice per Python.

In pratica, è il “cervello” che rende l’editing Python in VS Code molto più veloce e intelligente.
Si basa su Pyright, un analizzatore statico per Python scritto in TypeScript, ed è ottimizzato per dare:
- Completamento automatico (IntelliSense) molto rapido e preciso.
- Type checking: controlla i tipi delle variabili, parametri e ritorni di funzioni per segnalare potenziali errori prima dell’esecuzione.
- Go to Definition, Rename Symbol, Find References: strumenti per navigare facilmente nel codice.
- Suggerimenti di import e correzioni rapide.
- Supporto a type hints (PEP 484, PEP 561, ecc.) → migliora la leggibilità e riduce bug.

## type hint
In una dataclass (o in generale nelle dichiarazioni di variabili e parametri in Python 3.6+), il simbolo : introduce un type hint (annotazione di tipo).

Esempio:
```python
seed: int = 42
```
- seed è il nome del campo.
- : int dice che ci si aspetta un valore di tipo intero (int).
- = 42 assegna il valore di default.

Le annotazioni di tipo servono a strumenti come Pylance, mypy, o IDE (VS Code, PyCharm) per:
- Controllare errori di tipo staticamente (senza eseguire il codice).
- Fornire autocompletamento e documentazione migliorata.
- Generare automaticamente metodi speciali (__init__, __repr__, ecc.) nella dataclass.

APPUNTI:
BASIC USAGE
env.reset() --> prima osservazione dell'ambiente
Possibile inizializzare l'ambinete con un seed particolare
timestep: applico l'azione all'ambinte e osservo (obrservaition)

## gym.make
Osservando gli esempi sulla pagina di gymnsasium si nota che gli ambienti built-in vengono creati con la funzione make(). Questo può essere fatto anche con ambienti "esterni" utlizzando un register:
```python
# Register the environment so we can create it with gym.make()
gym.register(
    id="gymnasium_env/GridWorld-v0",
    entry_point=GridWorldEnv,
    max_episode_steps=300,  # Prevent infinite episodes
)
```
Vantaggi
- Permette un’integrazione uniforme con gli strumenti Gym/Gymnasium (es. agenti, vector envs, registri personalizzati) che si aspettano l’API gym.make.
- Consente di parametrizzare l’ambiente passando gli argomenti direttamente a gym.make, utile se carichi configurazioni da file o CLI prima di creare l’ambiente.
- Facilita la creazione dinamica di ambienti per esperimenti, hyperparameter tuning o librerie esterne che conoscono solo l’ID registrato.
- Standardizza il ciclo gym.make → wrappers, rendendo il codice più leggibile per chi è abituato all’ecosistema Gym.

Svantaggi
- Richiede una fase di registrazione da mantenere allineata con il modulo reale (entry point, nome, parametri); eventuali refactor possono rompere l’ID registrato.
- Perde esplicità: con CellSimEnv(...) vedi subito classi e costruttore; con gym.make l’origine dell’ambiente è meno evidente.
- Il type checking/static analysis è più debole: gym.make ritorna un Env generico, mentre l’instanziazione diretta mantiene i tipi concreti.
- Se la registrazione avviene all’import, può introdurre effetti collaterali indesiderati (p.es. caricare cell_sim) in contesti dove non serve o in ambienti di test.

Dicendo che il type checking è più debole stiamo dicendo che mentre con Con CellSimEnv(...) il tipo concreto resta visibile al type checker: Pyright/mypy sanno che variabile è CellSimEnv, quindi possono verificare l’uso di attributi/metodi specifici come growth() o proprietà custom. Anche gli IDE offrono completamento contestuale accurato.

Quando diciamo che il type checking è “più debole”, intendiamo questo:

- Se usi CellSimEnv(...) direttamente, il tipo concreto rimane visibile al type checker (Pyright/mypy). Questo significa che lo strumento sa che la variabile è un CellSimEnv e può quindi verificare correttamente l’uso di metodi o attributi specifici, come growth() o proprietà personalizzate. Anche gli IDE, di conseguenza, forniscono un completamento automatico preciso e contestuale.

- Se invece usi gym.make(...), il valore restituito è tipizzato come gym.Env o gymnasium.Env, cioè solo come l’interfaccia base. Dal punto di vista statico diventa una variabile “generica”: il type checker non può più garantire la presenza di attributi aggiuntivi (come env.ctrl o env.total_dose), e quindi potrebbe segnalare errori o — se disattivi i warning — lasciar passare potenziali bug.

- Puoi recuperare il tipo corretto usando typing.cast(CellSimEnv, gym.make(...)), ma in questo caso stai facendo una promessa manuale: se per errore l’ID puntasse a un’altra classe, il cast maschererebbe il problema.

In sintesi: l’instanziazione diretta mantiene automaticamente le garanzie del type checker, mentre gym.make richiede cast espliciti o wrapper aggiuntivi per non perdere il supporto del controllo statico.

Di conseguenaza ho scelto di non utilizzare gym.make().

## Wrappers di Gymnasium
In Gymnasium (l’evoluzione di OpenAI Gym), i wrappers sono classi che “avvolgono” un ambiente per modificarne o arricchirne il comportamento senza dover toccare direttamente il codice dell’ambiente originale. Sono fondamentali per costruire pipeline di reinforcement learning flessibili e riutilizzabili.

A cosa servono nello specifico:
- Preprocessing delle osservazioni o delle azioni
    - Esempio: ridimensionare immagini, convertire a scala di grigi, normalizzare vettori d’ingresso.
    - Wrapper tipico: ObservationWrapper.
- Modifica dello spazio delle azioni o delle osservazioni
    - Esempio: discretizzare un’azione continua o limitare un range.
    - Wrapper tipico: ActionWrapper.
- Gestione delle ricompense
    - Esempio: trasformare le ricompense (clipping, normalizzazione, shaping).
    - Wrapper tipico: RewardWrapper.
- Aggiunta di funzionalità extra
    - Esempio: conteggio degli episodi, registrazione di video, monitoraggio delle metriche (RecordVideo, RecordEpisodeStatistics).
- Combinazione modulare di trasformazioni
    - Puoi concatenare più wrappers per applicare più trasformazioni in serie, mantenendo l’ambiente base intatto.
    
## Policy sequenziale e Policy ottimale
### Policy sequenziale
In reinforcement learning, sequenziale significa che l’agente non prende una sola decisione isolata, ma una serie di decisioni collegate nel tempo, dove ogni scelta influenza lo stato futuro dell’ambiente e quindi le decisioni successive.

Nel caso del paper PMC7922060:
- Ambiente: un modello cellulare che evolve nel tempo (cellule sane e tumorali cambiano dopo ogni dose).
- Azione: in ogni fraction (passo temporale) l’agente sceglie la dose di radiazione da somministrare.
- Transizione: la dose scelta modifica il numero di cellule tumorali e sane, cambiando lo stato dell’ambiente.
- Conseguenza: le decisioni prese oggi influenzano quante cellule saranno presenti nei passi futuri, quindi cambiano le opzioni disponibili in seguito.

Policy sequenziale: una strategia 𝜋(𝑠) che indica quale dose scegliere ad ogni stato futuro, non solo la prima volta. L’agente impara a pianificare lungo più frazioni per massimizzare il reward cumulativo (uccidere tumori minimizzando il danno alle cellule sane lungo tutto il trattamento).

📌 Esempio intuitivo:
Se l’agente usa una dose altissima subito, uccide molte cellule tumorali ma danneggia molto le sane, riducendo la “salute” dell’ambiente e potenzialmente compromettendo i trattamenti futuri. Una policy sequenziale gli insegna a bilanciare le dosi frazionate per un vantaggio maggiore alla fine dell’intero trattamento.

### Policy ottimale nel caso dell'articolo
Nel contesto della simulazione descritta nell’articolo (PMC7922060), la policy ottimale rappresenta:

📋 Una strategia di trattamento completa: una mappa che, dato lo stato corrente della simulazione (es. quantità di cellule tumorali e sane, tempo trascorso, dosi già somministrate), indica quale dose di radiazione scegliere a quel passo.

🧭 Il “piano” che massimizza il reward cumulativo: cioè la sequenza di decisioni che, nell’intero corso del trattamento, uccide il maggior numero possibile di cellule tumorali minimizzando il danno alle cellule sane.

⏳ Una funzione a lungo termine: non guarda solo alla prossima frazione, ma pianifica l’effetto futuro delle scelte presenti — ad esempio, può decidere di somministrare una dose più bassa oggi per preservare cellule sane e ottenere un risultato migliore nei passi successivi.

🧠 La conoscenza appresa dall’agente RL: dopo il training, la policy ottimale è il “comportamento” dell’agente: basta fornirle lo stato corrente della simulazione per ottenere la dose consigliata, senza dover ripetere l’addestramento.

In pratica, la policy ottimale è il protocollo di radioterapia appreso automaticamente dall’agente, che specifica come frazionare le dosi nel tempo per ottenere il miglior compromesso tra efficacia contro il tumore e sicurezza per i tessuti sani.

## CUDA
CUDA (Compute Unified Device Architecture) è una piattaforma di calcolo parallelo e un'API creata da NVIDIA.
Serve a sfruttare la GPU (scheda grafica) non solo per la grafica, ma anche per eseguire calcoli generali ad alte prestazioni, come quelli usati nel machine learning, nell’elaborazione di immagini o nella simulazione scientifica.

Come funziona
- Le GPU sono composte da migliaia di core che possono eseguire tante operazioni in parallelo.
- Con CUDA, puoi scrivere codice (in C, C++, Python tramite librerie come PyTorch o TensorFlow) che sposta parte del lavoro dalla CPU alla GPU.
- PyTorch, ad esempio, usa CUDA per accelerare il training delle reti neurali.

## Installazione Pytorch
Installazione di PyTorch il quale gira sia su CPU che (quando presente) su GPU. L’installazione “GPU-enabled” funziona comunque su CPU: se non trova una GPU compatibile userà automaticamente la CPU.

```bash
pip install --upgrade pip
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

## train.py
### parse_args()
parse_args() serve a leggere e interpretare gli argomenti passati da linea di comando quando esegui lo script train.py. In pratica ti permette di configurare l’allenamento senza modificare direttamente il codice.

- Creazione di un parser
    ```python
    parser = argparse.ArgumentParser(description="Train a DQN agent for CellSimEnv")
    ```
    Questo oggetto raccoglierà tutti gli argomenti che lo script accetta.
- Definisce gli argomenti (ognuno con nome, tipo, default e help). Ad esempio: 
    - --episodes: numero di episodi di training (default 500).
    - --max-steps: massimo numero di step per episodio (default 1000).
- Restituisce i valori con `return parser.parse_args()`. Questi valori vengono messi dentro un oggetto Namespace, accessibile come args.qualcosa. Un singolo elemento di Namespace, è una coppia chiave-valore dove la chiave è il nome dell'argomento mentre il valore è quello inserito da teminale o, se non passato, di default

Da terminale si può quindi eseguire, per esepio:
```bash
python train.py --episodes 1000 --device auto --lr 0.0005
```
### resolve_device()
Questa funzione traduce la stringa passata con --device (che viene da parse_args()) in un oggetto torch.device di PyTorch, scegliendo in maniera intelligente se usare CPU o GPU (CUDA).

1. Caso auto
    - Se scrivi `--device auto`, la funzione controlla se CUDA è disponibile (torch.cuda.is_available()):
        - Se sì → ritorna torch.device("cuda").
        - Se no → ritorna torch.device("cpu").

2. Caso cuda
    - Se scrivi `--device cuda`, la funzione controlla comunque che CUDA sia disponibile:
        - Se sì → ritorna torch.device("cuda").
        - Se no → ricade alla CPU.
3. Tutti gli altri casi (cpu o flag non validi)
        - Ritorna sempre torch.device("cpu").
        
### build_discrete_actions()
Per come sono state definite in CellSimEnv, le possibile azioni appartengono ad un range continuo. Per esempio, la dose potrebbe essere 1.37, 1.85, 0.05, ecc. Il problema è che l’algoritmo DQN funziona solo con azioni discrete, non continue. Quindi build_discrete_actions() trasforma lo spazio continuo in un insieme finito (una griglia). 

Tramite la funzione linspace si divide dose e numero di ore in un numero bins di intervalli discreti. 
```python
dose_values = np.linspace(low_dose, high_dose, num=dose_bins)
```
### linear_epsilon()
Serve a calcolare il valore di ε (epsilon) nell’ε-greedy policy.
- In un DQN, ε rappresenta la probabilità di scegliere un’azione casuale invece di quella con Q-valore massimo.
- All’inizio del training vogliamo molta esplorazione (ε alto, tipicamente 1.0).
- Col passare degli step, vogliamo diminuire ε verso un valore minimo (es. 0.05), per fare più sfruttamento della policy appresa.

linear_epsilon() implementa questa decrescita lineare di ε.

1. Se decay_steps <= 0 → ritorna subito end (niente annealing, ε fisso).
2. Calcola la frazione di progresso:
    ```python
    fraction = min(1.0, step / float(decay_steps))
    ```
    - 0.0 all’inizio (step=0)
    - cresce fino a 1.0 dopo decay_steps passi.
3. Interpola linearmente:
    ```python
    return start + fraction * (end - start)
    ```
    - start rappresenta il valore iniziale di ε (epsilon), cioè la probabilità di esplorazione all’inizio del training.
    - Se fraction=0 → ε = start
    - Se fraction=1 → ε = end
    - Valori intermedi → interpolazione lineare.
    
### main()
- Come mai viene usato `state_dim = int(np.prod(env.observation_space.shape))`?
self.observation_space è definito con
```python
self.observation_space = spaces.Box(
    low=0.0,
    high=np.inf,
    shape=(2,),
    dtype=np.float32,
)
```

quindi è un oggetto box "contenente" un array di dimensione 2". L'attributo `env.observation_space.shape` restituisce una tupla (2,) cioè la dimensione dell'array di box. Per ottenere solo il numero che rappresenta la dimensione è necessario fare il prodotto dei valori allinterno della tupla ottenedo quindi solo 2

- update()
    - update() = 1 passo di ottimizzazione DQN:
    - Campiona un batch dal replay buffer.
    - Calcola Q(s,a) corrente.
    - Costruisce il target con Double DQN.
    - Calcola la loss (Huber).
    - Aggiorna la policy net.
    - Sincronizza la target net periodicamente.

VEDI SEZIONE agent.py

## agent.py

### eval target network
```python
self.target_net.eval()
```
In PyTorch, una rete neurale (nn.Module) può trovarsi in due modalità principali:
1. Training mode (model.train()):
    - Alcuni layer si comportano in modo stocastico o dipendente dal batch.
    - Esempi:
        - Dropout → spegne casualmente neuroni a ogni forward per regolarizzare.
        - BatchNorm → normalizza gli output usando le statistiche del batch corrente.
2. Evaluation mode (model.eval()):
    - Questi comportamenti vengono disattivati o resi deterministici:
        - Dropout → non spegne più neuroni.
        - BatchNorm → usa le statistiche fissate in training, non quelle del batch.
    - In questo modo, l’output della rete diventa stabile e ripetibile.
    
Nel caso della target network:
La target network non si allena mai direttamente: serve solo a calcolare i target Q-values nella formula di aggiornamento. Quindi vogliamo che il suo comportamento sia deterministico e costante, indipendentemente dal batch o da effetti casuali. Per questo viene messa in eval(): garantisce che la rete venga usata solo per inferenza, senza dropout o altre variazioni.

### In select_action()
- `state_tensor = torch.as_tensor(state, dtype=torch.float32, device=self.device).unsqueeze(0)`
Il ReplayBuffer è una memoria che conserva le transizioni che l’agente vive:
$$ (s_t, a_t, r_t, s_{t+1}, \text{done}) $$
Ogni volta che l’agente fa uno step nell’ambiente (env.step()), aggiunge una transizione al buffer:

```python
self.replay_buffer.add(state, action_index, reward, next_state, done)
```

Quindi il buffer diventa una "banca dati" di esperienze passate.
Quando facciamo l’update della rete Q, non usiamo solo l’ultima transizione (come in Q-learning tabellare), ma estraiamo un mini-batch di esperienze a caso dal replay buffer:
```python
batch = self.replay_buffer.sample(self.config.batch_size, self.device)
states, actions, rewards, next_states, dones = batch
```

Esempio se batch_size = 64:
- states.shape = torch.Size([64, 2]) → 64 stati, ciascuno con 2 feature (healthy, cancer).
- actions.shape = torch.Size([64]) → 64 indici azione.
- rewards.shape = torch.Size([64]) → 64 reward scalari.
- ecc.

**Perché serve il batch?**
Addestrare la rete con più esempi contemporaneamente è molto più stabile ed efficiente (grazie alla media dei gradienti).
Il batch rompe la correlazione temporale tra stati consecutivi → se usassi solo l’ultima transizione, rischieresti di imparare solo pattern molto dipendenti dall’ordine degli stati.

La dimensione di input per le reti in PyTorch segue sempre la convenzione:
```python
[batch_size, feature_dim]
```

Nel caso del codice, lo stato osservato è un singolo array, es.:

DA FINIRE

### Update

```python
loss = agent.update() 
```
L’ordine delle azioni che portano ad update è (in main di train.py):
- Azione scelta con select_action.
- Ambiente aggiornato con env.step.
- Transizione salvata nel replay buffer (agent.store_transition).
- Aggiornamento della rete (agent.update()).

L'estrazione avviene nel seguente modo:
- Esperienze salvate in ReplayBuffer.add(...) ogni volta che fai env.step().
- Batch estratto in DQNAgent.update() tramite ReplayBuffer.sample(...).
- Questo batch viene poi passato attraverso la rete per calcolare i Q-values e aggiornare i pesi.

update() esegue i seguenti compiti
1. Check sul buffer: 
controlla il numero minimo di transizioni che servono nel replay buffer prima di iniziare il training con la funzione can_update():

```python
def can_update(self) -> bool:
    """Return True when the buffer has enough samples for training."""
    needed = max(self.config.min_buffer_size, self.config.batch_size)
    return len(self.replay_buffer) >= needed
```
Restituisce True se il buffer contiene almeno needed transizioni, False altrimenti.

2. Estrazione batch
Incrementa il contatore interno _step_counter (serve per sapere quando aggiornare la target network).
Campiona un mini-batch dal replay buffer (sample). Ottenendo i tensori:
- states: [batch_size, state_dim]
- actions: [batch_size]
- rewards: [batch_size]
- next_states: [batch_size, state_dim]
- dones: [batch_size]

```python
    self._step_counter += 1
    batch = self.replay_buffer.sample(self.config.batch_size, self.device)
    states, actions, rewards, next_states, dones = batch
```

3. Calcolo dei Q-values della policy net per tutti gli stati del batch

```python
    current_q = self.policy_net(states).gather(1, actions.unsqueeze(1)).squeeze(1)
```
In particolare:
- states ha shape `[batch_size, state_dim]` quindi, per esempio, batch_size=64 e state_dim=2: `q_values.shape = [64, 2]`. states viene preso dal batch estratto dal replay buffer.
- actions: vine estratto dal batch e quindi dal replay buffer. È un tensore di dimensione batch_size. Contiene l'indice dell'azione (dopo che le azioni sono state discretizzate in indici)

Esempio: se batch_size = 4
```python
actions = tensor([0, 5, 2, 1])  # torch.Size([4])
```
- actions.unsqueeze(1) 
Aggiunge una nuova dimensione in posizione 1. Serve perchè torch.gather(input, dim=1, index) si aspetta che index abbia lo stesso numero di righe del batch e una colonna per ciascun indice da estrarre.

Quindi se q_values.shape = [batch_size, num_actions], allora actions.unsqueeze(1).shape = [batch_size, 1] è compatibile.

- .gather(1, actions.unsqueeze(1))

torch.gather(input, dim, index) prende valori da input lungo dim, usando index cioè:
- input = q_values ([64, 2])
- dim = 1 (asse delle azioni)
- index = actions.unsqueeze(1) ([64, 1])

Si ottiene una cosa del genere:
```pytohn
q_values =
[[1.0, 2.0, 3.0, 4.0],
 [0.5, 1.5, 2.5, 3.5],
 [9.0, 8.0, 7.0, 6.0]]

actions = [2, 0, 3]   # scelto azione 2, 0, 3

q_values.gather(1, actions.unsqueeze(1)) =
[[3.0],
 [0.5],
 [6.0]]
```
- .squeeze(1)
    - Rimuove la dimensione “inutile” da [64, 1] → [64].
    - Quindi current_q ha shape [batch_size]: un Q-value per ogni transizione del batch.
    
- ESEMPIO COMPLETO
Consideriamo:
- dose_bins = 3 → dose ∈ [0.0, 1.0, 2.0]
- wait_bins = 2 → ore di attesa ∈ [0.0, 24.0]

Quindi le azioni discrete possibili (self.actions) saranno:
```python
0 → [0.0,  0.0]
1 → [0.0, 24.0]
2 → [1.0,  0.0]
3 → [1.0, 24.0]
4 → [2.0,  0.0]
5 → [2.0, 24.0]
```
Abbiamo il seguente esempio di utilizzo di `current_q = self.policy_net(states).gather(1, actions.unsqueeze(1)).squeeze(1)`

```python
import torch

# 🔹 Batch di stati (cellule_sane, cellule_cancerose)
states = torch.tensor([
    [9500, 500],   # stato 1
    [9000, 1000],  # stato 2
    [9800, 200],   # stato 3
    [8700, 1300]   # stato 4
], dtype=torch.float32)
print("states.shape:", states.shape)  # torch.Size([4, 2])

# 🔹 Supponiamo che la policy_net restituisca Q-values per 6 azioni discrete:
#   0 → [0.0,  0.0]
#   1 → [0.0, 24.0]
#   2 → [1.0,  0.0]
#   3 → [1.0, 24.0]
#   4 → [2.0,  0.0]
#   5 → [2.0, 24.0]
q_values = torch.tensor([
    [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],   # stato 1
    [6.0, 5.0, 4.0, 3.0, 2.0, 1.0],   # stato 2
    [0.5, 1.5, 2.5, 3.5, 4.5, 5.5],   # stato 3
    [9.0, 8.0, 7.0, 6.0, 5.0, 4.0]    # stato 4
])
print("q_values.shape:", q_values.shape)  # torch.Size([4, 6])

# 🔹 Indici delle azioni realmente eseguite (nel batch)
actions = torch.tensor([4, 1, 5, 0])   # es: dose/tempo scelti
print("actions.shape:", actions.shape)  # torch.Size([4])

# 🔹 Aggiungiamo la seconda dimensione (necessaria per gather)
actions_unsq = actions.unsqueeze(1)
print("actions_unsq.shape:", actions_unsq.shape)
print(actions_unsq)
# tensor([[4],
#         [1],
#         [5],
#         [0]])

# 🔹 Estraiamo i Q-values delle azioni scelte
chosen_q = q_values.gather(1, actions_unsq)
print("chosen_q.shape:", chosen_q.shape)
print(chosen_q)
# tensor([[5.0],   # stato 1 → azione 4 = [2.0, 0.0]
#         [5.0],   # stato 2 → azione 1 = [0.0, 24.0]
#         [5.5],   # stato 3 → azione 5 = [2.0, 24.0]
#         [9.0]])  # stato 4 → azione 0 = [0.0, 0.0]

# 🔹 Togliamo la dimensione extra
current_q = chosen_q.squeeze(1)
print("current_q.shape:", current_q.shape)
print(current_q)
# tensor([5.0, 5.0, 5.5, 9.0])
```

NOTA: COME MAI q_values HA 6 COLONNE?
Nell'ambiente un’azione reale è un vettore di due numeri:
```bash
[dose, num_ore]
```
Ma per usare un DQN (che lavora su spazi di azione discreti), il continuo `[dose, num_ore]` viene discretizzato in un insieme finito di possibili azioni.

La funzione build_discrete_actions() in train.py costruisce una lista di azioni possibili:
- dose_bins = 3 → valori dose = [0.0, 1.0, 2.0]
- wait_bins = 2 → valori ore = [0.0, 24.0]
allora le azioni discrete diventano tutte le combinazioni:

```python
[0.0, 0.0], [0.0, 24.0],
[1.0, 0.0], [1.0, 24.0],
[2.0, 0.0], [2.0, 24.0]
```
Totale = 3 × 2 = 6 azioni discrete. 

Cosa rappresentano le colonne di q_values?

La rete policy_net produce un valore Q per ciascuna azione discreta.
Quindi: n° colonne = n° azioni discrete Ogni colonna corrisponde ad una combinazione [dose, num_ore].
Esempio:
- Se hai 6 azioni discrete, q_values avrà shape [batch_size, 6].
- Se hai 3 azioni discrete, q_values avrà shape [batch_size, 3].

Considerando che i bin dell'esempio precedente sono 
```python
q_values =
[[1.0, 2.0, 3.0, 4.0],
 [0.5, 1.5, 2.5, 3.5],
 [9.0, 8.0, 7.0, 6.0]]
```
dell'esempio precedente, il numero di righe rappresenta ciascuno stato mentre ogni valore q in ciascuna riga rappresenta il valore q della possibile azione (6 colonne poichè abbiamo 6 possibili azioni).

4. Target Q (Double DQN)
```python
    with torch.no_grad():
        next_actions = torch.argmax(self.policy_net(next_states), dim=1, keepdim=True)
        next_q = self.target_net(next_states).gather(1, next_actions).squeeze(1)
        targets = rewards + (1.0 - dones) * self.config.gamma * next_q
```
- Usa la policy net per scegliere l’azione migliore (argmax) nei next_states.
- Usa la target net per valutare il valore Q di quell’azione.
- Costruisce i target secondo la formula di Bellman

5. Ottimizzazione
```python
    loss = F.smooth_l1_loss(current_q, targets)
    self.optimizer.zero_grad()
    loss.backward()
    if self.config.gradient_clip is not None:
        torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), self.config.gradient_clip)
    self.optimizer.step()
```
- Calcola la perdita Huber loss (smooth_l1_loss) tra current_q e targets
- Azzera i gradienti poichè PyTorch, di default, accumula i gradienti a ogni backward(), quindi vanno resettati prima di calcolare quelli nuovi. (self.optimizer.zero_grad())
- Backpropagation: calcola i gradienti e aggiorna i pesi della policy net (loss.backward()). 
- Opzionalmente fa clipping dei gradienti per stabilizzare l’allenamento.
- Aggiorno i pesi della rete (self.optimizer.step())

Cosa si intende per clipping?
- Durante il training di una rete neurale, i gradienti calcolati con backpropagation possono diventare molto grandi (problema del exploding gradients).
- Se i gradienti sono enormi → i pesi vengono aggiornati con passi troppo grandi → l’allenamento diventa instabile o diverge.
- Clipping vuol dire limitare la grandezza dei gradienti prima dell’aggiornamento dei pesi.

Esistono diverse tipologie di clipping tra cui Norm clipping (quello utilizzato) e Value clipping

6. Aggiornamento della target network

```python
    if self._step_counter % self.config.target_update_interval == 0:
        self.sync_target_network()
```
- Ogni target_update_interval passi, copia i pesi della policy net nella target net (soft reset).
- Questo stabilizza l’apprendimento, perché la target rimane fissa per un po’ di passi.

7. Ritorno
```python
    return float(loss.item())
```
Ritorna la perdita numerica come float cioè il numero che misura quanto i valori previsti dalla rete si discostano dai valori target.

### save()
La funzione salva su file dati relativi alla rete. In particolare:
- "policy_state_dict" → i parametri (pesi e bias) della policy network (self.policy_net.state_dict()).
- "target_state_dict" → i parametri della target network.
- "config" → la configurazione dell’agente (DQNConfig) che contiene iperparametri (learning rate, gamma, batch size, ecc.).
- "actions" → la lista di azioni discrete (self.actions) usata per mappare gli indici alle azioni reali [dose, wait].

### load()
1. Caricamento del file
```python
checkpoint = torch.load(path, map_location=self.device)
```
- Legge il file salvato con save().
- map_location=self.device assicura che i tensori vengano caricati sul device corretto (CPU o GPU).

2. Ripristino pesi delle reti
```python
self.policy_net.load_state_dict(checkpoint["policy_state_dict"])
self.target_net.load_state_dict(checkpoint["target_state_dict"])
```
- Carica i parametri (pesi e bias) sia della policy net che della target net.
- Così il modello riprende esattamente da dove era stato salvato.

3. Ripristino delle azioni
```python
self.actions = [np.asarray(a, dtype=np.float32) for a in checkpoint.get("actions", self.actions)]
```
- Se nel file c’è la lista delle azioni (actions), viene ricaricata.
- Se non c’è (vecchio checkpoint), mantiene self.actions attuale.

4. Ripristino configurazione
```python
self.config = checkpoint.get("config", self.config)
```
- Se il file contiene la configurazione (DQNConfig), la carica.
- Se no, mantiene quella esistente.

## model.py
Il file definisce la rete neurale usata dall’agente DQN.

### init()
1. Dichiarazione
```python
def __init__(
    self,
    input_dim: int,
    output_dim: int,
    hidden_sizes: Iterable[int] = (128, 128),
) -> None:
    super().__init__()
```
- input_dim = dimensione dello stato (es. 2: healthy_cells, cancer_cells).
- output_dim = numero di azioni discrete (len(self.actions) nell’agente).
- hidden_sizes = dimensioni dei layer nascosti, default (128,128).
- super().__init__() → inizializza la parte base di nn.Module.

COSA SI INTENDE PER DIMENSIONE DEI LAYER NASCOSTI?
In una rete neurale feed-forward (come la tua QNetwork), distinguiamo in generale tre tipi di layer:
- Input layer — riceve lo stato in ingresso (nel tuo caso dimensione = numero di feature ad dello, stato es. 2).
- Hidden layers (layer nascosti) — situati tra input e output, servono a trasformare l’informazione.
- Output layer — produce il risultato finale (nel tuo caso Q-values per ciascuna azione).

La dimensione di un hidden layer (o “numero di unità / neuroni nel layer nascosto”) è il numero di neuroni / unità presenti in quel layer.

Se un layer nascosto ha dimensione 128, significa che quel layer riceve un input (da precedente layer) e produce un output che è un vettore di 128 valori (uno per ogni neurone del layer).

In termini più tecnici: il layer è una trasformazione lineare da uno spazio dimensione $d_{in}$ a uno spazio dimensione d_{hidden}, seguita da un’attivazione non lineare.

Se hai più hidden layers, ciascuno ha la sua dimensione. Ad esempio, hidden_sizes = (128, 128) significa che hai due hidden layers, ciascuno con 128 neuroni (o unità).

2. Costruzione della QNetwork
```python
layers: list[nn.Module] = []
last_dim = input_dim
for size in hidden_sizes:
    layers.append(nn.Linear(last_dim, int(size)))
    layers.append(nn.ReLU())
    last_dim = int(size)
layers.append(nn.Linear(last_dim, output_dim))
self.net = nn.Sequential(*layers)
```

    - Lista dei layer
    ```pytohn
    layers: list[nn.Module] = []
    ```
    Crea una lista vuota di moduli PyTorch (nn.Module). In questa lista verranno aggiunti i layer della rete (densi e attivazioni).

    - Inizio dal dimensionamento input
    ```python
    last_dim = input_dim
    ```
    last_dim tiene traccia della dimensione di uscita del layer precedente (serve per collegare correttamente i layer lineari). All’inizio, è uguale all’input (dimensione dello stato, es. 2 → [healthy, cancer]).
    - Ciclo sui layer nascosti
    ```python
    for size in hidden_sizes:
        layers.append(nn.Linear(last_dim, int(size)))
        layers.append(nn.ReLU())
        last_dim = int(size)
    ```
    Per ogni layer nascosto creo, con nn.Linear(last_dim, int(size)), un layer che trasforma un input di last_dim (per esempio 2 feature al primo ciclo) features in int(size) neuroni. Definiamo l'attivazione non lineare ReLu per i neuroni e aggiorniamo last_dim
    - Layer di output
    ```python
    layers.append(nn.Linear(last_dim, output_dim))
    ```
    Aggiungiamo il layer di output. In questo caso trasforma un input di last_dim features (numero di features dell'ultimo layer nascosto) in un numero di output_dim neuroni corrispondenti al numero di azioni discrete ovvero al numero Q-values vogliamo ottenere

### _init_weights()
_init_weights serve a inizializzare i pesi dei layer lineari (nn.Linear) in un modo controllato, invece di lasciare la scelta al default di PyTorch.

Un’inizializzazione corretta evita:
- Gradiente che esplode → valori enormi nei pesi.
- Gradiente che scompare → valori che si avvicinano a zero e bloccano l’apprendimento.

```python
def _init_weights(self) -> None:
    """Apply Xavier initialization to the linear layers."""
    for module in self.modules():
        if isinstance(module, nn.Linear):
            nn.init.xavier_uniform_(module.weight)
            nn.init.zeros_(module.bias)
```

- self.modules()
il metodo .modules() restituisce un iteratore su tutti i sotto-moduli che compongono la tua rete, inclusi:
    - i layer lineari (nn.Linear)
    - le funzioni di attivazione (nn.ReLU, nn.Sigmoid, ecc.)
    - eventuali blocchi sequenziali (nn.Sequential)
    - altri moduli annidati
- if isinstance(module, nn.Linear):
    - Controlla se il modulo è un layer lineare (nn.Linear).
    - Vogliamo inizializzare solo i layer con pesi e bias, non le attivazioni (ReLU).
- nn.init.xavier_uniform_(module.weight)
Applica Xavier uniform initialization (anche chiamata Glorot uniform). Distribuisce i pesi con valori random in un intervallo calcolato in base alla dimensione del layer. In DQN e reti con ReLU, Xavier (uniforme o normale) è una buona scelta perché:
    - Mantiene i valori dei neuroni bilanciati in media.
    - Riduce il rischio di gradienti instabili.
- nn.init.zeros_(module.bias)
    - Inizializza tutti i bias a 0.
    - I bias non hanno lo stesso problema dei pesi (non amplificano la varianza), quindi zero è una scelta comune e sicura.
    
## replay_buffer.py
### init()
```python
class ReplayBuffer:
    """Fixed-size buffer that stores transitions for off-policy learning."""

    def __init__(self, capacity: int) -> None:
        self.capacity = int(capacity)
        self._buffer: Deque[Transition] = deque(maxlen=self.capacity)
```
1. Parametro capacity
È la dimensione massima del buffer, cioè quante transizioni ((state, action, reward, next_state, done)) può contenere al massimo.

2. self._buffer: Deque[Transition] = deque(maxlen=self.capacity)

    - _buffer è una deque (double-ended queue) della libreria standard Python.
    - maxlen=self.capacity → significa che la deque mantiene al massimo capacity elementi.
    - Quando aggiungi un nuovo elemento oltre la capacità, il più vecchio viene automaticamente rimosso.
    - Tipo degli elementi: Transition (una dataclass che contiene state, action, reward, next_state, done). La classe transition è stata definita nel codice
    
### add()
Append new Transition to the buffer. 
### sample()
- Costruzione di states:
```python
states = torch.as_tensor(np.stack([t.state for t in batch], axis=0), device=device)
```
    - t.state for t in batch: estrae l'attributo state dall'oggetto Transition per ogni elemento del batch
    - np.stack prende la lista di array e li unisce lungo un nuovo asse
    - torch.as_tensor(..., device=device): Converte la matrice NumPy in un tensore PyTorch. Viene copiato sul device corretto (cpu o cuda). Non specifica dtype → quindi eredita da NumPy (float32, perché gli stati vengono salvati così in add()).

- Costruzione di actions, reward e next_state, dones: Avviene come per states

## pycache
Le cartelle __pycache__ sono la cache di Python per i moduli compilati in bytecode. Ogni volta che importi o esegui un file .py, Python lo compila in bytecode ottimizzato (corrispondente alla versione del tuo interprete) e lo scrive in __pycache__, in modo che le importazioni successive vengano caricate più velocemente, senza bisogno di rianalizzare/compilare il codice sorgente ogni volta. Sono interamente generate automaticamente; puoi eliminarle in sicurezza e Python le rigenererà su richiesta.

Python crea una cartella __pycache__ in ogni directory dove importa o compila moduli. Anche strumenti come python3 -m compileall rein generano bytecode per tutti i file e li salvano accanto ai sorgenti. Dal momento che il progetto è stato suddiviso in più sottopacchetti (rein/agent, rein/env, rein/tests, …) e abbiamo eseguito la compilazione di prova, ogni cartella ha ricevuto il proprio __pycache__. Sono file temporanei: puoi ignorarli o cancellarli (Python li rigenera alla successiva esecuzione).

## Esecuzione file
In genere, cos'è più comune fare:
Lanciare i programmi dalla root o direttamente dalla directory del file?

Di solito conviene restare nella root del progetto e lanciare lì i tuoi script (spesso via python -m package.module). Così il package layout e gli import funzionano sempre, la documentazione/istruzioni risultano più coerenti e non devi ricordarti percorsi relativi diversi. Capita di eseguire un file direttamente dalla sua directory, ma è meno portabile e può rompere gli import quando ci sono riferimenti al package principale.

## Errori
### Errore Pylance
Nella seguente riga di codice python, Pylance segna l'errore: No overloads for "prod" match the provided arguments 
```python
state_dim = int(np.prod(env.observation_space.shape))
```
L'avviso vuol dire che non riesce a capire che env.observation_space.shape è una sequenza di interi compatibile con np.prod.

In pratica:
- A runtime il codice funziona perfettamente.
- Pylance, però, non trova un overload tipizzato di np.prod che accetti il tipo che pensa abbia env.observation_space.shape.

Soluzioni:
- Ignorare l’avviso: il codice è corretto e gira.
- Aiutare Pylance con un hint di tipo:
    ```python
    import numpy as np
    from typing import Tuple

    shape: Tuple[int, ...] = env.observation_space.shape
    state_dim = int(np.prod(shape))
    ```
- Aggiungere un commento per ignorare il check:
    ```python
    state_dim = int(np.prod(env.observation_space.shape))  # type: ignore
    ```
###  No module named 'cell_sim'
Lanciando python -m rein.tests.control_test dalla root ottengo:
`ModuleNotFoundError: No module named 'cell_sim'`

L’errore nasce da rein/tests/control_test.py:7, che fa import cell_sim, mentre il modulo compilato vive in rein/cell_sim.cpython-312-…so (siccome è l’estensione Python compilata (binding C/C++) del progetto), quindi non è risolvibile come top-level package se avvii lo script dal progetto.

È stato aggiunto uno stub per l’estensione nativa, così che PyLance possa riconoscere correttamente le esportazioni.
Il file di riferimento è rein/cell_sim.pyi:1, dove sono dichiarate le firme di Grid, Controller e seed, corrispondenti ai binding definiti con pybind11.
Con questo stub in posizione, l’import from rein import cell_sim viene risolto senza problemi: PyLance infatti può leggere le definizioni del modulo senza dover ispezionare direttamente il file .so compilato.

## seed
Ecco tutti i punti del tuo codice in cui il seed viene usato (o passato) e cosa fa in ognuno:

1. Argomento CLI --seed (training)
    - Definito tra gli argomenti di train.py, così puoi impostarlo da riga di comando. 

2. Inizializzazione dei generatori random (training)
    - Funzione seed_everything(seed) in train.py: inizializza Python random, NumPy, PyTorch e (se presente) CUDA per rendere la run deterministica. Chiamata all’inizio di main().
3. Seeding per-episodio dell’ambiente (training loop)
    - Ad ogni episodio: state, _ = env.reset(seed=args.seed + episode). In questo modo ogni episodio ha un seed diverso ma riproducibile dato lo stesso --seed. 
train
4. Gestione del seed dentro l’ambiente (rl_env.py)
    - CellSimEnv.reset(..., seed=...):
        - prova a chiamare super().reset(seed=seed) per allinearsi all’API Gym/Gymnasium (se supportato);
        - chiama cell_sim.seed(int(seed) & 0xFFFFFFFF) per inizializzare anche l’RNG C++ del simulatore via binding.
5. Binding C++: funzione cell_sim.seed
    - In binding.cpp è esposta la funzione seed verso Python; internamente fa std::srand(s) per il RNG C++ (usata dal punto 4).

### super().reset(seed=seed)
Nel tuo CellSimEnv.reset(...) chiami il reset della classe base Gym/Gymnasium:
- Inizializza l’RNG dell’ambiente (self.np_random)
Gymnasium, quando passi seed=..., crea un generatore NumPy dedicato all’ambiente (tipicamente un np.random.Generator con PCG64). Questo finisce in self.np_random e viene usato dall’ecosistema Gym per tutto ciò che è “random” lato env.

- (Spesso) re-seeda gli spazi (action_space, observation_space)
Nelle versioni moderne di Gymnasium, gli spaces hanno un proprio RNG. Passare seed a reset porta a riallineare anche gli RNG degli spazi, così action_space.sample() diventa riproducibile rispetto al seed.
(Nelle versioni più vecchie di gym questo comportamento era meno uniforme: da qui il tuo try/except.)

- Stabilisce lo standard Gym per la riproducibilità
Molti wrapper/algoritmi (vectorized envs, monitor, ecc.) si aspettano che il seeding avvenga proprio così: tramite env.reset(seed=...). Chiamare super().reset(...) ti rende compatibile con quell’aspettativa.

Nota: Il super().reset(seed=seed) non crea l’osservazione iniziale — quello lo fai tu nella tua reset. La chiamata serve (principalmente) a gestire il seeding in modo “canonico”.

### cell_sim.seed(int(seed) & 0xFFFFFFFF)

- Imposta il RNG “globale” del C/C++
Nel binding è definita una funzione seed(s) che chiama std::srand(s). Quindi inizializza (o re-inizializza) la sequenza di numeri pseudo-casuali usata da std::rand() in tutto il codice C++ della simulazione. Da quel momento, ogni chiamata a rand() restituirà la stessa sequenza dato lo stesso seed. 

- Quando viene chiamata
La chiami dentro CellSimEnv.reset(..., seed=...) in rl_env.py: ogni reset, se passi un seed, riallinea sia l’RNG Gym (con super().reset(seed=...)) sia il RNG C++ (con cell_sim.seed(...)). Quindi l’episodio parte sempre dallo stesso stato casuale lato C++ se usi lo stesso seed. 

- Cosa cambia “sul campo”
Qualsiasi parte della libreria C++ che usi std::rand() (es. decisioni stocastiche su crescita/morte, posizionamenti casuali, perturbazioni, ecc.) diventa riproducibile: stesse azioni → stessi eventi casuali → stesse traiettorie, finché l’ordine delle chiamate a rand() resta uguale.

- Perché c’è & 0xFFFFFFFF
Maschera il seed a 32-bit non segnato (range 0…2³²−1) così il valore è sempre compatibile con l’argomento unsigned int passato a std::srand. Semi negativi o enormi vengono mappati/modulati in modo stabile. La logica della maschera la vedi nella tua reset. 

- Cosa NON fa
    - Non tocca l’RNG di Python, NumPy o PyTorch (quelli li setti con seed_everything in train.py). 
    - Non influenza generatori C++ diversi da std::rand() (es. std::mt19937), se mai venissero usati nella libreria.

Nota importante: stato globale
std::rand() ha stato globale di processo: tutte le istanze/oggetti della simulazione lo condividono. Re-seedarlo durante l’esecuzione “riavvolge” la sequenza per tutto il codice che usa rand().

## Cosa sono PYTHONPATH e sys.path?

- sys.path è una lista di directory che Python esplora nell’ordine per cercare i moduli o pacchetti che vuoi importare.
- PYTHONPATH è una variabile d’ambiente del sistema operativo (come PATH o HOME) che serve per aggiungere directory personalizzate a sys.path.

In altre parole:
- sys.path è la lista effettiva usata da Python a runtime;
- PYTHONPATH è un modo per modificarla prima che Python parta.

Nel nostri caso togliere i file __init__.py renderebbe gli import più verbosi e ti farebbe perdere le scorciatoie/export definiti ora; conviene tenerli finché vuoi mantenere questa interfaccia unica per il package.
