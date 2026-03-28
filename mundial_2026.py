import random
import math
from collections import defaultdict
import csv
from datetime import datetime


class Team:
    def __init__(self, name: str, strength: float):
        self.name = name
        self.strength = strength


class MatchResult:
    def __init__(self, goals_a: int, goals_b: int):
        self.goals_a = goals_a
        self.goals_b = goals_b


class GroupStanding:
    def __init__(self, team: Team):
        self.team = team
        self.points = 0
        self.goals_for = 0
        self.goal_diff = 0


def poisson_random(lambda_val: float) -> int:
    L = math.exp(-lambda_val)
    k = 0
    p = 1.0
    while p > L:
        k += 1
        p *= random.random()
    return k - 1


def simulate_match(a: Team, b: Team, goals_dict=None) -> MatchResult:
    lambda_a = 1.2 + (a.strength - b.strength) / 600.0
    lambda_b = 1.2 + (b.strength - a.strength) / 600.0

    lambda_a = max(0.3, lambda_a)
    lambda_b = max(0.3, lambda_b)

    goals_a = poisson_random(lambda_a)
    goals_b = poisson_random(lambda_b)

    # sumar goles 
    if goals_dict is not None:
        goals_dict[a.name] += goals_a
        goals_dict[b.name] += goals_b

    return MatchResult(goals_a, goals_b)

def simulate_group(group: list, goals_dict=None):
    standings = [GroupStanding(t) for t in group]

    for i in range(len(group)):
        for j in range(i + 1, len(group)):
            res = simulate_match(group[i], group[j], goals_dict)

            standings[i].goals_for += res.goals_a
            standings[i].goal_diff += res.goals_a - res.goals_b

            standings[j].goals_for += res.goals_b
            standings[j].goal_diff += res.goals_b - res.goals_a

            if res.goals_a > res.goals_b:
                standings[i].points += 3
            elif res.goals_b > res.goals_a:
                standings[j].points += 3
            else:
                standings[i].points += 1
                standings[j].points += 1

    standings.sort(key=lambda s: (-s.points, -s.goal_diff, -s.goals_for))
    return standings

def simulate_knockout_match(a: Team, b: Team, goals_dict=None) -> Team:
    res = simulate_match(a, b, goals_dict)

    if res.goals_a != res.goals_b:
        return a if res.goals_a > res.goals_b else b
    #penales
    prob_a = a.strength / (a.strength + b.strength)
    return a if random.random() < prob_a else b
#Simulacion de Mejores Terceros
def get_best_third_places(groups: list, n: int = 8):
    third_places = []

    for group in groups:
        table = simulate_group(group)
        third_places.append(table[2])

    third_places.sort(key=lambda s: (-s.points, -s.goal_diff, -s.goals_for))

    return [s.team for s in third_places[:n]]

def simulate_one_tournament(groups, goals_dict=None):
    qualified = []
    third_places = []

    # fase de grupos
    for g in groups:
        table = simulate_group(g, goals_dict)
        qualified.append(table[0].team)
        qualified.append(table[1].team)
        third_places.append(table[2])

    # mejores terceros
    third_places.sort(key=lambda s: (-s.points, -s.goal_diff, -s.goals_for))
    for i in range(8):
        qualified.append(third_places[i].team)

    # eliminatorias
    current_round = qualified[:]
    random.shuffle(current_round)

    semifinal_losers = []

    # rondas hasta la final
    while len(current_round) > 2:
        next_round = []

        for i in range(0, len(current_round), 2):
            a = current_round[i]
            b = current_round[i + 1]

            winner = simulate_knockout_match(a, b, goals_dict)
            loser = b if winner == a else a

            # guardar perdedores de semifinal
            if len(current_round) == 4:
                semifinal_losers.append(loser)

            next_round.append(winner)

        current_round = next_round

    # final
    a, b = current_round[0], current_round[1]
    champion = simulate_knockout_match(a, b, goals_dict)
    runner_up = b if champion == a else a

    # partido por tercer lugar
    third_place = simulate_knockout_match(
        semifinal_losers[0],
        semifinal_losers[1],
        goals_dict
    )

    return champion.name, runner_up.name, third_place.name

NAME_MAPPING = {
    "Argentina": "Argentina",
    "France": "Francia",
    "Spain": "España",
    "Brazil": "Brasil",
    "England": "Inglaterra",
    "Portugal": "Portugal",
    "Netherlands": "Países Bajos",
    "Germany": "Alemania",
    "Belgium": "Bélgica",
    "Italy": "Italia",           
    "Croatia": "Croacia",
    "Uruguay": "Uruguay",
    "Colombia": "Colombia",
    "Morocco": "Marruecos",
    "Senegal": "Senegal",
    "Switzerland": "Suiza",
    "USA": "Estados Unidos",
    "Mexico": "México",
    "Norway": "Noruega",
    "Denmark": "Dinamarca",     
    "Poland": "Polonia",        
    "Japan": "Japón",
    "Korea Republic": "Corea del Sur",
    "Australia": "Australia",
    "IR Iran": "Irán",
    "Ecuador": "Ecuador",
    "Türkiye": "Turquía",        
    "Austria": "Austria",
    "Uzbekistan": "Uzbekistán",
    "Côte d'Ivoire": "Côte d'Ivoire",
    "Canada": "Canadá",
    "Qatar": "Qatar",
    "Saudi Arabia": "Arabia Saudita",
    "Jordan": "Jordania",
    "Iraq": "Irak",             
    "New Zealand": "Nueva Zelanda",
    "Haiti": "Haití",
    "Curaçao": "Curazao",
    "Congo DR": "RD Congo",    
    "Scotland": "Escocia",
    "Paraguay": "Paraguay",
    "Tunisia": "Túnez",
    "Egypt": "Egipto",
    "Cape Verde": "Cabo Verde",
    "Algeria": "Argelia",
    "Ghana": "Ghana",
    "Panama": "Panamá",
    "South Africa": "Sudáfrica", 
}

