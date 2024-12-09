# Problema della creazione della griglia tumorale

Il problema risiede nel fatto che il numero di cellule sane e cancerose ottenute varia in base al voxel. Questo accade quando il codice sopra viene spostato nel file *controller.py* o in *grid.py*. In teoria, non dovrebbe cambiare nulla, poiché il codice è identico e l'unica differenza è il file in cui è inserito.

Chiamiamo **caso 1** il riempimento della griglia in *controller.py* e **caso 2** il riempimento della griglia in *grid.py*. A seconda del caso, si ottiene un numero diverso di cellule dopo aver applicato funzioni come `go()` o `irradiate()`.

Un aspetto importante è che, quando il codice si trova in *controller.py*, la griglia viene chiamata con `self.grid.cells[]`, mentre in *grid.py* viene chiamata con `self.cells[]`.

### Descrizione

La creazione del tumore avviene nel file *main.py*, mentre la griglia che conterrà le cellule sane e tumorali viene creata all'interno di `grid.py` (ogni elemento della griglia diventa un oggetto `CellList()`). Il problema si presenta nel momento in cui le cellule vengono aggiunte alla griglia precedentemente creata. Con il codice seguente, la griglia 3D viene "riempita" con un numero preimpostato di cellule.

```python
# Creo la griglia del tumore
for k in range(self.zsize):
    for i in range(self.xsize):
        for j in range(self.ysize):
            # Aggiungo le cellule sane
            if real_tumor_grid[k, i, j] == 1:
                for _ in range(self.num_hcells):
                    new_cell = HealthyCell(random.randint(0, 4))
                    self.cells[k, i, j].append(new_cell)
            # Aggiungo le cellule tumorali
            elif real_tumor_grid[k, i, j] == -1:
                for _ in range(self.num_ccells):
                    new_cell = CancerCell(random.randint(0, 3))
                    self.cells[k, i, j].append(new_cell)
```

Qui, `real_tumor_grid` è la griglia del tumore "reale" creata nel file *main.py*, in cui ogni elemento contiene un valore `-1` o `1` a seconda che il voxel contenga cellule tumorali o sane, rispettivamente.

### Riassunto del problema

Si osserva un diverso numero di cellule sane e tumorali nei voxel nei due casi:

- **Caso 1**: Riempimento della griglia in *controller.py*
- **Caso 2**: Riempimento della griglia in *grid.py*

### Test effettuati

Come prima cosa ho contato il numero di cellule sane e cancerose subito dopo la creazione della griglia in entrambi i casi. Il numero era lo stesso.

Le successive verifiche sono state effettuate con la funzione *irradiate()* in *grid.py*, ed in particolare con le seguenti righe di codice nel caso 1 e 2.

```python
multiplicator = get_multiplicator(dose, radius)
oer_m = 3.0
k_m = 3.0

for k in range(self.zsize):
    for i in range(self.xsize):
        for j in range(self.ysize):
            dist = math.sqrt((z - k) ** 2 + (x - i) ** 2 + (y - j) ** 2)
            if dist < 3 * radius:
                omf = (self.oxygen[k, i, j] / 100.0 * oer_m + k_m) / (self.oxygen[k, i, j] / 100.0 + k_m) / oer_m
                for cell in self.cells[k, i, j]:
                    cell.radiate(scale(radius, dist, multiplicator) * omf)
                count = len(self.cells[k, i, j])
                self.cells[k, i, j].delete_dead()
                if len(self.cells[k, i, j]) < count:
                    self.add_neigh_count(k, i, j, len(self.cells[k, i, j]) - count)
```

I valori di *multiplicator*, *omf* e (*scale(radius, dist, multiplicator) x omf*) erano i medesimi per ogni caso.

Successivamente ho controllato il numero di cellule sane e il numero di cellule cancerose all'interno di ciascun voxel senza irradiazione (*cell.radiate()*) e lasciando la funzione *self.cells[k, i, j].delete\_dead()*. Anche in questo caso il numero rimaneva lo stesso.

Come ultima prova, ho ricontrollato il numero di cellule considerando anche la funzione *cell.radiate()*. In questo caso, dopo aver irradiato, il numero differiva tra il caso 1 e il caso 2.

Per ciascuna di queste prove, se il calcolo veniva ripetuto mantenendo inalterato il codice, cioè se il programma veniva eseguito più volte nello stesso caso (1 o 2), il risultato non cambiava. Questo esclude possibili variazioni tra un'esecuzione e l'altra mantenendo inalterato il codice (stesso caso).

### Conclusioni

Il problema sta all'interno della funzione *cell.radiate()*. Ricordo che *cell.radiate()* calcola la probabilità di sopravvivenza per ogni cellula all'interno di ogni voxel. Secondo me, il problema potrebbe essere legato a una possibile diversa gestione della funzione *random* nei due diversi casi. Siccome la funzione random controlla la morte o la sopravvivenza di una cellula, è possibile che, a causa di una gestione differente tra il caso 1 e il caso 2, vengano eliminate più o meno cellule, causando il problema del diverso numero di cellule tra i due casi.

