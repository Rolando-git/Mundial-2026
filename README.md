# Mundial-2026
## Explicacion del Codigo

A continuacion se detalla el propósito de cada funcion principal del simulador:

### `poisson_random(lambda_val)`
Genera un numero entero de goles utilizando la distribucion de Poisson, con el objetivo de modelar la cantidad de goles en un partido.

### `simulate_match(a, b, goals_dict=None)`
Simula un partido entre dos equipos y devuelve los goles de cada uno. Puede acumular estadisticas de goles totales.

### `simulate_group(group, goals_dict=None)`
Simula la fase de grupos completa (todos contra todos), calcula puntos, diferencia de goles y ordena la tabla segun las reglas oficiales.

### `simulate_knockout_match(a, b, goals_dict=None)`
Simula un partido de eliminacion directa. En caso de empate, resuelve con penales basados en la "fuerza" de cada equipo.

### `simulate_one_tournament(groups, goals_dict=None)`
Simula un torneo completo: fase de grupos + eliminatorias hasta la final. Devuelve el campeon.

### `load_teams_from_fifa_csv()`
Carga los 48 equipos desde el archivo CSV del ranking FIFA y calcula su fuerza relativa.

### `load_groups_from_csv()`
Lee el archivo `groups.csv` y organiza los equipos en los 12 grupos oficiales.

### `run_simulation(groups)`
Funcion utilizada para ejecutar simulaciones en paralelo.

### `main()`
Coordina todo el proceso: carga de datos, validaciones, simulaciones masivas y presentacion de resultados.