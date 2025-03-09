# Componenti di un File Header e C++

Un programma C++ tipico è organizzato in file header (`.h`) e file sorgenti (`.cpp`):

1. File Header (`.h`):
    - Contiene dichiarazioni di classi, strutture, e funzioni.
    - Usa inclusioni condizionali (`#ifndef`, `#define`, `#endif`) per evitare problemi di doppia inclusione.
2. File Sorgente (`.cpp`):
    - Contiene l'implementazione delle funzioni e dei metodi definiti nel file header.
    - Include i file header necessari.

Nel nostro caso:
- `cell.h` Definisce una struttura base per le cellule e tre classi derivate: `HealthyCell`, `CancerCell`, e `OARCell`.
- `cell.cpp` Implementa le logiche operative delle classi.

I vantaggi dell'uso della combinazione di file header e c++ sono:
- **Separazione della Dichiarazione e dell'Implementazione**: Questa separazione rende il codice più organizzato e leggibile, facilitando la gestione di progetti di grandi dimensioni. Gli header descrivono l'interfaccia, mentre i file `.cpp` forniscono la logica.
- **Riutilizzo del Codice**: I file header possono essere facilmente riusati in diversi file `.cpp` senza duplicare il codice. Questo significa che puoi includere lo stesso header in più file `.cpp` per sfruttare le dichiarazioni comuni, evitando ripetizioni inutili e facilitando il riutilizzo del codice.
- **Manutenzione del Codice più Facile**: 
    - La separazione tra dichiarazione e implementazione rende il codice più manutenibile. Se devi modificare la logica di una funzione, puoi fare la modifica nel file `.cpp` senza dover alterare l'header, a meno che l'interfaccia non cambi.
    - Inoltre, i cambiamenti che non coinvolgono l'interfaccia (come l'ottimizzazione di un algoritmo) richiedono la ricompilazione solo del file `.cpp` modificato e non di tutti i file che includono l'header.
- **Miglioramento dei Tempi di Compilazione**: Usando i file header, il compilatore può utilizzare tecniche di compilazione incrementale. Quando viene modificato un file `.cpp`, il compilatore non deve ricompilare tutti gli altri file se l'interfaccia nei file header non è cambiata. Questo riduce il tempo di compilazione complessivo per grandi progetti.

## Fasi di Esecuzione di un File `.cpp`
Quando si esegue un file `.cpp`, il computer attraversa diverse fasi per trasformare il codice sorgente in un programma eseguibile. Di seguito sono descritte le fasi principali:

### 1. **Editing del Codice Sorgente**
- Il primo passo consiste nello scrivere il codice sorgente utilizzando un editor di testo o un ambiente di sviluppo integrato (IDE). Questo codice è salvato in un file con estensione `.cpp`.

### 2. **Preprocessing (Preprocessore)**
- Il preprocessore elabora le direttive incluse nel codice, come quelle che iniziano con `#` (ad esempio, `#include` o `#define`).
- Questo passaggio genera un nuovo file sorgente con tutte le direttive preprocessate, risolvendo riferimenti come `#include` per includere il contenuto dei file di intestazione (`.h`) e sostituendo macro definite con `#define`.

### 3. **Compilazione**
- Il compilatore trasforma il codice preprocessato in **linguaggio assembly**, un linguaggio a basso livello specifico per l'architettura del computer in uso.
- Questa fase verifica la correttezza sintattica del codice e traduce il codice C++ in istruzioni comprensibili per il computer a livello hardware.

### 4. **Assemblaggio**
- Il codice assembly viene poi passato all'**assembler**, che lo converte in **codice macchina**, generando così un file **oggetto** (`.o` o `.obj`), contenente il codice binario.

### 5. **Linking**
- Nella fase di linking, vengono combinati uno o più file oggetto e risolte le dipendenze con **librerie** esterne, come le librerie standard C++ o altre librerie di terze parti.
- Il linker produce un **file eseguibile** combinando tutti i file oggetto e assicurandosi che tutte le funzioni, variabili e riferimenti siano collegati correttamente.

### 6. **Caricamento**
- Il programma eseguibile viene poi caricato in **memoria** dal sistema operativo. In questa fase, vengono riservati spazio di memoria per il codice, le variabili e le risorse necessarie al programma.

### 7. **Esecuzione**
- Infine, il processore esegue il codice macchina caricato in memoria. Il **loader** del sistema operativo avvia il programma, gestisce la memoria dinamica e fornisce i puntatori necessari per l'esecuzione.

### Sintesi
In sintesi, le fasi di esecuzione di un file `.cpp` sono:

1. Editing
2. Preprocessing
3. Compilazione
4. Assemblaggio
5. Linking
6. Caricamento
7. Esecuzione

