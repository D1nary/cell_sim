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

Contesto: questi metodi vengono esposti nei binding C++ → Python del controller, vedi rein/binding.cpp.

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

