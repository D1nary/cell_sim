# Specifica la versione minima richiesta di CMake
cmake_minimum_required(VERSION 3.10)

# Questa riga assicura che l'utente abbia almeno la versione 3.10 di CMake.
# Se l'utente ha una versione inferiore, CMake mostrerà un errore.

# Definisce il nome del progetto
# Il nome del progetto viene utilizzato internamente da CMake per organizzare la configurazione del progetto.
project(TestGrid)


# Imposta lo standard di C++
# Se il compilatore non supporta C++17, la configurazione fallirà.
set(CMAKE_CXX_STANDARD 17) # Utilizza lo standard C++17
set(CMAKE_CXX_STANDARD_REQUIRED True) # Obbliga l'uso di C++17

# Aggiunge l'eseguibile del progetto
# Il primo argomento (test_grid) è il nome dell'eseguibile generato
# I file successivi sono i file sorgente necessari per la compilazione

# I file di codice sorgente necessari per la compilazione sono test_grid.cpp, grid_3d.cpp e cell.cpp.
# Gli header (grid_3d.h e cell.h) non vengono inclusi esplicitamente perché vengono automaticamente inclusi dai file .cpp.
add_executable(test # Eseguibile che verrà generato nella cartella build
    src/test.cpp  # File principale che contiene la funzione main
    src/controller_3d.cpp # File sorgente con l'implementazione della classe Controller
    src/grid_3d.cpp    # File sorgente con l'implementazione della classe Grid
    src/cell.cpp       # File sorgente con l'implementazione della classe cell
)



# La direttiva target_include_directories(<target> <ACCESS_MODE> <DIRECTORY>...) in CMake 
# serve per specificare 
# le directory in cui si trovano i file di intestazione (.h) necessari per la 
# compilazione di un target. Dove:
# <target> → Il nome del target, ovvero l'eseguibile o la libreria a cui si applica la direttiva.
# <ACCESS_MODE> → Il tipo di accesso che le directory avranno rispetto ai target dipendenti.
# <DIRECTORY> → Una o più directory contenenti i file di intestazione (.h).
target_include_directories(test PRIVATE src)