## **Puntatore**
In C++, un puntatore è una variabile che memorizza l'indirizzo di memoria di un'altra variabile. I puntatori sono una delle caratteristiche fondamentali del linguaggio C++ e sono utilizzati per manipolare la memoria direttamente, accedere a dati dinamici, gestire array e strutture, e implementare tecniche avanzate come passaggio per riferimento e polimorfismo.

Un puntatore si dichiara usando l'operatore `*` (asterisco). Esempio:
```c++
int a = 10;         // Una normale variabile
int* p = &a;        // Dichiarazione di un puntatore che punta alla variabile 'a'
```
- `a` è una normale variabile intera.
- `&a` restituisce l'indirizzo di memoria di `a` (operatore "address-of").
- `p` è un puntatore che memorizza l'indirizzo di `a`.

### Vantaggi e usi dei puntatori 
- Gestione dinamica della memoria: con funzioni come `new` e `delete`.
- Passaggio per riferimento: evita copie di grandi strutture nei parametri delle funzioni.
- Implementazione di strutture dati dinamiche: come liste collegate e alberi.
- Polimorfismo: utilizzato insieme ai puntatori a base class.

## **Macro**
Una **macro** in programmazione, soprattutto in C e C++, è un meccanismo fornito dal **preprocessore** per definire simboli o blocchi di codice che vengono sostituiti direttamente nel sorgente durante la fase di preprocessing, prima della compilazione vera e propria.

Una macro è definita utilizzando la direttiva **`#define`**. Esistono due tipi principali di macro:

1. **Macro semplici**:
   Queste assegnano un nome a un valore o a un testo, permettendo al preprocessore di sostituire tutte le occorrenze di quel nome con il valore o testo associato.

   ```cpp
   #define PI 3.14159
   ```

   In questo caso, ovunque nel codice compare `PI`, il preprocessore sostituirà con `3.14159`.

2. **Macro parametriche**:
   Funzionano come funzioni inline, ma vengono espanse durante il preprocessing.

   ```cpp
   #define SQUARE(x) ((x) * (x))
   ```

   Qui, `SQUARE(5)` sarà sostituito con `((5) * (5))`.


### Utilità delle Macro

1. **Semplificare il codice**:
   Le macro possono ridurre ripetizioni, permettendo di definire costanti o operazioni comuni.

2. **Portabilità**:
   Possono essere usate per adattare il codice a piattaforme diverse, definendo comportamenti condizionali con direttive come `#ifdef`.

3. **Prevenire inclusioni multiple**.

## Metodi / funzioni virtuali
Le funzioni virtuali e i metodi virtuali sono termini che vengono spesso usati in modo intercambiabile. In C++, la parola metodo si riferisce specificamente alle funzioni membro di una classe, mentre il termine funzione può riferirsi a qualsiasi funzione definita nel programma. Tuttavia, quando parliamo di "virtuale" nel contesto delle classi, si tratta sempre di funzioni membro, che sono chiamate metodi virtuali.

Una funzione virtuale (o metodo virtuale) in C++ è una funzione membro di una classe che può essere sovrascritta nelle classi derivate. La parola chiave `virtual` indica che una funzione è destinata a essere dinamicamente associata agli oggetti durante l'esecuzione, il che significa che viene deciso quale versione della funzione chiamare a runtime invece che a compile-time.

Questo comportamento permette il polimorfismo, che è una delle caratteristiche fondamentali della programmazione orientata agli oggetti (OOP). Quando si utilizza un puntatore o un riferimento a una classe base per gestire un oggetto di una classe derivata, la funzione virtuale garantisce che venga chiamata la versione corretta, ovvero quella più specifica.

### Sintassi
Una funzione virtuale viene dichiarata utilizzando la parola chiave virtual nella classe base:
```c++
class Base {
public:
    virtual void stampa() {
        std::cout << "Chiamata a Base::stampa" << std::endl;
    }
};
```
- `virtual`: Parola chiave per indicare che la funzione è virtuale.
- `void stampa()`: Nome e firma della funzione.

