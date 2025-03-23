# Radiazione cellule.
Ogni cellula possiede una determinata probabilità di sopravvivenza alla radiazione. Questa cambia se la cellula è sana o cancerosa. 

In entrambi i casi, l probabilità di sopravvivenza della cellula dopo l'irradiazione è calcolata utilizzando un modello LQ (Linear-Quadratic) modificato.

## Healthy Cells
$$
P_{sopravvivenza} = \exp\Big( \gamma \cdot \Big(-\alpha \cdot d - \beta \cdot d^2\Big) \Big)
$$

Dove:
- **$d$** è la dose di radiazione (in grays).
- **$\alpha$** corrisponde al parametro `alpha_norm_tissue` nel codice.
- **$\beta$** corrisponde al parametro `beta_norm_tissue`nel codice.
- **$\gamma$** è un fattore di modifica che dipende dallo **stadio** della cellula:
  - Se lo stadio è `'2'` o `'m'`$\gamma = 1.$
  - Se lo stadio è `'1'` (o in caso di default): $\gamma = 1$
  - Se lo stadio è `'q'` o `'s'`$\gamma = 0.$

## Cancer Cells

$$
P_{sopravvivenza} = \exp\Big( \gamma \cdot \big(-\alpha_{tumor} \cdot d - \beta_{tumor} \cdot d^2\big) \Big)
$$

Dove:
- **$d$** è la dose di radiazione (in grays).
- **$\alpha_{tumor}$** rappresenta il parametro `alpha_tumor`.
- **$\beta_{tumor}$** rappresenta il parametro `beta_tumor`.
- **$\gamma$** è un fattore modificatore che dipende dallo **stadio** della cellula:
  - Se lo stadio è `'2'` o `'m'`: $\gamma = 1.25$
  - Se lo stadio è `'1'` oppure si verifica il caso predefinito: $\gamma = 1.0$
  - Se lo stadio è$

## Parametri utilizzati:
- `alpha_tumor = 0.3` (Powathil)
- `beta_tumor = 0.03` (Powathil)
- `alpha_norm_tissue = 0.15`
- `beta_norm_tissue = 0.03`

