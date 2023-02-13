---
marp: true
backgroundColor: white
theme: default

style: |
  .columns {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 1rem;
  }
  div{
    height: 100%;
  }
  h1{
    font-size: 52px
  }
  *{
    font-size: 34px;
  }

---
# Extracción de entidades con Rasa
### Miguel Edo Goterris

---
<div>

# :train: TramTime 


<!-- This is a presenter note for this page. -->

- Quiero ir desde la estación de <span style="color:crimson;">Benimaclet</span> a la de <span style="color:crimson;">Universidad Politécnica</span>. 
- De <span style="color:crimson;">La carrasca</span> a <span style="color:crimson;">Tossal del rei</span>

<br>

```
Benimaclet -> Universitat Politècnica:
Linea: 6     Hora: 05:55:00     Destino: Marítim
Linea: 4     Hora: 06:05:00     Destino: Dr. Lluch
Linea: 4     Hora: 06:25:00     Destino: Dr. Lluch
Linea: 6     Hora: 06:28:00     Destino: Marítim
```

</div>

----
<div>

# :warning: Problema: extracción de entidades
- Dado un mensaje, extraer la **información relevante**.

- Fundamental para crear chatbots que usen **lenguaje natural**.
- Dependiendo de como se elaboren los mensajes puede ser **complicado**.
</div>

---
# Entidades y roles

<div class="columns">
<div>

Dos tipos de datos distintos.

```yaml
entities:
    - departure_station
    - destination_station

```
</div>
<div>

Un tipo de datos, dos funciones.

```yaml
entities:
   - station:
       roles:
       - departure
       - destination

```

</div>

</div>

---

# Expresiones regulares y look up tables

<div class="columns" >

<div>

```yaml
- regex: account_number
  examples: |
    - \d{10,12}
```

Formatos fijos:

- DNI
- Matrículas 
- Códigos postales

</div>

<div> 

```yaml
- lookup: station
  examples: |
    - À Punt
    - Aeroport
    - ...
    - Vicente Zaragozá
    - Xàtiva
```

</div>

</div>

---

# Expresiones regulares y look up tables

<div> 

> Rather than directly returning matches, these lookup tables work by marking tokens in the training data to indicate whether they’ve been matched. This provides an extra set of features to the conditional random field entity extractor ( ner_crf ) This lets you <u>**identify entities that haven’t been seen in the training data**</u> and also eliminates the need for any post-processing of the results.

</div>

---

# Sinónimos

<div class='columns'> 

<div>

```yaml
- synonym: Universitat Politécnica
  examples: |
    - El poli
    - La UPV
    - La politécnica
    - Politécnica

```

</div><div>

- Distintas formas de referirse a una misma entidad.
- Rasa asignará `Universitat Politécnica` si extrae cualquiera de las entidades de ejemplo.
- :train: TramTime no usa.

</div>

</div>

---

# Intents

<div>

Quiero ir desde <span style="color:crimson;">Benimaclet</span> a la <span style="color:crimson;">Universitat Politécnica</span>.

```yaml
Quiero ir desde [Benimaclet]
{"entity": "o_station", "value": "benimaclet"}
hasta [Universitat politécnica]
{"entity": "d_station", "value": "Universitat politécnica"}
```

Quiero ir de <span style="color:crimson;">beni</span> al <span style="color:crimson;">poli</span>.

```yaml
Quiero ir de [beni]
{"entity": "o_station", "value": "benimaclet"} 
al [poli]
{"entity": "d_station", "value": "Universitat politécnica"}
```

</div>

---

# Intents

<div>

Quiero ir de <span style="color:crimson;">beni</span> al <span style="color:crimson;">poli</span>.

```yaml
Quiero ir desde
[Benimaclet]{"entity": "station", "role": "departure"}
hasta
[La politecnica]{"entity": "station", "role": "destination"}
```

- Origen: `beni`
- Destino: `poli`

</div>

---

<div>

# Más intents

Generar intents automaticamente no es una mala idea.

```python
import random
frase = "- Voy de {origen} a {destino}"
estaciones = [...]
origen, destino = random.sample(estaciones, 2)
origen = f'[{origen}]{{"entity": "station", "role": "departure"}}'
destino = f'[{destino}]{{"entity": "station", "role": "destination"}}' 
frase.format(origen=origen, destino=destino)
```

</div>

---
# Pipeline

<div class='columns'>
<div>

```
pipeline:
  - name: SpacyNLP
    model: es_core_news_sm
  - name: SpacyTokenizer
  - name: SpacyFeaturizer
    pooling: mean
  - name: LexicalSyntacticFeaturizer
  - name: CountVectorsFeaturizer
    analyzer: char_wb
    min_ngram: 1
    max_ngram: 4
  - name: DIETClassifier
    epochs: 100
  - name: SpacyEntityExtractor
```

</div>
<div>

1. Tokenizado
2. Embedings preentrenados.
3. Extracción de características léxicas y sintácticas.
4. Dual Intent and Entity Transformer. Usa embedings.
5. BILOU con modelos preentrenados.


</div>

</div>

---

<div>

# Postprocesado
Las entidades extraidas se deben convertir en IDs para acceder a la API.
- Sinonimos.
- Distancia de Damerau-Levenshtein.

</div>

---

<div>

# Ejemplos

- me gustaria ir de <span style="color:crimson;">trinitat</span> hasta la estación de <span style="color:crimson;">valencia sud</span> :white_check_mark:
- de <span style="color:crimson;">trinitat</span> a <span style="color:crimson;">pont de fusta</span> :white_check_mark:
- anire de <span style="color:crimson;">beniferro</span> a <span style="color:crimson;">beninanet</span> :white_check_mark:
- ire de <span style="color:crimson;">beni</span> a la <span style="color:crimson;">politecnica</span> :question:
- quiero llegar a <span style="color:crimson;">betera</span> saliendo de <span style="color:crimson;">betero</span> :question:

La calidad del bot depende de nuestro conocimiento. Almacenando las consultas y mejorando el bot en base a estas se puede conseguir una muy buena extracción de entidades.

</div>