### Comportamento Polimorfico
Il polimorfismo dinamico è la caratteristica principale delle funzioni virtuali. Permette di utilizzare un puntatore alla classe base per chiamare il metodo appropriato di una classe derivata. Questo avviene grazie al dynamic dispatch, ovvero il meccanismo che seleziona l'implementazione corretta a runtime. Esempio:
```c++
#include <iostream>
using namespace std;

// Classe base
class Animale {
public:
    virtual void parla() const {
        cout << "L'animale fa un suono generico" << endl;
    }
    
    virtual ~Animale() = default; // Distruttore virtuale per garantire una distruzione corretta
};

// Classe derivata Cane
class Cane : public Animale {
public:
    void parla() const override {
        cout << "Il cane dice: Bau Bau" << endl;
    }
};

// Classe derivata Gatto
class Gatto : public Animale {
public:
    void parla() const override {
        cout << "Il gatto dice: Miao Miao" << endl;
    }
};

// Funzione che accetta un puntatore alla classe base
void faiParlareAnimale(const Animale* animale) {
    animale->parla(); // Chiama il metodo "parla" appropriato a seconda dell'oggetto
}

int main() {
    Animale* a = new Cane();   // Puntatore alla classe base che punta a un oggetto Cane
    Animale* b = new Gatto();  // Puntatore alla classe base che punta a un oggetto Gatto

    faiParlareAnimale(a); // Output: "Il cane dice: Bau Bau"
    faiParlareAnimale(b); // Output: "Il gatto dice: Miao Miao"

    // Pulizia della memoria
    delete a;
    delete b;

    return 0;
}
```
Alcuni chiarimenti:
- L'utilizzo di `const` nel parametro della funzione `faiParlareAnimale` serve a garantire che l'oggetto puntato dal puntatore passato alla funzione non venga modificato all'interno della funzione stessa.
-  `Animale* a = new Cane();`: 
    - `Animale* a;`: Creazionr di un puntatore `a` che può puntare a un oggetto di tipo `Animale` o di una classe derivata.
    - `a = new Cane();`

**Cosa Succederebbe Senza virtual?**
Se il metodo `parla()` nella classe base non fosse dichiarato virtual, il comportamento polimorfico non avverrebbe:

- Se il metodo non è `virtual`, la chiamata animale->parla() nella funzione `faiParlareAnimale()` chiamerebbe sempre la versione della classe base (`Animale::parla()`), anche se il puntatore punta a un oggetto `Cane` o `Gatto`.
- Questo significa che l'output sarebbe `"L'animale fa un suono generico"` per entrambe le chiamate, il che non è il comportamento desiderato. 

**Override**
Nell'esempio precedente possiamo ossservare l'`override` cioè  il processo mediante il quale una classe derivata fornisce una propria implementazione di una funzione virtuale della classe base. In questo esempio, le classi `Cane` e `Gatto` sovrascrivono (`override`) la funzione `parla()` della classe base `Animale` per dare un comportamento più specifico:

- `Cane` stampa `"Il cane dice: Bau Bau"`.
- `Gatto` stampa `"Il gatto dice: Miao Miao"`.

L'utilizzo della parola chiave `override` è opzionale, ma è una buona pratica.

### Funzioni Virtuali Pure e Classi Astratte
Una funzione virtuale pura è una funzione virtuale che viene dichiarata nella classe base, ma che non ha un'implementazione, costringendo le classi derivate a fornire una propria implementazione. Una funzione virtuale pura viene dichiarata assegnandola a `0`.
```c++
class BaseAstratta {
public:
    virtual void stampa() = 0; // Funzione virtuale pura
};
```
Quando una classe contiene almeno una funzione virtuale pura, essa diventa una **classe astratta** e non può essere istanziata direttamente. Serve solo come base per altre classi che devono fornire l'implementazione delle funzioni virtuali pure.

### `Override` e `final`
- `override`: Come detto prima, la parola chiave override viene utilizzata per indicare esplicitamente che una funzione in una classe derivata sta sovrascrivendo una funzione virtuale della classe base. È un buon strumento per evitare errori di scrittura, poiché se la funzione non corrisponde correttamente a una funzione della classe base, il compilatore genererà un errore.

- `final`: Impedisce che una funzione virtuale venga ulteriormente sovrascritta nelle classi derivate successive.

```c++
class Derivata : public Base {
public:
    void stampa() final {
        std::cout << "Chiamata a Derivata::stampa" << std::endl;
    }
};
```
In questo esempio, `stampa()` non può essere sovrascritta da altre classi che derivano da `Derivata`.


## Problema dell'Ereditarietà Multipla: Il Diamond Problem / Classi virtuali
Quando si utilizza l'ereditarietà multipla, può capitare che una classe erediti da più classi base che, a loro volta, derivano da una classe comune. Questo può portare al cosiddetto problema del diamante (**diamond problem**). Consideriamo l'esempio seguente:
```c++
class A {
public:
    void stampa() {
        std::cout << "Classe A" << std::endl;
    }
};

class B : public A {
};

class C : public A {
};

class D : public B, public C {
};

int main() {
    D d;
    d.stampa(); // Quale metodo stampa() dovrebbe essere chiamato?
    return 0;
}
```
In questo esempio:
- La classe `A` è una classe base.
- `B` e `C` derivano entrambe da `A`.
- La classe `D` eredita sia da `B` che da `C`.


