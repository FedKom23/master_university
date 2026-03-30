import tomllib
from kaggle import KaggleApi
import os
import pytest


def get_kaggle_score(competition_name, team_name, min_score):
    api = KaggleApi()

    os.environ['KAGGLE_USERNAME'] = os.environ['HW4_KAGGLE_USERNAME']
    os.environ['KAGGLE_KEY'] = os.environ['HW4_KAGGLE_KEY']

    api.authenticate()

    leaderboard = api.competition_leaderboard_view(competition_name)

    for team in leaderboard:
        team = team.__dict__
        if team['_team_name'] == team_name:
            score = float(team['_score'])
            return score >= min_score

    pytest.fail(f"Команда '{team_name}' не найдена в лидерборде Kaggle. "
                f"Проверь правильность имени в hw4/config.toml.")


def test_kaggle_score():
    competition_name = os.environ['KAGGLE_COMPETITION_NAME']
    min_score = float(os.environ['MIN_SCORE'])

    config_path = "config.toml"

    with open(config_path, 'rb') as f:
        config = tomllib.load(f)

    team_name = config["kaggle"][0]["team_name"]

    assert team_name, "Не задано название команды"

    print(f"Соревнование: {competition_name}")
    print(f"Команда: {team_name}")
    print(f"Минимальный балл: {min_score}")

    assert get_kaggle_score(competition_name, team_name, min_score), \
        f"Решение команды {team_name} не набрало необходимый скор {min_score}"
