# Essence smart-parser
Include parser, summarizer and ebedder.


# DEV BUILD
1. `conda create -n essence_parser python=3.11`
2. `conda activate essence_parser`
3. `pip install -r requirements/dev.txt`
4. `pre-commit install` — установка прекоммитов
5. `pre-commit run --all-files` — проверка кодстайла (будет запускаться автоматически при коммитах)

Для локального тестирования использовать также `source docker/deploy.sh up --app`

При этом у вас должен быть поднят postgres, elk.