Quando cerchiamo di chiamare `d.stampa()` su un oggetto di tipo `D`, il compilatore non sa quale versione di `stampa()` chiamare: quella ereditata da `B` o quella ereditata da `C`? Questo è il problema del diamante: ci sono due copie della classe `A` all'interno dell'oggetto `D`, il che può portare a confusione e ambiguità.

Per risolvere il problema del diamante, C++ offre l'**ereditarietà virtuale**. Quando una classe viene ereditata in modo virtuale, si garantisce che la classe base venga condivisa da tutte le classi derivate, evitando duplicazioni.

Per esempio:
```c++
class A {
public:
    void stampa() {
        std::cout << "Classe A" << std::endl;
    }
};

class B : virtual public A {
};

class C : virtual public A {
};

class D : public B, public C {
};

int main() {
    D d;
    d.stampa(); // Ora chiama correttamente Classe A senza ambiguità
    return 0;
}
```
In questo esempio:

- `B` e `C` ereditano virtualmente da `A` usando la sintassi `virtual public A`.
- La classe `D`, che eredita da `B` e `C`, ora ha una sola copia di `A` nella sua gerarchia, eliminando l'ambiguità.

Quando una classe eredita in modo virtuale, viene creata una singola copia della classe base in tutta la gerarchia degli oggetti derivati. Questo significa che qualsiasi classe che erediti da una classe base virtuale avrà una sola copia dei membri della classe base, indipendentemente dal numero di percorsi di ereditarietà. Questo garantisce una migliore gestione della memoria

## override

La parola chiave `override` viene utilizzata per indicare esplicitamente che un metodo di una classe derivata sta **ridefinendo** un metodo virtuale dichiarato nella classe base.

#### Vantaggi dell'uso di `override`

1. **Sicurezza del Tipo**: L'uso di `override` aiuta a evitare errori accidentali quando si vuole ridefinire un metodo della classe base, ma si commette un errore nella firma del metodo.
2. **Migliora la Manutenibilità del Codice**: Quando un metodo viene marcato con `override`, il compilatore verifica che esista un metodo virtuale con la stessa firma nella classe base.
3. **Maggiore Chiarezza**: L'uso di `override` rende il codice più leggibile e chiaro, facilitando la comprensione del comportamento del codice per gli sviluppatori.

### Esempio

Consideriamo le seguenti due classi: la classe base `Cell` e la classe derivata `HealthyCell`:

```c++
class Cell {
public:
    virtual void radiate(double dose) = 0;
};
```

La classe `HealthyCell` ridefinisce il metodo `radiate`:

```c++
class HealthyCell : public Cell {
public:
    void radiate(double dose) override {
        // Implementazione specifica per HealthyCell
    }
};
```

- **Senza `override`**: Se per errore si cambia la firma del metodo in `HealthyCell` (ad esempio, si usa `void radiate(int dose)`), il compilatore non darebbe errore, ma `HealthyCell` non sovrascriverebbe il metodo virtuale di `Cell`, creando un nuovo metodo diverso. Questo porterebbe a comportamenti inattesi.
- **Con `override`**: Se aggiungi `override` e sbagli la firma del metodo, il compilatore segnala immediatamente l'errore, evitando errori di comportamento.

### In Sintesi

L'uso di `override` non è obbligatorio, ma è fortemente consigliato, perché fornisce una verifica a livello di compilazione che il metodo stia effettivamente ridefinendo un metodo virtuale della classe base. Questo rende il codice più sicuro, manutenibile e leggibile.

## Costruttore
Un costruttore in C++ è una funzione speciale di una classe che viene chiamata automaticamente ogni volta che un nuovo oggetto della classe viene creato. Il suo scopo principale è inizializzare gli oggetti della classe.

**Caratteristiche Principali**
1. Il costruttore ha lo stesso nome della classe a cui appartiene e non ha un valore di ritorno (nemmeno `void`)
    ```c++
    class MyClass {
    public:
        MyClass();  // Costruttore
    };
    ```
2. Viene Eseguito Automaticamente. Non bisogna chiamarlo esplicitamente. Si attiva automaticamente quando si crea un oggetto:
    ```c++
    MyClass obj;  // Il costruttore viene chiamato automaticamente
    ```
3. Può Avere Parametri:

    ```c++
    class MyClass {
    public:
        MyClass(int x, int y);  // Costruttore con parametri
    };
    MyClass obj(10, 20);       // Passaggio di valori al costruttore
    ```
4. Supporta la Lista di Inizializzazione: La lista di inizializzazione è un modo per inizializzare i membri della classe prima che venga eseguito il corpo del costruttore:
    ```c++
    MyClass::MyClass(int x, int y) : member1(x), member2(y) {}
    ```

