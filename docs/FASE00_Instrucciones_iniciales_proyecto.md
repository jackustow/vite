# Software en Python para validar información de terceros para medios magnéticos en Colombia

## Objetivo
Construir una aplicación Python para realizar la validación de los terceros que se deberán reportar en los formatos de medios magnéticos que se deben reportar a la DIAN en Colombia. 

## Extracción de datos

Lo primero que se le debe solicitar al usuario es seleccionar, de una lista desplegable, la compañía a la que pertenecen los datos que se han de validar. Cada empresa estará
identificada en una tabla de la base de datos con un ID y con su nombre (tabla "cfg_empresa"). Este ID servirá para identificar todo el proceso de validación que se llevará a cabo. La tabla 
de la empresa debe tener un campo entero identity y con el cual se identificarán todos los registos asociados a dicho proceso.

** Tabla "cfg_empresa" **
| ** empresa_id ** | ** empresa_desc ** |
|------------------|--------------------|
| 1                | INSUGEC            |

El siguiente campo de información que debe diligenciar el usuario es el año al que pertenece la información a procesar. Se deberá seleccionar de una lista de despliegue y si no
existe, el usuario deberá contar con un botón de creación, en el cual debará dilgenciar el año al que pertenecen los datos. Al igual que el campo anterior, el año servirá para 
identificar todo el proceso de validación que se llevará a cabo. Esta información se deberá almacenar en la tabla "cfg_periodo".

** Tabla "cfg_periodo" **
| ** periodo_id ** |
|------------------|
| 2024             |
| 2025             |
| 2026             |

Luego de diligenciada l ainformacion de la empresa y el año, el usuario deberá seleccionar la ruta de la carpeta donde se encuentran todos los archivos de medios que se desean validar. Una vez 
diligenciada la carpeta, se le debe mostrar los archivos de excel (.xls y .xlsx) presentes en la carpeta. El usuario debe seleccionar aquellos que desea procesar 
(botones tipo check en cada documento de excel presentado).

El nombre de los archivos posee el número del formato al que pertenece la información. Un ejemplo de nombre de archivo es: "Formato 1001 DEFINITIVO.xlsx", lo cual indica que
el formato al que pertenecen los datos es el 1001. Si hay algún nombre que no posea el número de formato, deberá presentarse un modal de error al usuario cuando este intente
iniciar el proceso de validación, para que lo corrija. Para que la aplicación refleje los cambios, el formulario deberá contener un botón "refrescar" para leer de nuevo la inforamción
de la carpeta.

El usuario deberá hacer clic en el botón "Iniciar proceso". Una vez el usuario decide iniciar el proceso luego de seleccionar los archivos, los datos se deben extraer, 
sanitizar y luego almacenarlos en una base de datos de posgresql para luego iniciar el proceso de Transformación.

Se debe priorizar la importación de datos considerando aquellos formatos que cuenten con mayor cantidad de campos a procesar que otros. Para ello, haremos uso de la tabla 
"cfg_prioridad_importacion" la cual posee la siguiente estructura: 

** Tabla "cfg_prioridad_importacion" **
| formato_id | prioridad |
|------------|-----------|
| 1008       | 1         | 
| 2276       | 2         |
| 1003       | 3         | 
| 1001       | 4         | 
| 1004       | 5         | 
| 1005       | 6         | 
| 1006       | 7         | 
| 1007       | 8         | 

La información de los campos que se deben extraer de los documentos de excel seleccionados son los siguientes:

- Tipo de documento
- Número de identificación
- Dígito de Verificación
- Primer apellido del informado
- Segundo apellido del informado
- Primer nombre del informado
- Otros nombres del informado
- Razón social del informado
- Dirección
- Código del departamento
- Código del municipio
- Código del país

Es muy seguro que los nombres de los campos varíen según cada empresa configurada; para personalizar los nombres por cada empresa, vamos a usar esta estrateiga:
Crear una tabla de campos base (tabla "cfg_campos_terceros") con la cual la aplicación gestionará todas las validaciones y una segunda tabla para personalizar 
cada campo según la empresa (tabla "cfg_campos_terceros_empresas"), la cual será usada para el proceso de extracción (usando el campo "empresa_campo"). 
La estructura de las tablas es la siguiente:

