# 🚀 Compilare ed Eseguire `test_grid.cpp` con CMake in VSCode

## Indice

1. **Introduzione**
2. **Struttura del progetto**
3. **Usare CMake con `tasks.json` e `launch.json`**
   - Creare `CMakeLists.txt`
   - Generare la cartella di build ed eseguire CMake
   - Creare `tasks.json` per la compilazione
   - Creare `launch.json` per eseguire il programma
   - Eseguire il codice
4. **Usare CMake Tools (Senza JSON, più automatico)**
   - Installare "CMake Tools" in VSCode
   - Creare il file `CMakeLists.txt`
   - Configurare CMake
   - Compilare il progetto
   - Eseguire il codice
5. **Differenze nei comandi di compilazione ed esecuzione**
   - CMake con `tasks.json` e `launch.json`
   - CMake Tools (Automatico)
6. **Funzione del file `CMakeLists.txt`**
   - Definizione del progetto
   - Impostazione delle opzioni di compilazione
   - Definizione degli eseguibili e dei file sorgente
   - Inclusione di librerie e dipendenze
   - Specifica delle directory di inclusione
   - Definizione delle opzioni di compilazione personalizzate

## Introduzione

Immaginiamo di volere compilare ed eseguire un file c++ `test_grid.cpp` che dipende a sua volta da altri file.

Possiamo fare questo in due modi diversi

1️⃣ **Uso di CMake con `tasks.json` e `launch.json`** (configurazione manuale)
- Questo metodo richiede la creazione manuale di file di configurazione (`tasks.json` per la compilazione e `launch.json` per il debug).
- È utile se vuoi controllare il processo di build ed esecuzione con impostazioni personalizzate.
- Permette di usare direttamente il pulsante **"Run"** di VSCode per eseguire il programma.

2️⃣ **Uso di CMake Tools (senza JSON, automatizzato)**
- Con questo metodo, non è necessario creare `tasks.json` o `launch.json`, perché l'estensione **CMake Tools** gestisce automaticamente la configurazione, la compilazione e il debug.
- Offre un'esperienza più semplice e diretta, con comandi come "`CMake: Configure`", "`CMake: Build`" e "`CMake: Debug`".
- Il pulsante "**Run**" di VSCode non funziona direttamente senza una configurazione aggiuntiva, ma puoi eseguire il codice tramite il **Command Palette** (Ctrl+Shift+P) o la barra di stato di CMake Tools.

---

## **🔹 Struttura del progetto**
La struttura dei file del progetto è la seguente:

```
progetto/
│── src/
│   ├── test_grid.cpp
│   ├── grid_3d.cpp
│   ├── grid_3d.h
│   ├── cell.cpp
│   ├── cell.h
│── CMakeLists.txt
│── build/ (verrà generata dopo)
```

---

## **1️⃣ Usare CMake con `tasks.json` e `launch.json`**

### **Passaggi**

### 🔹 **1. Creare `CMakeLists.txt` (se non esiste)**
📌 Il file `CMakeLists.txt` deve essere nella root del progetto:
```cmake
cmake_minimum_required(VERSION 3.10)
project(MyProject)

set(CMAKE_CXX_STANDARD 17)

add_executable(test_grid src/test_grid.cpp src/grid_3d.cpp src/cell.cpp)
```

### 🔹 **2. Generare la cartella di build ed eseguire CMake**
Aprire il terminale ed eseguire:
```bash
rm -rf build  # Pulizia (opzionale)
cmake -S . -B build  # Configurazione del progetto
cmake --build build  # Compilazione
```

### 🔹 **3. Creare `tasks.json` per la compilazione**
📌 Crea il file `.vscode/tasks.json` e inserisci:
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "CMake Build",
            "type": "shell",
            "command": "cmake",
            "args": [
                "--build",
                "${workspaceFolder}/build"
            ],
            "group": {
                "kind": "build",
                "isDefault": true
            },
            "problemMatcher": ["$gcc"]
        }
    ]
}
```

### 🔹 **4. Creare `launch.json` per eseguire il programma**
📌 Crea il file `.vscode/launch.json` e inserisci:
```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug test_grid",
            "type": "cppdbg",
            "request": "launch",
            "program": "${workspaceFolder}/build/test_grid",
            "args": [],
            "stopAtEntry": false,
            "cwd": "${workspaceFolder}/build",
            "environment": [],
            "externalConsole": false,
            "MIMode": "gdb",
            "setupCommands": [
                {
                    "description": "Enable pretty-printing for gdb",
                    "text": "-enable-pretty-printing",
                    "ignoreFailures": true
                }
            ],
            "preLaunchTask": "CMake Build"
        }
    ]
}
```

### 🔹 **5. Eseguire il codice**
✅ **Compilare** (`Ctrl+Shift+B` → seleziona "CMake Build")  
✅ **Eseguire** (`F5`, cliccando il pulsante **Run** di VSCode o usando il terminale con `./build/test_grid`)  

📌 **Quando premi il pulsante "Run"**
- VSCode compila automaticamente il progetto usando "CMake Build".
- Dopo la compilazione, esegue `test_grid`.
- Il programma gira nel terminale di VSCode.

---

## **2️⃣ Usare CMake Tools (Senza JSON, più automatico)**

### **Passaggi**

### 🔹 **1. Installare "CMake Tools" in VSCode**
- Apri **VSCode** → Vai su **Extensions (`Ctrl+Shift+X`)** → Cerca **"CMake Tools"** e installalo.

### 🔹 **2. Creare il file `CMakeLists.txt`**
📌 Il file `CMakeLists.txt` deve essere nella root del progetto:
```cmake
cmake_minimum_required(VERSION 3.10)
project(MyProject)

