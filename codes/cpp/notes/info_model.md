# INFO PARAMETRI CELLULE O'NEIL:
Informazioni, riguardanti seguenti parametri, nel paper O'Neil.

- `critical_neighbors = 9`
- Valori di assorbimento di glucosio

## Critical Neighbors
Basandosi sulla struttura a griglia di NetLogo, il numero di vicini consentiti per una cella è stato fissato a otto. Pertanto, se una cella è circondata da otto o più celle nel suo vicinato, la densità era troppo alta per consentire la sintesi. Questo si basa su un **modello sviluppato da Richard, Kirkby, Webb e Kirkby**. Poiché i modelli sviluppati in questo contesto permettevano la possibilità che più di una cella occupasse la stessa patch, è stato necessario tenere conto delle celle situate sulla stessa patch, e non solo di quelle sui patch adiacenti. Di conseguenza, il valore effettivamente utilizzato è stato nove, ovvero otto vicini più la cella stessa.

## Valori di assorbimento di glucosio

Il tasso medio di assorbimento del glucosio per cellula per ora è stato stimato in base al lavoro di Faraday, Hayter e Kirkby [7]. Il coefficiente di assorbimento del glucosio è stato valutato a: $ 3.6 \times 10^{-8} \text{ ml/cellula/ora} $

per una concentrazione di glucosio pari a 0.1 mg/ml. Di conseguenza, l'assorbimento medio di glucosio è stato fissato a:

$$ 3.6 \times 10^{-9} \text{ mg/cellula/ora} $$

In particolare:

1. **Costante di velocità per il consumo di glucosio**  
$$3.6 \times 10^{-8} \text{ ml/cellula/ora}$$
- **ml (millilitri)**: unità di volume.  
- **cellula**: indica che il valore è riferito a una singola cellula.  
- **ora**: unità di tempo.  
- **Interpretazione**: indica il volume di glucosio consumato da una singola cellula in un'ora.

2. **Concentrazione di glucosio**  
$$0.1 \text{ mg/ml}$$
- **mg (milligrammi)**: unità di massa.  
- **ml (millilitri)**: unità di volume.  
- **Interpretazione**: indica la quantità di glucosio (in mg) presente in ogni millilitro di soluzione.

3. **Assorbimento medio di glucosio** 
Si ottiene moltiplicando la costante di velocità per la concentrazione di glucosio.
$$3.6 \times 10^{-9} \text{ mg/cellula/ora}$$
- **mg (milligrammi)**: quantità di glucosio assorbita.  
- **cellula**: il valore è riferito a una singola cellula.  
- **ora**: unità di tempo.  
- **Interpretazione**: indica la massa di glucosio assorbita da una cellula in un'ora.



### Efficienza e Assorbimento Massimo
Per introdurre una variazione tra le cellule, è stato definito un parametro **efficienza** che rappresenta la quantità di glucosio assorbito per ora da una singola cellula. Per le cellule sane, l'efficienza è stata assegnata con una distribuzione normale con:

- Valore medio: $ 3.6 \times 10^{-9} \text{ mg/cellula/ora} $
- Deviazione standard: $ 1.2 \times 10^{-9} \text{ mg/cellula/ora} $

Per limitare l'assorbimento massimo, il valore massimo di efficienza è stato imposto come il doppio del valore massimo.

Le cellule tumorali, notoriamente più aggressive nell'assorbimento di nutrienti, sono state assegnate con un'efficienza superiore.

### Requisiti per la Transizione nel Ciclo Cellulare
Il glucosio necessario per la transizione dalla fase Gap1 alla fase S (sintesi del DNA) è stato calcolato moltiplicando l'assorbimento medio di glucosio per il tempo medio che una cellula prolifera trascorre in Gap1:

$$ 3.6 \times 10^{-9} \text{ mg/cellula/ora} \times 11 \text{ ore} = 3.96 \times 10^{-8} \text{ mg/cellula} $$

Anche in questo caso, il valore è stato distribuito normalmente con:

- Valore medio: $$ 3.96 \times 10^{-8} \text{ mg/cellula} $$
- Deviazione standard: $$ 1.32 \times 10^{-8} \text{ mg/cellula} $$


### Livello di Glucosio per la Quiescenza
Il livello di glucosio che segna la transizione in fase quiescente (G0) è stato stimato considerando il glucosio necessario per due cicli cellulari completi, dato che una cellula divisione ne produce due:

$$ 3.6 \times 10^{-9} \text{ mg/cellula/ora} \times 24 \text{ ore} \times 2 = 1.728 \times 10^{-7} \text{ mg/cellula} $$

### Livello Critico di Glucosio
Il livello critico di glucosio, sotto il quale la cellula non può sopravvivere, è stato fissato al 75% del glucosio necessario per un intero ciclo cellulare:

$$ \frac{3.6 \times 10^{-9} \text{ mg/cellula/ora} \times 24 \text{ ore} \times 3}{4} = 6.48 \times 10^{-8} \text{ mg/cellula} $$