** Tabla "cfg_campos_terceros" **	
| ** campo_id ** | ** campo_desc **                |
|----------------|---------------------------------|
| TPDOC          | Tipo de documento               |
| NMDOC          | Número de identificación        |
| DV             | Dígito de Verificación          |
| AP1            | Primer apellido del informado   |
| AP2            | Segundo apellido del informado  |
| NM1            | Primer nombre del informado     |
| NM2            | Otros nombres del informado     |
| RZ             | Razón social del informado      |
| DIR            | Dirección                       |
| DPTO           | Código del departamento         |
| MPIO           | Código del municipio            |
| PAIS           | Código del país                 |

** Tabla "cfg_campos_terceros_empresas" **
| ** campo_id ** | ** empresa_id ** | ** empresa_campo **             |
|----------------|------------------|---------------------------------|
| TPDOC          | 1                | Tipo de documento               |
| NMDOC          | 1                | Número de identificación        |
| DV             | 1                | Dígito de Verificación          |
| AP1            | 1                | Primer apellido del informado   |
| AP2            | 1                | Segundo apellido del informado  |
| NM1            | 1                | Primer nombre del informado     |
| NM2            | 1                | Otros nombres del informado     |
| RZ             | 1                | Razón social del informado      |
| DIR            | 1                | Dirección                       |
| DPTO           | 1                | Código del departamento         |
| MPIO           | 1                | Código del municipio            |
| PAIS           | 1                | Código del país                 |

Ahora bien, no todos los formatos cuentan con todos los campos, pues no todos aplican (según el formato). Para saber qué campos debemos validar y cuales no, hay que crear la
tabla "cfg_campos_requeridos". A continuación comparto los datos y la estructura de la tabla que indica los campos que aplican y que no aplican para cada formato:

** Tabla "cfg_campos_requeridos" **
| **campo_id** | **Formato_1001** | **Formato_1003** | **Formato_1004** | **Formato_1005** | **Formato_1006** | **Formato_1007** | **Formato_1008** | **Formato_2276** |
|--------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|------------------|
| TPDOC        | Aplica           | Aplica           | Aplica           | Aplica           | Aplica           | Aplica           | Aplica           | Aplica           |
| NMDOC        | Aplica           | Aplica           | Aplica           | Aplica           | Aplica           | Aplica           | Aplica           | Aplica           |
| DV           | No aplica        | Aplica           | No aplica        | Aplica           | Aplica           | No aplica        | Aplica           | No aplica        |
| AP1          | Aplica           | Aplica           | Aplica           | Aplica           | Aplica           | Aplica           | Aplica           | Aplica           |
| AP2          | Aplica           | Aplica           | Aplica           | Aplica           | Aplica           | Aplica           | Aplica           | Aplica           |
| NM1          | Aplica           | Aplica           | Aplica           | Aplica           | Aplica           | Aplica           | Aplica           | Aplica           |
| NM2          | Aplica           | Aplica           | Aplica           | Aplica           | Aplica           | Aplica           | Aplica           | Aplica           |
| RZ           | Aplica           | Aplica           | Aplica           | Aplica           | Aplica           | Aplica           | Aplica           | No aplica        |
| DIR          | Aplica           | Aplica           | Aplica           | No aplica        | No aplica        | No aplica        | Aplica           | Aplica           |
| DPTO         | Aplica           | Aplica           | Aplica           | No aplica        | No aplica        | No aplica        | Aplica           | Aplica           |
| MPIO         | Aplica           | Aplica           | Aplica           | No aplica        | No aplica        | No aplica        | Aplica           | Aplica           |
| PAIS         | Aplica           | No aplica        | Aplica           | No aplica        | No aplica        | Aplica           | Aplica           | Aplica           |

IMPORTANTE: Para esta fase de extracción, la definición de "Aplican" o "No aplican" se refiere a que los campos deben estar presente en el formato en cuestion. La validación de los registros en cada campo
se tratará con mas detalle en la fase de "Tranformación"

Al momento de extraer los datos de los campos, puede ocurrir que alguno de los formatos no posea el nombre de columna tal y como se definió en la tabla "cfg_campos_terceros_empresas". 
En caso de que esto ocurra se debe generar un mensaje de error informando qué campo no se encontró en el formato [número del formato] y se debe abortar todo el proceso. 
No se debe importar ningún formato hasta tanto todos los campos estén debidamente configurados para cada uno de los formatos según la empresa.