5. Costruttori di Default e Personalizzati:
    - Se non viene definito nessun costruttore, il compilatore genera automaticamente un costruttore di `default`.
    - Puoi definire costruttori personalizzati per inizializzazioni specifiche.

**Tipologie di Costruttori**
1. **Costruttore di Default**: Non accetta parametri e può essere generato automaticamente dal compilatore
    ```c++
    class MyClass {
    public:
        MyClass() { /* Inizializzazione di default */ }
    };
    ```
2. **Costruttore Parametrizzato**: Accetta parametri per inizializzare i membri con valori specifici
    ```c++
    class MyClass {
    public:
        MyClass(int x) : value(x) {}
    private:
        int value;
    };
    ```
3. **Costruttore di Copia**: Crea un nuovo oggetto copiando un oggetto esistente
    ```c++
    MyClass(const MyClass& other);
    ```
4. **Costruttore di Spostamento (Move Constructor)**: Viene utilizzato per "trasferire" risorse da un oggetto temporaneo.
    ```c++
    MyClass(MyClass&& other);
    ```

## Include (<span style="color: red;">file .cpp</span>)
Le seguenti righe rappresentano elementi fondamentali di un file header in C++:

```c++
#ifndef RADIO_RL_CELL_H
#define RADIO_RL_CELL_H
```

Queste righe sono un esempio di una direttiva di **inclusione condizionale** chiamata "**Include Guard**". Viene usata una combinazione di **`#ifndef`**, **`#define`**, e **`#endif`**. E' necessario per evitare **inclusioni multiple** di un file header in un programma C++. Durante la compilazione, un file header potrebbe essere incluso più volte se viene richiamato da file diversi che includono lo stesso file. Questo può causare errori, ad esempio:

- Dichiarazioni ripetute di classi, funzioni, o variabili globali.
- Conflitti nel linker o compilatore.

### Uso di **`#ifndef`**, **`#define`**, e **`#endif`**:
- **`#ifndef RADIO_RL_CELL_H`**: Verifica se il macro `RADIO_RL_CELL_H` non è ancora definito.
- **`#define RADIO_RL_CELL_H`**: Se il macro non è definito, lo definisce per la prima volta.
- Tutto il codice all'interno viene incluso solo se il macro non è già stato definito.
- Quando il compilatore trova `#endif`, completa il blocco di inclusione condizionale, evitando ridondanze.


## Dichiarazione classe derivata (<span style="color: green;">file header</span>)
```c++
class HealthyCell : public Cell {}
```
 La sintassi `: public Cell` viene utilizzata per indicare che la classe `HealthyCell` eredita dalla classe base `Cell`. 
 In questo caso, la parola chiave `public` specifica il livello di accesso per l'ereditarietà.
Quando una classe eredita pubblicamente da un'altra classe (`public Cell`), significa che i membri pubblici e protetti della classe base Cell manterranno il loro livello di accesso originale nella classe derivata `HealthyCell`. In particolare:
- I membri `public` della classe base rimangono public nella classe derivata.
- I membri `protected` della classe base rimangono protected nella classe derivata.
- I membri `private` della classe base non sono accessibili direttamente nella classe derivata.
---

## Variabile static
Un esempio di dichiarazione di una variabile static lo si ha nel file `header` nella dichiarazione della classe `HealthyCell`(`static int count;`). Dichiarare una variabile come `static`, significa che la variabile è condivisa tra tutte le istanze (cioè tutti gli oggetti creati a partire dalla classe) della classe in cui è dichiarata. 
Questo è diverso da una variabile membro normale, che appartiene a ciascuna istanza separata della classe.

## Modificatori di Accesso (`protected`, `public` e `private`)
- `protected`: Gli attributi e i metodi protected sono accessibili solo dalla classe stessa e dalle classi derivate.
- `public`: Le variabili e funzioni dichiarate con questo modificatore sono accessibili da qualsiasi parte del programma. 
- `private:`: Significa che può essere accessibile solo all'interno della classe in cui è stato definito. Al di fuori della classe, questi membri non possono essere usati direttamente, nemmeno dalle classi derivate.


---
## Distribuzione normale
```c++
normal_distribution<double> norm_distribution(1.0, 0.3333333);
```
crea una distribuzione normale (o Gaussiana) parametrizzata. Analizziamo le sue componenti:
1. `normal_distribution<double>`:
    - È una classe template della libreria `<random>` di C++.
    - Rappresenta una distribuzione normale continua per generare numeri casuali.
    - Il tipo `double` specifica che i numeri generati saranno in virgola mobile.
2. `norm_distribution`:
    - È il nome dell'oggetto istanziato dalla classe `normal_distribution`.
    - Può essere usato per generare numeri casuali secondo la distribuzione definita.
