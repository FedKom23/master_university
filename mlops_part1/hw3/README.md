# Домашнее задание HW3: Статистика по рекламным событиям

## Как сдавать решение и в какой срок

### Оценка
За задание можно получить 5 баллов, если сдать до Soft Deadline. После него, но до Hard Deadline -- половина баллов. После решение не оценивается.

### Дедлайны
**Soft Deadline - 12 марта в 23:59.**

**Hard Deadline - 19 марта в 23:59.**

### Формат сдачи
1. Нужно завести ветку `hw3` и вести свою разработку там.
2. Вам доступны для добавления, изменения файлы `solution.py`, `requirements.txt`.
3. Как только считаете, что решение готово, заводите Merge Request из ветки `hw3` в `master`.
4. Если с прошлым МР-ом что-то было не так и вы решили завести новый, закройте, пожалуйста, старый самостоятельно. Это делается на странице МР-а: Троеточие -> Close merge request.
5. Если бот отписал комментарий с баллами в ваш MR можете ставить в assignee `Бекетов Роман`.
6. Profit!

## Общее описание задачи 
Напишите скрипт, который собирает и агрегирует статистику по рекламным событиям за период с 2026-02-02 по 2026-02-10

- Выполнить 2 SQL-запроса к ClickHouse (mydb.events) - **Задача Q1 и Q2**
- Использовать SDK ClickHouse (clickhouse-connect) - **необходимо рассчитывать агрегаты исключительно через sql запрос**
- Загрузить словарь маппинга кампаний из S3 (MinIO)
- Обработать данные в pandas
- Записать результаты в Redis

## Данные

```
p.s.

Примеры (семплы) данных лежат в папке hw3/example_data 
```

#### Таблица mydb.events в ClickHouse

| Поле        | Тип     | Описание                                        |
| ----------- | ------- | ----------------------------------------------- |
| event_date  | Date    | дата события                                    |
| campaign_id | UInt64  | id кампании                                     |
| user_id     | UInt64  | id пользователя                                 |
| event       | String  | тип события (`impression`, `click`, `purchase`) |
| price       | Float64 | стоимость покупки (для purchase)                |
| platform    | String  | платформа (`web`, `ios`, `android`)             |

### Словарь campaigns.csv на S3

| campaign_id | category | region | is_brand |

- category — категория бизнеса
- region — регион 
- is_brand — 1 если брендовая кампания, иначе 0

Файл необходимо загрузить через boto3 из S3 (MinIO).

## Задача Q1 — Дневные метрики по платформам (2.5 балла)

Необходимо рассчитать агрегаты по:
```
event_date, platform
```

Для каждой пары (event_date, platform) нужно вычислить:

- **impressions** – кол-во показов: количество событий `event = 'impression'`
- **clicks** - кол-во кликов по баннеру: количество событий `event = 'click'`
- **purchases** - кол-во покупок товара после клика на баннер: количество событий `event = 'purchase'`
- **revenue** - доход рекламной кампании: в поле `price` содержится цена покупки
- **ctr** - click/impressions
- **cr** - conv/click
- **cpm** - revenue/impressions*1000
- **rev_3d** - cкользящая сумма revenue за текущий день и 2 предыдущих дня: `revenue(day-2) + revenue(day-1) + revenue(day)`
- **top3_rev_share**
  - Для каждого (event_date, platform):
    - считаем revenue по каждой кампании
    - сортируем по убыванию revenue
    - берём топ-3 кампании
    - суммируем их revenue
  - Делим revenue топ-3 на общий revenue дня : `top3_rev_share = revenue_top3/total_revenue`

**📌 Ключ Redis для Q1** = `hw3:q1:{event_date}:{platform}`

Пример _hw3:q1:2026-02-02:web_

📌 JSON структура значения Q1
```json
  "impressions": 123
  "clicks": 45
  "purchases": 6
  "revenue": 1234.56
  "uniq_users": 78
  "ctr": 0.12
  "cr": 0.13
  "cpm": 45.67
  "rev_3d": 3456.78
  "top3_rev_share": 0.42
```

## Задача Q2 — Метрики по категории и региону (2.5 балла)

- Посчитать метрики по campaign_id
- Смаппить с campaigns.csv
- Сгруппировать по (category, region)

Для каждой пары (category, region) нужно вычислить:
- revenue
- campaigns - количество уникальных campaign_id в группе
- brand_revenue_share - доля revenue брендовых кампаний: `brand_revenue/total_revenue`
- top_campaign_id - ID кампании с максимальным revenue в группе
- top_campaign_revenue

**📌 Ключ Redis для Q2** = `hw3:q2:{category}:{region}`

Пример _hw3:q2:retail:EU_

📌 JSON структура значения Q2
```json
  "revenue": 123456.78
  "campaigns": 12
  "brand_revenue_share": 0.34
  "top_campaign_id": 1042
  "top_campaign_revenue": 54321.12
```

## Требования к реализации
- Использовать clickhouse-connect
- Использовать SQL (ch синтаксис) для агрегаций
- Использовать boto3 для загрузки S3
- Использовать pandas для merge и группировок
- Записать результаты в Redis
- Точность до 2 знаков после запятой
- **Баллы начисляются только если все ключи и все поля совпадают.**