El almacenamiento de los registros importados deberá almacenarse en la tabla "mov_terceros_importados", la cual deberá tener la siguiente estructura:

** mov_terceros_importados **
| ** empresa_id ** | ** periodo_id** | ** empresa_id ** | ** timestamp **     | ** TPDOC ** | ** NMDOC ** | ** DV ** | ** AP1 ** | ** AP2 ** | ** NM1 ** | ** NM2 ** | ** RZ ** | ** DIR **            | ** DPTO ** | ** MPIO ** | ** PAIS ** |
|------------------|-----------------|------------------|---------------------|-------------|-------------|----------|-----------|-----------|-----------|-----------|----------|----------------------|------------|------------|------------|
| 1                | 2026            | 1                | 2026-05-18 15:06:35 | 13          | 311705      |          | URBANO    |           | ALDANA    | CASTAÑEDA |          | TV 3 10 59           | 19         | 397        | 169        |
| 1                | 2026            | 1                | 2026-05-18 15:06:35 | 31          | 1764379     | 8        | FERNANDEZ | DAZA      | EFRAIN    | DARIO     |          | DIAGONAL 21 N 31-50  | 20         | 001        | 169        |
| 1                | 2026            | 1                | 2026-05-18 15:06:35 | 13          | 2737906     |          | HERNANDO  |           | NIETO     | LEON      |          | CRA 16 # 23 - 26     | 20         | 013        |            |
| 1                | 2026            | 1                | 2026-05-18 15:06:35 | 13          | 3469827     |          | JARAMILLO | PALACIO   | JUAN      | CARLOS    |          | avenida 38 - 28 - 77 | 13         | 683        | 169        |

Un mismo tercero puede estar presente en múltiples formatos, por lo cual se deberá almacenar la asociación entre terceros y formatos en la tabla "mov_terceros_importados_formato"

** mov_terceros_importados_formato **
| ** empresa_id ** | ** periodo_id** | ** empresa_id ** | ** NMDOC ** | ** formato ** |
|------------------|-----------------|------------------|-------------|---------------|
| 1                | 2026            | 1                | 311705      | 1001          |
| 1                | 2026            | 1                | 311705      | 1003          |
| 1                | 2026            | 1                | 1764379     | 1001          |
| 1                | 2026            | 1                | 1764379     | 1003          |
| 1                | 2026            | 1                | 2737906     | 1001          |
| 1                | 2026            | 1                | 3469827     | 1001          |

IMPORTANTE: Para la importación se deben tener en cuenta las siguientes condiciones: 
- En la tabla "mov_terceros_importados" no se pueden cargar registros duplicados. Las llaves que se deben respetar son: empresa_id, periodo_id, empresa_id, NMDOC
- En la tabla "mov_terceros_importados_formato" no se pueden cargar registros duplicados. Las llaves que se deben respetar son: empresa_id, periodo_id, empresa_id, NMDOC, formato
- En la tabla "mov_terceros_importados" los valores vacios se deben importar como NULL en la base de datos. Esto es importante porque con base en este tipo de datos se aplicarán reglas de validaciones y actualización de datos en la fase de "Transformación"


## Tranformación de datos

El avance del proceso se deberá informar por medio de un modal de tipo loading y que vaya mostrando en pantalla la fase en la que se encuentra.

La aplicación deberá realizar los siguientes tipos de acciones sobre los registros de los terceros, a saber:
- (ACTINF) Actualización de información: Se especificarán algunas herramientas o reglas que la herramienta deberá usar para poder completar o corregir la información del tercero. Los registros a los que se les apliquen este tipo de cambios se deben identificar a modo de "Alerta"
- (VALRES) Validaciones restrictivas: Son aquellas reglas que los terceros deberán cumplir. Las reglas pueden aplicar para todos los formatos (reglas globales) o para formatos específicos (reglas específicas). El incumplimiento de estas reglas se deben identificar a modo de "Error"
- (INFOOK) Información correcta: Son los casos en los que los registros de los terceros están debidamente diligenciados, superan las validaciones restrictivas y no es necesario complemntar su información. Los registros con estas características se deben identificar a modo de "Info"