3. `(1.0, 0.3333333)`:
    - Sono i parametri che definiscono la distribuzione:
        - Media (`mean`) = 1.0:
        - Deviazione standard (stddev) = 0.3333333:
            - Circa il 68% dei valori generati sarà compreso nell'intervallo `[0.6666667, 1.3333333]` (media ± deviazione standard).
---
## Commenti
```c++
/**
 * Constructor of the abstract class Cell
 *
 * @param stage Current stage of the cell in the cell cycle
 */
```

Commento multi-linea.
- `@param` serve a descrivere i parametri di una funzione o di un costruttore. 
- `stage` è il nome del parametro.

Questo tipo di commenti è utile per rendere il codice più leggibile e per strumenti di generazione di documentazione (come Doxygen) che estraggono e formattano automaticamente queste informazioni per creare documentazione leggibile. Altri Tag di Documentazione Comuni:

- `@param`: Descrive i parametri di input.
- `@return`: Spiega cosa restituisce la funzione (se non è `void`).
- `@throws` o @exception: Descrive eccezioni o errori che la funzione potrebbe sollevare.
- `@brief`: Fornisce una breve descrizione dell'elemento documentato.
- `@details`: Aggiunge una descrizione più dettagliata.


## Struttura `struct`
Una `struct` in C++ è un tipo di dato composto che permette di raggruppare più variabili sotto un unico nome. Queste variabili all'interno della `struct` vengono chiamate **membri** o **campi**. 
La `struct` è utile quando abbiamo bisogno di rappresentare un oggetto o un'entità che ha più attributi.

Nel caso della simualzione cellulare, all'interno del file `header`, abbiamo la struttura `cell_cycle_res`:

```c++
typedef struct {
double glucose;
double oxygen;
char new_cell;
} cell_cycle_res;
```
Quando andiamo a definire un metodo, per esempio con `cell_cycle_res cycle(double glucose, double oxygen, int neigh_count) override;` (classe `HealthyCell` nel file `header`), stiamo dicendo che che `cell_cycle_res` è il tipo di ritorno della funzione `cycle`. In altre parole, quando la funzione `cycle` viene chiamata, restituisce un oggetto di tipo `cell_cycle_res`. 

## Definizione di un costruttore
Consideriamo le righe di codice presenti nel file `.cpp` della simulazione:
```c++
HealthyCell::HealthyCell(char stage): Cell(stage) {
    count++;
    double factor = max(min(norm_distribution(generator), 2.0), 0.0);
    glu_efficiency = factor * average_glucose_absorption;
    oxy_efficiency = factor * average_oxygen_consumption;
    alive = true;
}
```
Stiamo implemendando il costruttore della classe `HealthyCell`.
1. `HealthyCell::HealthyCell(char stage)`
    - Il primo `HealthyCell` (prima dei due punti `::`) si riferisce al nome della classe, mentre il secondo `HealthyCell` (subito dopo `::`) è il nome del costruttore. In questo caso, il costruttore prende in ingresso un singolo parametro `char stage`. 
    - Il doppio due punti (`::`) è l'operatore di risoluzione dell'ambito e serve per indicare che il costruttore appartiene alla classe HealthyCell.
2. `: Cell(stage)`
    - Questa parte è chiamata lista di inizializzazione del costruttore.
    - `Cell(stage)` è una chiamata al costruttore della classe base `Cell` da cui `HealthyCell` eredita.
    - Poiché `HealthyCell` è una sottoclasse di `Cell` (definita nel file di intestazione cell.h), la lista di inizializzazione serve per passare il parametro `stage` al costruttore della classe base.
    - In pratica, `Cell(stage)` viene chiamato per inizializzare gli attributi ereditati dalla classe base `Cell` prima che il corpo del costruttore di `HealthyCell` venga eseguito.

### Come mai in `HealthyCell::HealthyCell(char stage): Cell(stage)`, usiamo `char stage` e non solo `stage`? 
La domanda sorge dal fatto che `char stage` è già scritto nel file header. Quindi non possiamo scrivere solo stage?
- Nel file header (`cell.h`), viene dichiarato il costruttore di `HealthyCell`. Una dichiarazione serve a informare il compilatore sull'esistenza del costruttore e sul tipo di parametro che accetta (`char stage`).
- Nel file di implementazione (`.cpp`), invece, viene definito il costruttore, specificando effettivamente come viene implementato.
- Quando si definisce un costruttore (o qualsiasi funzione), si deve ripetere la lista dei parametri con i loro tipi, anche se questi sono stati già dichiarati nel file header. Questo perché la definizione è una parte separata, dove si specifica come la funzione funziona effettivamente.

### Come mai in `:Cell(stage)` manca `char` all'interno delle parentesi `()`?

