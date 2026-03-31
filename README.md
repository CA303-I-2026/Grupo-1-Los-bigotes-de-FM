# Proyecto CA303 — Análisis estadístico de las contraseñas de RockYou 2009

## Integrantes del grupo

|     Nombre completo     | Carné  |      Correo institucional       |
|-------------------------|--------|---------------------------------|
| Anthonny Flores Rojas   | C32975 | anthonny.flores@ucr.ac.cr       |
| Andrey Gonzalez Bastos  |        | andrey.gonzalezbastos@ucr.ac.cr |
| Leonardo Vega Aragon    |        | leonardo.vegaaragon@ucr.ac.cr   |
| Randall Picado Bermudez |        | randal.picadobermudez@ucr.ac.cr |

## Descripción del proyecto

<!-- Describa brevemente el tema, la pregunta de investigación y el objetivo general del proyecto. --

## Estructura del repositorio

```
proyecto-ca303/
+-- README.md
+-- .gitignore
+-- datos/
|   +-- originales/        # datos crudos, NUNCA se modifican
|   +-- procesados/        # datos limpios listos para análisis
+-- codigo/
|   +-- 01_limpieza.R
|   +-- 02_descriptivo.R
|   +-- 03_modelacion.R
|   +-- funciones/         # funciones auxiliares reutilizables
+-- bitacoras/
|   +-- bitacora_1/
|   |   +-- bitacora_1.tex
|   |   +-- figuras/
|   +-- bitacora_2/
|   +-- bitacora_3/
|   +-- bitacora_4/
+-- fichas/
|   +-- literatura/        # fichas bibliográficas (.md o .tex)
|   +-- resultados/        # fichas de hallazgos (.md o .tex)
+-- referencias/
|   +-- referencias.bib    # archivo BibTeX centralizado
+-- anteproyecto/
|   +-- anteproyecto.tex
+-- proyecto_final/
|   +-- proyecto.tex
|   +-- figuras/
+-- presentacion/
    +-- presentacion.tex
```

## Fuente de datos

- Nombre del conjunto de datos: RockYou 2009.
- Institución que los publica: RockYou Inc. (filtración no oficial)
- URL de descarga: https://github.com/RykerWilder/rockyou.txt
- Fecha de acceso: 2026
- Licencia de uso: Sin licencia oficial. Los datos provienen de una filtración de seguridad ocurrida en diciembre de 2009, donde aproximadamente 32 millones de contraseñas de usuarios fueron expuestas. Su uso es estrictamente académico e investigativo.

## Instrucciones de reproducibilidad

Pasos de limpieza de datos (C++):

Version de copilador de C++: GCC 15.1.0.

Version de c++ soportada: C++23 y soporte experimental para C++26.

Librerias requeridas:

- iostream
- vector
- string
- fstream
- sstream
- cctype
- conteos.h
- entropias.h
- unordered_map
- unordered_set
- chrono
- thread


ADVERTENCIA: TENGA CUIDADO A LA HORA DE EJECUTAR EL PROGRAMA (SON 14 MILLONES DE DATOS), EL CORRER EL CALCULO DE LAS ENTROPIAS PUEDE SATURAR LA RAM Y EL PROCESADOR (C++ TIENE ACCESO A TODA LA MEMORIA DEL SISTEMA), SE RECOMIENDA POR LO MENOS 12 GB DE RAM Y UN PROCESADOR DE 6 NUCLEOS. Para la ejecucion de cualquier otra funcion no hay problemas de ram ni de poder computacional.

Para la ejecucion del programa (si solo incluye los scrips y no el json) tiene que hacer un nuevo json donde indique que 01_limpieza.ccp se ejecuta con entropias.h y conteos.h como librerias sino, incluirlos en la ejecucion de la terminal de GCC (Ej: g++ 01_limpieza.cpp entropias.cpp conteos.cpp -o limpieza.exe).

NO ES UN .EXE CON MENU. Tiene que elegir las funciones que va a ejecutar antes de copilar el .cpp (No se incluye un menu por razones practicas).

<!-- Describa los pasos necesarios para reproducir los resultados: versión de R/Python, paquetes requeridos, orden de ejecución de los scripts, etc. --

## Avance y bitácoras

|  Bitácora  | Período | Temas abordados | Estado |
|------------|---------|-----------------|--------|
| Bitácora 1 |         |                 |        |
| Bitácora 2 |         |                 |        |
| Bitácora 3 |         |                 |        |
| Bitácora 4 |         |                 |        |

## Referencias principales

<!-- Liste aquí las referencias más importantes del proyecto (formato APA o BibTeX). El archivo completo se encuentra en `referencias/referencias.bib`. --
