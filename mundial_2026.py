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


def simulate_match(a: Team, b: Team) -> MatchResult:
    lambda_a = 1.2 + (a.strength - b.strength) / 1200.0
    lambda_b = 1.2 + (b.strength - a.strength) / 1200.0
    lambda_a = max(0.3, lambda_a)
    lambda_b = max(0.3, lambda_b)
    goals_a = poisson_random(lambda_a)
    goals_b = poisson_random(lambda_b)
    return MatchResult(goals_a, goals_b)


def simulate_group(group: list):
    standings = [GroupStanding(t) for t in group]

    for i in range(len(group)):
        for j in range(i + 1, len(group)):
            res = simulate_match(group[i], group[j])

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


def simulate_knockout_match(a: Team, b: Team) -> Team:
    res = simulate_match(a, b)
    if res.goals_a != res.goals_b:
        return a if res.goals_a > res.goals_b else b
    return random.choice([a, b])


def simulate_one_tournament(groups) -> Team:
    qualified = []
    third_places = []

    for g in groups:
        table = simulate_group(g)
        qualified.append(table[0].team)
        qualified.append(table[1].team)
        third_places.append(table[2])

    third_places.sort(key=lambda s: (-s.points, -s.goal_diff, -s.goals_for))
    for i in range(8):
        qualified.append(third_places[i].team)

    current_round = qualified[:]
    random.shuffle(current_round)

    while len(current_round) > 1:
        next_round = []
        for i in range(0, len(current_round), 2):
            winner = simulate_knockout_match(current_round[i], current_round[i + 1])
            next_round.append(winner)
        current_round = next_round

    return current_round[0]

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
    champion = simulate_one_tournament(groups)
    return champion.name

from multiprocessing import Pool, cpu_count

def main():
    global GLOBAL_GROUPS

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

    # contar resultados
    winners = {}
    for name in results:
        winners[name] = winners.get(name, 0) + 1

    print("\nResultados:\n")

    sorted_results = sorted(
        winners.items(),
        key=lambda x: x[1],
        reverse=True
    )

    for team, wins in sorted_results:
        probability = (wins / simulations) * 100
        print(f"{team:<20} {wins:>6} títulos   {probability:>6.2f}%")
if __name__ == "__main__":
    main()