La parte `:Cell(stage)` è una lista di inizializzazione che viene usata per chiamare il costruttore della classe base (`Cell`) e passare un valore (`stage`) a tale costruttore.
In questa lista, `Cell(stage)` viene utilizzato per **richiamare** il costruttore della classe `Cell`, passando come argomento il valore di `stage`, che è stato precedentemente definito nel costruttore di `HealthyCell`.

Allo stesso modo, con 
```c++
Cell::Cell(char stage):age(0), stage(stage), alive(true), repair(0)  {}
```
stiamo definendo il costruttore della classe base `Cell` e utilizzando la lista di inizializzazione dei membri per inizializzare gli attributi della classe. Come nel caso precedente:
- Il primo `Cell` si riferisce al nome della classe.
- Il secondo `Cell` (dopo `::`) è il nome del costruttore.
- `char stage` è un parametro del costruttore che viene passato quando viene creata un'istanza della classe `Cell`.
- Dopo i due punti inizia la lista di inizializzazione, che serve per inizializzare direttamente i membri della classe prima dell'esecuzione del corpo del costruttore.

## Lista di inizializzazione
La **Lista di Inizializzazione** in C++ è una sintassi che consente di inizializzare i membri di una classe prima che venga eseguito il corpo del costruttore. È particolarmente utile per migliorare le prestazioni e per inizializzare i membri della classe che richiedono una inizializzazione diretta. È utile poichè può evitare una doppia assegnazione dei membri. Ad esempio:
```c++
// Senza lista di inizializzazione
Cell::Cell(char stage) {
    age = 0;        // Prima "age" viene costruito (default) e poi assegnato
    this->stage = stage;
    alive = true;
    repair = 0;
}
```
In questo caso, `age` viene inizializzato al valore di default e successivamente sovrascritto a 0, causando un'operazione inutile.

**Come mai edge viene inizializzato ad  un valore di default?**

In C++, quando un membro di una classe viene inizializzato senza una lista di inizializzazione, viene eseguito il seguente processo per i membri della classe:

- **Costruzione implicita** (default): Se un membro ha un costruttore predefinito, esso viene automaticamente chiamato prima che il corpo del costruttore della classe venga eseguito.

    - Nel caso di tipi primitivi come int, il valore non viene inizializzato in modo esplicito, quindi può contenere un valore casuale (garbage value) a meno che non venga assegnato un valore nel corpo del costruttore.

- Assegnazione esplicita nel corpo del costruttore: Successivamente, il membro può essere sovrascritto con un nuovo valore, come accade nel codice fornito.

Quindi nel nostro caso, la variabile `age` (e lo stesso vale per `repair` o altre variabili non inizializzate nella lista) segue questi passaggi:

- Durante la costruzione dell'oggetto Cell, ogni membro della classe viene inizializzato implicitamente (per tipi primitivi come int, non viene attribuito un valore specifico, lasciandolo con un valore casuale).
- Successivamente, nel corpo del costruttore, assegni esplicitamente age = 0, sovrascrivendo il valore iniziale.


Questo comportamento si verifica perché il costruttore della classe esegue implicitamente la costruzione dei membri prima di entrare nel corpo del costruttore stesso.

Con la lista di inizializzazione:
```c++
Cell::Cell(char stage) : age(0), stage(stage), alive(true), repair(0) {}
```
i membri sono direttamente inizializzati con i valori specificati, evitando la doppia operazione. 