IMPORTANTE: Primero se deberá validar la información y luego actualizarla. El log del registro de estas accines deben quedar almacenado con el tipo (ACTINF)

### Actualización de información

Lo primero que se debe hacer con la información es completar y/o actualizar la información. Para ello se debe realizar las siguientes acciones:

** 1. Actualización del campo TPDOC **
El código del tipo del documento debe corresponder al número del documento según las siguientes condiciones:

- El valor es 13 si la longitud del campo "NMDOC" es menor a 9
- El valor es 31 si la longitud del campo "NMDOC" es igual a 9
- El valor es 13 si la longitud del campo "NMDOC" es mayor a 9

** 2. Actualización del campo DV **
El digito de verificación se debe calcular solamente a los terceros cuyo valor en TPDOC sea 31. El cálculo se debe realizar y almacenar según la siguiente función:

```python
def calcular_dv_colombia(nit):
    """
    Calcula el dígito de verificación (DV) para un NIT o cédula en Colombia
    utilizando el algoritmo oficial de la DIAN (Módulo 11).
    
    :param nit: int o str con el número de identificación
    :return: int con el dígito de verificación (0-9)
    """
    # Convertir a cadena y conservar únicamente los dígitos numéricos
    nit_limpio = "".join(caracter for caracter in str(nit) if caracter.isdigit())
    
    if not nit_limpio:
        raise ValueError("El NIT ingresado no contiene números válidos.")
    
    # Coeficientes primos definidos por la DIAN (ordenados de derecha a izquierda)
    coeficientes = [3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]
    
    sumatoria = 0
    
    # Recorrer el NIT al revés (de derecha a izquierda) y multiplicar por los coeficientes
    for i, digito in enumerate(reversed(nit_limpio)):
        if i >= len(coeficientes):
            break  # Resguardo en caso de que el NIT supere los 15 dígitos estándar
        sumatoria += int(digito) * coeficientes[i]
        
    # Calcular el residuo de la división por 11
    residuo = sumatoria % 11
    
    # Aplicar la regla de la DIAN para el resultado final
    if residuo > 1:
        return 11 - residuo
    else:
        return residuo
```
** 3. Actualización de direcciones **
Lo primero que se debe hacer es actualizar los valores de las direcciones a mayusculas. Esta actualización no requiere reportarse como un evento (ACTINF).

Lo segundo a tener en cuenta es que la longitud de la dirección no puede ser inferior a 8 caracteres. Si el valor de la dirección, luego de la actualización resulta 
siendo menor a 8 caracteres de lognitud, no se deberá llevar a cabo la actualzación y se debe reportar la novedad como un evento (ACTINF).

Ahora bien, las direcciones deben cumplir con una estructura basada en nomenclaturas y solamente debe contener los caracteres letras, numeros y espacios. Lo primero que se debe
hacer es reemplazar los valores de la dirección según la nomenclatura correspondiente. Para llevar a cabo dicho reemplazo, se debe usar la información de la tabla "cfg_nomenclatura".

La información y estructura de la tabla "cfg_nomenclatura" se encuentra en la carpeta "docs" del proyecto.

Como puede observar, hay valores en el campo "nomenclatura_palabras_clave" que poseen varias palabras claves separadas por comas, esto quiere decir que cualquiera de estas
coincidencias en la dirección dene ser reemplazada por el valor del campo "nomenclatura_id". Tenga en cuenta que se deben reemplazar palabras completas (que inicien y que 
terminen con espacio).

He aquí un ejemplo de una dirección original y el resultado luego de realizar el proceso de ** 3. Actualizació de direcciones **:

- Dirección original: Carrera 25 A # 38D sur - 111, Apartamento 1513, Edificio Castello
- Dirección nueva: CR 25 A 38D SUR 111 AP 1513 ED CASTELLI

** 4. Nombres, apellidos y razón social ** 

Hay casos de registros en que diligencian los nombres en los campos incorrectos, ya que esto depende del tipo de identificación del tercero. 
Para corregir estos valores, debe realizar la siguiente actualización de información: 