def load_teams_from_fifa_csv(csv_path: str = "fifa_ranking.csv"):
    teams_dict = {}
    latest_date = None

    with open(csv_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                team_name_fifa = row.get('country_full', row.get('team', '')).strip()
                rank_str = row.get('rank', row.get('position', '999'))
                points_str = row.get('total_points', row.get('points', '0'))
                date_str = row.get('rank_date', '')

                if not team_name_fifa or not rank_str.isdigit():
                    continue

                rank = int(rank_str)
                points = float(points_str.replace(',', '')) if points_str else 0.0

                if date_str:
                    try:
                        current_date = datetime.strptime(date_str, '%Y-%m-%d')
                        if latest_date is None or current_date > latest_date:
                            latest_date = current_date
                    except:
                        pass

                key = team_name_fifa.lower()
                if key not in teams_dict or (date_str and current_date > teams_dict[key]['date']):
                    teams_dict[key] = {
                        'name_fifa': team_name_fifa,
                        'rank': rank,
                        'points': points,
                        'date': current_date if 'current_date' in locals() 
                        else None
                    }
            except:
                continue

    teams = []
    for data in teams_dict.values():
        fifa_name = data['name_fifa']
        our_name = NAME_MAPPING.get(fifa_name, fifa_name)

        strength = max(800, 2200 - (data['rank'] * 15))

        teams.append(Team(our_name, strength))

    return teams

def load_groups_from_csv(path, teams):
    team_dict = {t.name: t for t in teams}
    groups_dict = {}

    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            g = row['group']
            name = row['team']

            if g not in groups_dict:
                groups_dict[g] = []

            if name in team_dict:
                groups_dict[g].append(team_dict[name])
            else:
                print(f" No encontrado: {name}")

    return list(groups_dict.values())


def run_simulation(groups):
    goals_dict = defaultdict(int)
    champion, runner_up, third = simulate_one_tournament(groups, goals_dict)
    return champion, runner_up, third, goals_dict

from multiprocessing import Pool, cpu_count


def main():
    global GLOBAL_GROUPS

    total_goals = defaultdict(int)

    teams = load_teams_from_fifa_csv("fifa_ranking.csv")
    print(f"Equipos cargados: {len(teams)}")

    groups = load_groups_from_csv("groups.csv", teams)
    GLOBAL_GROUPS = groups 

    print("\nGrupos cargados correctamente:")
    for i, g in enumerate(groups):
        print(f"Grupo {chr(65+i)}:", [t.name for t in g])


    simulations = 100000

    print("\nEjecutando simulacion\n")

    with Pool(cpu_count()) as p:
        results = p.map(run_simulation, [groups] * simulations)

    winners = {}
    runners_up = {}
    third_places = {}

    for champ, second, third, goals in results:
        winners[champ] = winners.get(champ, 0) + 1
        runners_up[second] = runners_up.get(second, 0) + 1
        third_places[third] = third_places.get(third, 0) + 1

        for team, g in goals.items():
            total_goals[team] += g
    # contar resultados

    print("\nCampeones:\n")

    sorted_results = sorted(
        winners.items(),
        key=lambda x: x[1],
        reverse=True
    )

    for team, wins in sorted_results:
        probability = (wins / simulations) * 100
        print(f"{team:<20} {wins:>6} títulos   {probability:>6.2f}%")

    print("\nGoles totales:\n")

    sorted_goals = sorted(
        total_goals.items(),
        key=lambda x: x[1],
        reverse=True
    )

    for team, g in sorted_goals[:20]:
        print(f"{team:<20} {g}")



    print("\nSubcampeones:\n")
    # Ordenamos por la cantidad de veces que quedaron en 2do lugar (el valor x[1])
    sorted_runners_up = sorted(runners_up.items(), key=lambda x: x[1], reverse=True)
    
    for team, counts in sorted_runners_up:
        probability = (counts / simulations) * 100
        # Mostramos el nombre, la cantidad de veces y el porcentaje
        print(f"{team:<20} {counts:>6} veces    {probability:>6.2f}%")

    print("\nTercer lugar:\n")
    # Ordenamos por la cantidad de veces que quedaron en 3er lugar
    sorted_third_places = sorted(third_places.items(), key=lambda x: x[1], reverse=True)
    
    for team, counts in sorted_third_places:
        probability = (counts / simulations) * 100
        # Mostramos el nombre, la cantidad de veces y el porcentaje
        print(f"{team:<20} {counts:>6} veces    {probability:>6.2f}%")


if __name__ == "__main__":
    main()