set(CMAKE_CXX_STANDARD 17)

add_executable(test_grid src/test_grid.cpp src/grid_3d.cpp src/cell.cpp)
```

### 🔹 **3. Configurare CMake**
Apri il **Command Palette (`Ctrl+Shift+P`)** → cerca **"CMake: Configure"** e selezionalo.  
Se ti chiede di scegliere un kit di compilazione, seleziona **GCC** (o il tuo compilatore corretto).

### 🔹 **4. Compilare il progetto**
Apri il **Command Palette (`Ctrl+Shift+P`)** → cerca **"CMake: Build"** e selezionalo. Compila il progetto senza avviare il debugger.


### 🔹 **5. Eseguire il codice**
✅ **Metodo 1:** Apri il Command Palette (`Ctrl+Shift+P`) → cerca **"CMake: Run Without Debugging"**. Lanciando questo comando vine eseguita la compilazione (sia del file di lavoro che di quelli da cui dipende quest'ultimo). 

✅ **Metodo 2:** Apri il terminale ed esegui manualmente:
```bash
./build/test_grid
```
✅ **Metodo 3:** Se vuoi fare il debug, premi **F5** o usa **"CMake: Debug"** dal Command Palette. **NOTA: F5 è l'equivalentedi lanciare "CMake: Debug" il quale ESEGUE ANCHE LA COMPILAZIONE**.

---

## 📌 Differenze nei comandi di compilazione ed esecuzione

### 🔹 **1️⃣ CMake con `tasks.json` e `launch.json` (Manuale)**

| **Operazione**      | **Comando** |
|--------------------|------------|
| **Configurare CMake** | `cmake -S . -B build` |
| **Compilare il progetto** | `cmake --build build` oppure `Ctrl+Shift+B` ("CMake Build") |
| **Eseguire il programma** | `./build/test_grid` nel terminale oppure `F5` (VSCode "Run") |
| **Debuggare il programma** | `F5` (VSCode "Run") con `launch.json` configurato |

### 💙 **2️⃣ CMake Tools (Automatico)**

| **Operazione**          | **Comando** |
|------------------------|------------|
| **Configurare CMake** | `Ctrl+Shift+P` → "CMake: Configure" |
| **Compilare il progetto** | `Ctrl+Shift+B` oppure `Ctrl+Shift+P` → "CMake: Build" |
| **Eseguire il programma** | `Ctrl+F5` oppure `Ctrl+Shift+P` → "CMake: Run Without Debugging" oppure `./build/test_grid` nel terminale (se il file eseguibile è in `build/`) |
| **Debuggare il programma** | `F5` oppure `Ctrl+Shift+P` → "CMake: Debug" |


✅ **CMake Tools** rende tutto più automatico, mentre con **`tasks.json` e `launch.json`** hai più controllo manuale sul processo di compilazione ed esecuzione.


## 📌 Funzione del file `CMakeLists.txt`

Il file `CMakeLists.txt` è il cuore della configurazione del progetto CMake. Serve a definire come il progetto deve essere configurato, compilato ed eseguito. Ecco i principali compiti di questo file:

### 🔹 **1. Definizione del progetto**
La prima riga solitamente specifica la versione minima richiesta di CMake e il nome del progetto:
```cmake
cmake_minimum_required(VERSION 3.10)
project(MyProject)
```
Questa impostazione garantisce che il progetto venga compilato con una versione compatibile di CMake.

### 🔹 **2. Impostazione delle opzioni di compilazione**
Ad esempio, puoi specificare la versione dello standard C++ da usare:
```cmake
set(CMAKE_CXX_STANDARD 17)
```
Questo assicura che il compilatore utilizzi C++17.

### 🔹 **3. Definizione degli eseguibili e dei file sorgente**
Qui si specificano i file che compongono l'eseguibile:
```cmake
add_executable(test_grid src/test_grid.cpp src/grid_3d.cpp src/cell.cpp)
```
In questo caso, `test_grid` è l'eseguibile che verrà generato a partire dai file sorgente elencati.

### 🔹 **4. Inclusione di librerie e dipendenze**
Se il progetto utilizza librerie esterne, puoi includerle nel file `CMakeLists.txt`. Ad esempio:
```cmake
find_package(OpenGL REQUIRED)
target_link_libraries(test_grid OpenGL::GL)
```
Questo comando cerca la libreria OpenGL e la collega all'eseguibile.

### 🔹 **5. Specifica delle directory di inclusione**
Se i file header (`.h`) sono in una directory specifica, è possibile indicarlo:
```cmake
include_directories(${CMAKE_SOURCE_DIR}/include)
```
Così il compilatore saprà dove trovare i file `.h`.

### 🔹 **6. Definizione delle opzioni di compilazione personalizzate**
Se vuoi attivare le ottimizzazioni o avvisi specifici, puoi farlo con:
```cmake
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -O2")
```