- Cuando el tercero es TPDOC=13 quiere decir que es persona natural, por lo cual el valor de los campos AP1 y NM1 son obligatorios y el campo RZ debe ser null. Si el campo RZ tiene valores debe separar el texto según los espacios y si hay dos resultados, debe ubicarlos en los campos AP1 y NM1. Si hay 3 resultados se deben ubicar en los campos AP1, NM1 y AP2. Si devuelve 4 registros se deben ubicar en AP1, NM1, AP2, NM2. Si hay más de 4 campos, deste la quinta columna en adelante se deben concatenar a la columna 4 e ingresar la información como si fueran 4 columas de resultado. Una vez alimentados los campos, registre en null el registro del campo RZ.
- Cuando el tercero es TPDOC=31 quiere decir que es persona jurídica. Para este campo el valor del campo RZ es obligatorio y los campos AP1, AP2, NM1 y NM2 deben ser null. En este caso lo que se debe hacer es concatenar la información de los campos AP1, AP2, NM1 y NM2 y almacenarlo en el campo RZ. Una vez alimentados los campos, registre en null el registro de los campos AP1, AP2, NM1 y NM2.

Ahora, puede suceder que aún habiendo realizado la corrección de datos de nombres, apellidos y razón social para los tipos de documentos 13 y 31, hayan registros que aún presenten inconsistencias. Para ello, vamos a completar la información consultando la información del tercero en la página [Consulta de inconsistencias DIAN](https://muisca.dian.gov.co/WebGestionmasiva/DefSelPublicacionesExterna.faces).

Este servicio es una página WEB que se deberá consultar usando Playwright. A continuación comparto el detalle que se debe automatizar para hacer uso de este servicio:

** Inicio **
Al acceder a la página se presenta el siguiente formulario:

```
|-----------------------------------------------------------|
| Fecha Actual de Consulta | 18-05-2026 17:43:49            |
|--------------------------|--------------------------------|
| NIT                      | [textbox para diligenciar NIT] |
| Dígito de Verificación   | [textbox para diligenciar DV]  |
|-----------------------------------------------------------|
|                       --------                            |
|                      | Buscar |                           |
|                       --------                            |
|-----------------------------------------------------------|
```

Playwright debe diligenciar el valor del campo "NMDOC" y calcular el digito de verificación con la función "calcular_dv_colombia" y luego hacer clic en el botón "Buscar"

** Resultados TPDOC13 (persona natural) **
Para este ejercicio he diligenciado el NMDOC=80100491 y el DV=3. En este caso la aplicación retorna un modal "AYUDA" con información y el formulario con los datos del tercero.

Formulario modal (informativo. no se debe considerar):
```
|-----------------------------------------------------------------|
| AYUDA   | Consulta documentos con inconsistencias               |
|-----------------------------------------------------------------|
| A 18-05-2026 para el nit digitado no se encontraron documentos  |
| con inconsistencias. Consulte frecuentemente esta opción.       |
|-----------------------------------------------------------------|
```

Formulario con información de tercero consultado:
```
|--------------------------------------------------------------------------|
| Fecha Actual de Consulta         | 18-05-2026 17:43:49                   |
|----------------------------------|---------------------------------------|
| NIT                              | 80100491                              |
| Dígito de Verificación           | 3                                     |
|----------------------------------|---------------------------------------|
| Primer Apellido  | CRUZ          | Segundo Apellido  | ROMERO            |
| Primer Nombre    | JAIME         | Segundo Nombre    | ANDRES            |
|----------------------------------|---------------------------------------|
|                              --------                                    |
|                             | Buscar |                                   |
|                              --------                                    |
|--------------------------------------------------------------------------|
```

Al obtener respuesta del servicio, se deben tomar los campos retornados y almacenarlos en los campos correspondientes:
- Primer Apellido 	-> AP1
- Segundo Apellido	-> AP2
- Primer Nombre		-> NM1
- Segundo Nombre	-> NM2

** Resultados TPDOC31 (persona jurídica) **
Para este ejercicio he diligenciado el NMDOC=811022981 y el DV=7. En este caso la aplicación retorna un modal "AYUDA" con información y el formulario con los datos del tercero.

Formulario modal (informativo. no se debe considerar):
```
|-----------------------------------------------------------------|
| AYUDA   | Consulta documentos con inconsistencias               |
|-----------------------------------------------------------------|
| A 18-05-2026 para el nit digitado no se encontraron documentos  |
| con inconsistencias. Consulte frecuentemente esta opción.       |
|-----------------------------------------------------------------|
```

Formulario con información de tercero consultado:
```
|--------------------------------------------------------------------------|
| Fecha Actual de Consulta         | 18-05-2026 17:43:49                   |
|----------------------------------|---------------------------------------|
| NIT                              | 811022981                             |
| Dígito de Verificación           | 7                                     |
|----------------------------------|---------------------------------------|
| Razón Social                     | SOBERANA S.A.S.                       |
|----------------------------------|---------------------------------------|
|                              --------                                    |
|                             | Buscar |                                   |
|                              --------                                    |
|--------------------------------------------------------------------------|
```
Al obtener respuesta del servicio, se deben tomar los campos retornados y almacenarlos en los campos correspondientes:
- Razón Social 	-> RZ

** Sin resultado (DV no corresponde al NIT) **
Para este ejercicio he diligenciado el NMDOC=811022981 y el DV=8 (valor errado). En este caso la aplicación retorna un modal "ERROR" con el mensaje correspondiente:

```
|-----------------------------------------------------------------|
| ERROR   | Consulta documentos con inconsistencias               |
|-----------------------------------------------------------------|
| El dígito de verificación 8 no corresponde con el NIT 811022981 |
|-----------------------------------------------------------------|
```
En este caso, se deben dejar los valores como estan para que sean procesados y alertados en el proceso "Validaciones restrictivas"

** Sin resultado (NIT no existe en la BD de la DIAN) **
Para este ejercicio he diligenciado el NMDOC=124568416 (NIT Inventado) y el DV=9. En este caso la aplicación retorna un modal "ERROR" con el mensaje correspondiente:

```
|--------------------------------------------------------|
| ERROR   | Consulta documentos con inconsistencias      |
|--------------------------------------------------------|
| El NIT 124568416 no es válido. verifique que el nit se |
| encuentre registrado en el RUT.                        |
|--------------------------------------------------------|
```
En este caso, se deben dejar los valores como estan para que sean procesados y alertados en el proceso "Validaciones restrictivas"


### Validaciones restrictivas

Las validacinoes restrictivas se definen en 2 grandes grupos jerárquicos:
- Reglas globales: Estas reglas aplican para todos los registros de todos los formatos seleccionados.
- Reglas específicas: Las reglas específicas son las que aplican para los registros de un formato específico.

IMPORTANTE: Las reglas se deben ejecutar en el orden indicado.

A continuación se detallan las regals globales y las reglas específicas que se deben incluír en este desarrollo

** Reglas globales **
1. Los campos "TPDOC" y "NMDOC" no pueden ser NULL
2. Cuando el tercero es TPDOC=13 el valor de los campos AP1 y NM1 son obligatorios y el campo RZ debe ser null. 
3. Cuando el tercero es TPDOC=31 el valor del campo RZ es obligatorio y los campos AP1, AP2, NM1 y NM2 deben ser null.

** Reglas específicas **
Las reglas específicas se deben realizar según el formato. Las validaciones específicas son las siguientes:

Las validaciones que se deben realizar son las siguientes:
- VAL_TPDOC_01: Los valores permitidos son 13 y 31.
- VAL_TPDOC_02: Si TPDOC=13 entonces AP1 y NM1 son obligatorios y RZ debe ser null. 
- VAL_TPDOC_03: Si TPDOC=31 entonces RZ es obligatorio y AP1, AP2, NM1 y NM2 deben ser null.
- VAL_DV_01: El campo DV no debe ser NULL si TPDOC=31
- VAL_DIR_01: DIR debe tener más de 8 caracteres
- VAL_PAIS_01: Los registros del campo PAIS deben coincidir con uno de los registros de la tabla "cfg_paises" campo "pais_id".
- VAL_DPTO_01: Si aplican las validaciones de los campos DPTO y PAIS entonces el valor del campo DPTO=cfg_geografia.dpto_id y PAIS=cfg_geografia.pais_id. Si solamente aplica la validacion del campo DPTO entonces el valor del campo DPTO=cfg_geografia.dpto_id y PAIS=169.
- VAL_MPIO_01: Si aplican las validaciones de los campos MPIO, DPTO y PAIS entonces el valor del campo MPIO=cfg_geografia.mpio_id y DPTO=cfg_geografia.dpto_id y PAIS=cfg_geografia.pais_id. Si solamente aplica la validacion del campo MPIO entonces el valor del campo MPIO=cfg_geografia.mpio_id y DPTO=cfg_geografia.dpto_id y PAIS=169.

NOTA: 
- Las validaciones VAL_PAIS_01, VAL_DPTO_01 y VAL_MPIO_01 se debe sustentar en la información de las tablas "cfg_paises" y "cfg_geografia". La información de estas tablas se encuentra 
presentes en la carpeta "docs".
- Se debe crear una tabla de validaciones con el nombre "cfg_validaciones" donde se almacene el código de la validación y la descripcion de la validación según lo indicado anteriormente

Ahora, las reglas se deben aplicar a determinados formatos específicos. Esta asociación de validaciones se deberá especificar en la tabla "cfg_validaciones_formatos" en la cual
se asocia el código de la validación y el código del formato al que hay que aplicar dicha validación. 

A continuación se detalla cada validación según el formato al que se le debe aplicar:

**Formato 1001**
- VAL_TPDOC_01, VAL_TPDOC_02, VAL_TPDOC_03
- VAL_DIR_01
- VAL_PAIS_01
- VAL_DPTO_01
- VAL_MPIO_01

**Formato 1003**
- VAL_TPDOC_01, VAL_TPDOC_02, VAL_TPDOC_03
- VAL_DV_01
- VAL_DIR_01
- VAL_PAIS_01
- VAL_DPTO_01
- VAL_MPIO_01

**Formato 1004**
- VAL_TPDOC_01, VAL_TPDOC_02, VAL_TPDOC_03
- VAL_DIR_01
- VAL_PAIS_01
- VAL_DPTO_01
- VAL_MPIO_01

**Formato 1005**
- VAL_DV_01
- VAL_TPDOC_01, VAL_TPDOC_02, VAL_TPDOC_03

**Formato 1006**
- VAL_DV_01
- VAL_TPDOC_01, VAL_TPDOC_02, VAL_TPDOC_03

**Formato 1007**
- VAL_TPDOC_01, VAL_TPDOC_02, VAL_TPDOC_03
- VAL_PAIS_01

**Formato 1008**
- VAL_DV_01
- VAL_TPDOC_01, VAL_TPDOC_02, VAL_TPDOC_03
- VAL_DIR_01
- VAL_PAIS_01
- VAL_DPTO_01
- VAL_MPIO_01

**Formato 2276**
- VAL_TPDOC_01, VAL_TPDOC_02
- VAL_DIR_01
- VAL_PAIS_01
- VAL_DPTO_01
- VAL_MPIO_01


### Información correcta
En caso tal que el registro cumpla con todas las validaciones y no haya sido necesario intervenirlo en el proceso de "Actualización de información" se deberá reportar como (INFOOK).


## Carga de datos
La disposición de la información se debe entregar al usuario por medio de un documento de excel con dos hojas, la primera debe contener un informe de los terceros y los ajustes o validaciones que se hayan aplicado y la segunda 
hoja debe poseer todos los terceros validados y ajustados en la estructura correspondiente. La segunda hoja solamente se deberá generar únicalmente cuando ningún tercero posea validaciones restrictivas.

El archivo deberá crearse en la carpeta que el usuario seleccionó para la lectura de los archivos con el nombre "Informe_validacion_terceros_[timestamp de creacion archivo].xlsx"


## Especificaciones técnicas
- La aplicación se llama "VITE - Validación de información de terceros exógena".
- La interacción de la aplicación debe hacerse por medio de una TUI usando la librería "Textualize" (https://www.textualize.io/).
- La arquitectura de la aplicación debe ser "Monolito modular"
- En escencia, la aplicación es de tipo "ETL". A continuación se detalla lo que debe suceder en cada una de las fases:
- La información se debe almacenar en una base de datos en Posgresql. Los datos de la conexión son:
	- host: localhost
	- database: vite
	- port: 5432
	- usuario: vite
	- clave: vite12345
- Use CONDA para el entorno virtual de Python. El nombre del entorno que deberá crear debe ser "vite". Use la última versión estable de Python.
- Crea un archivo README.md con la inforamción del proyecto, el objetivo, la guia del usuario y la guia de instalación


