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