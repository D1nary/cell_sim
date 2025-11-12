# Problema training (training 3)
## Reward
Possibili problemi:
- Funzione di reward costruita per il modello 2d
- Troppe cellule nella simulazione (modello 2d pate da una sola cellula tumorale centrale e 1000 sane in posiioni casuali)

### Prova da eseguire
- Meno cellule nella simulazione con la stessa funzione di reward
- Meno cellule nella simulazione modificando o cambiando la funzione di reward
- Cambiamento della funzione di reward

### In corso
In ccontroller.cpp, quando viene eseguito il costruttore della classe controller, vengono chiamate grid_creation() e fill_grid(). Siccome voglio creare una griglia iniziale composta da una sola cellula al centro e 1000 cellule sane in posizioni casunullptrali (come accade nella simulazione 2D), devo eliminare l'uso di grid_creaztion() e modificare l'uso di fill_gird().

Operazioni eseguite:
- Insetita una condizione per la chiamata di grid_creation(). La funzione viene chiamata solo se random_grid è false
- se random_grid è true, noFilledGrid rimane nullptr
- Modificato la funzione fill_grid(): Se noFilledGrid non è nullptr viene riempita la griglia in base alla forma di noFilledGrid. Se noFilledGrid è nullptr, aggiunge una cellula cancerosa al centro e cellulle sane casualmente nella grilgia.

VERIFICA SE DURANTE IL TRAINING VENIVA EFFETTIVAMENTE CREATA UNA NUOVA GRIGLIA DIVERSA DALLA PRECEDENTE
IL SEED FUNZIONA SOLO ALL'INTERNO DI RUN_TRAINING. PER VERIFICARE CHE EFFETTIVAMENTE LA GRGLIA VENGA IN BASE AL SEED, ESEGUI DEI TRAINING CON 1 SOLO EPISODIO SALVANDO I DATI DELLA GRIGLIA INIZIALE E VERICANDO CHE LA GRIGLIA SIA LA STESSA PER LO STESSO SEED