## **Distruttori**
Un distruttore è una funzione speciale in una classe che viene chiamata automaticamente quando un oggetto della classe viene distrutto (ad esempio, quando il programma esce dall'ambito in cui è definito un oggetto, oppure quando si chiama `delete` su un puntatore).

Quando una classe base ha delle classi derivate, è possibile che un oggetto derivato venga cancellato usando un puntatore alla classe base. Questo è particolarmente comune quando si utilizza l'ereditarietà per gestire polimorfismo, ovvero quando si utilizzano puntatori della classe base per fare riferimento agli oggetti delle classi derivate.

Se il distruttore della classe base non è dichiarato come virtuale, quando si distrugge l'oggetto derivato tramite un puntatore alla classe base, verrà chiamato solo il distruttore della classe base. Questo potrebbe lasciare alcune risorse allocate dalla classe derivata non rilasciate correttamente, causando problemi come memory leak.

Un distruttore è una funzione membro della classe che ha lo stesso nome della classe, preceduto da `~` (tilde), e non ha parametri.

### **Tipi di distruttori**
1. **Distruttore Normale**:
Viene utilizzato per distruggere un oggetto senza ereditarietà o polimorfismo. Ogni classe ha un distruttore, e se non viene definito dall'utente, il compilatore ne fornisce uno di default.

    Sintassi:
    ```cpp
    ~NomeClasse();
    ```

2. **Distruttore Virtuale**:
Viene utilizzato per garantire la corretta distruzione di una classe derivata quando viene cancellata tramite un puntatore alla classe base. È essenziale per prevenire memory leak nelle gerarchie di classi.

    - Polimorfismo: Necessario quando si lavora con il polimorfismo e si utilizzano puntatori alla classe base per riferirsi a oggetti di classi derivate.
    - Ereditarietà: Garantisce che tutti i distruttori, sia della classe derivata che della classe base, vengano chiamati correttamente durante la distruzione dell'oggetto.

    Sintassi:
    ```cpp
    virtual ~NomeClasse();
    ```

3. **Distruttore Virtuale Puro**: 
Rende la classe astratta e impedisce l'istanza diretta della classe. Viene implementato per assicurare la corretta distruzione degli oggetti derivati.

    - Classe Astratta: Rende la classe non istanziabile direttamente, obbligando le classi derivate a implementare il distruttore.
    - Implementazione Necessaria: Sebbene sia dichiarato come puro (`= 0`), deve comunque avere una definizione per garantire la corretta gestione della memoria durante la distruzione degli oggetti derivati.

    Sintassi:
    ```cpp
    virtual ~NomeClasse() = 0;
    ```
    Definizione del distruttore:
    ```cpp
    NomeClasse::~NomeClasse() { /* implementazione */ }
    ```

    **In che senso *"non può essere istanziata direttamente"?***: Significa che non possiamo creare un oggetto di quella classe utilizzando il costruttore di base della classe stessa.

    Nel caso delle classi astratte in C++, la presenza di una o più funzioni virtuali pure (dichiarate con `= 0;`) rende la classe astratta. Ciò significa che la classe rappresenta un concetto generico o incompleto e non fornisce tutte le implementazioni necessarie per essere utilizzata come una normale classe. 
    Nel nostro caso, `Cell` è una classe astratta, quindi il seguente codice non sarebbe valido:
    ```c++
    Cell cell('1'); // Errore! 'Cell' è una classe astratta e non può essere istanziata direttamente.
    ```
    Il motivo per cui Cell non può essere istanziata direttamente è che essa non fornisce un'implementazione concreta per la funzione virtuale pura `cycle`. In altre parole, non esiste. Per poter creare un oggetto, dobbiamo usare una classe derivata che eredita da `Cell` che fornisce una propria implementazione per la funzione `cycle`.

4. **Distruttore `default`**: 
Indica al compilatore di generare automaticamente il distruttore predefinito. Questo è utile quando si vuole mantenere il comportamento di default del distruttore, ma si desidera specificarlo esplicitamente.

    - Esplicitazione: Utilizzato per dichiarare esplicitamente che il distruttore generato automaticamente è sufficiente, migliorando la leggibilità del codice.
    - Ottimizzazione: Permette di evitare la scrittura manuale del distruttore, lasciando al compilatore l'ottimizzazione del codice.

    Sintassi:
    ```cpp
    ~NomeClasse() = default;
    ```

5. **Distruttore `delete`**: 
Viene utilizzato per impedire la distruzione degli oggetti di una classe. Questo genera un errore di compilazione se si tenta di distruggere un oggetto, ed è utilizzato raramente per particolari esigenze di progettazione.

    - Prevenzione: Impedisce la distruzione degli oggetti, ad esempio per classi con istanze statiche che non dovrebbero mai essere distrutte.

    Sintassi:
    ```cpp
    ~NomeClasse() = delete;
    ```

## Implementazione di una funzione
Consideriamo:
```c++
cell_cycle_res OARCell::cycle(double glucose, double oxygen, int neigh_count)
```
- `cell_cycle_res`: È il tipo di ritorno della funzione, definito come un tipo `struct`.
- `OARCell::`: Specifica che la funzione `cycle` appartiene alla classe `OARCell`. Questa è una funzione membro che può essere invocata solo sugli oggetti di tipo `OARCell`. Questo vuol dire  che è una funzione membro di quella classe e, di conseguenza, appartiene specificamente alla classe `OARCell` e alle sue istanze.
- `cycle(double glucose, double oxygen, int neigh_count)`: Questa è la funzione `cycle` che stiamo andando ad implementare insieme ai relativi parametri di ingresso.


## Inizializzazione di una varibile
La seguente è la dichiarazione e l'inizializzazione di una variabile di tipo `cell_cycle_res`, che è una `struct`:  `cell_cycle_res result = {.0,.0,'\0'};`. La variabile `result`, essendo una `struct` di tipo `cell_cycle_res` avrà 3 attributi:
- `result.glucose`
- `result.oxygen`
- `result.new_cell` 

La notazione `'\0'` indica un carattere nullo (usato spesso per indicare una stringa vuota o un valore non definito per `new_cell`). `