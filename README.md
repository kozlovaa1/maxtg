# MAX to Telegram relay bot

Бот пересылает сообщения из выбранных чатов MAX в Telegram.

Проект основан на репозитории [chsrdev/maxtg](https://github.com/chsrdev/maxtg).

## Возможности

- Пересылка текстовых сообщений из MAX в Telegram.
- Пересылка изображений.
- Поддержка нескольких MAX-чатов через `MAX_CHAT_IDS`.
- Маршрутизация разных MAX-чатов в разные Telegram-чаты через `TG_CHAT_MAP`.
- Запуск нескольких экземпляров бота с разными env-файлами через Docker Compose.
- Опциональные мониторинговые сообщения в Telegram через `MONITOR_ID`.

## Ограничения

- Поддерживаются не все типы сообщений MAX.
- Файлы кроме изображений могут отображаться как необработанные вложения.
- При большом количестве сообщений подряд часть сообщений может не успевать пересылаться.
- Использование неофициального клиента MAX может быть нестабильным.

## Требования

Для обычного запуска:

- Python 3.11 или совместимая версия Python 3.
- Аккаунт MAX.
- Telegram-бот, созданный через [@BotFather](https://t.me/BotFather).

Для Docker-запуска:

- Docker.
- Docker Compose v2.

## Получение токена MAX

В исходном проекте инструкция по получению токена MAX вынесена в закрепленное сообщение Telegram-чата автора: [t.me/intchaserlive](https://t.me/intchaserlive).

## Настройка

Создайте env-файл с настройками:

```env
MAX_TOKEN=token_from_max
MAX_CHAT_IDS=max_chat_id_1,max_chat_id_2
TG_BOT_TOKEN=telegram_bot_token
TG_CHAT_ID=telegram_chat_id
TG_CHAT_MAP=max_chat_id_1:telegram_chat_id_1,max_chat_id_2:telegram_chat_id_2
MONITOR_ID=optional_telegram_monitor_chat_id
MONITOR_DEBUG=0
```

Поля:

- `MAX_TOKEN` - токен MAX.
- `MAX_CHAT_IDS` - один или несколько ID чатов MAX через запятую.
- `TG_BOT_TOKEN` - токен Telegram-бота.
- `TG_CHAT_ID` - ID Telegram-чата, группы или канала для пересылки по умолчанию.
- `TG_CHAT_MAP` - необязательная карта маршрутов `max_chat_id:telegram_chat_id` через запятую. Можно записывать в несколько строк; комментарии после `#` игнорируются.
- `MONITOR_ID` - необязательный Telegram chat id для сервисных уведомлений.
- `MONITOR_DEBUG` - `1`, чтобы включить подробные служебные сообщения без текста исходных сообщений.

Для приватных Telegram-каналов ID обычно начинается с `-100`.

Если `TG_CHAT_MAP` не задан, все чаты из `MAX_CHAT_IDS` пересылаются в `TG_CHAT_ID`.
Если MAX-чат есть в `TG_CHAT_MAP`, сообщение уйдет в указанный для него Telegram-чат.
Если MAX-чат есть в `MAX_CHAT_IDS`, но отсутствует в `TG_CHAT_MAP`, используется запасной `TG_CHAT_ID`.
Если для отслеживаемого MAX-чата не найден ни маршрут в `TG_CHAT_MAP`, ни `TG_CHAT_ID`, сообщение не пересылается.

Пример маршрутизации:

```env
MAX_CHAT_IDS=-71032535556121,-72646267836456
TG_CHAT_ID=-1009999999999
TG_CHAT_MAP=-71032535556121:-1001111111111,-72646267836456:-1002222222222
```

Многострочный вариант с комментариями:

```env
TG_CHAT_MAP="
# родители
-71032535556121:-1001111111111,
# класс
-72646267836456:-1002222222222
"
```

## Получение ID чатов

MAX chat id:

1. Откройте [web.max.ru](https://web.max.ru).
2. Перейдите в нужный чат.
3. Возьмите ID из адресной строки.

Telegram chat id:

1. Для личного чата можно использовать бота, который показывает ваш Telegram ID.
2. Для группы или канала добавьте туда своего Telegram-бота.
3. Дайте боту права на отправку сообщений.
4. Узнайте chat id группы или канала удобным для вас способом.

## Запуск без Docker

Установите зависимости:

```bash
pip install -r requirements.txt
```

Запустите бот:

```bash
python starter.py
```

По умолчанию приложение читает настройки из `.env`.

## Запуск через Docker Compose

В репозитории есть `Dockerfile` и пример Compose-конфигурации `docker-compose.example.yml`.
Рабочий `docker-compose.yml` считается локальным файлом окружения и не хранится в Git.

Сделайте его из примера:

```bash
cp docker-compose.example.yml docker-compose.yml
```

После копирования при необходимости измените имя сервиса, `container_name`, `env_file` и `BOT_NAME`.
Создайте `.env` или другой env-файл, указанный в `env_file`, и запустите сервис:

```bash
docker compose up -d --build maxtg_bot
```

Посмотреть состояние:

```bash
docker compose ps maxtg_bot
```

Посмотреть логи:

```bash
docker logs --tail 200 maxtg_bot
```

После изменения кода пересоберите и пересоздайте сервис:

```bash
docker compose up -d --build --force-recreate maxtg_bot
```

После изменения env-файла тоже пересоздайте сервис, чтобы Docker заново прочитал `env_file`:

```bash
docker compose up -d --force-recreate maxtg_bot
```

## Проверка

1. Отправьте тестовое сообщение в отслеживаемый MAX-чат.
2. Проверьте, что сообщение появилось в указанном Telegram-чате.
3. Если настроен `MONITOR_ID`, проверьте сервисные уведомления.
