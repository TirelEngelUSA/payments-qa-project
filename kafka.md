# Памятка: команды Kafka изнутри Docker-контейнера (с пояснениями для тестирования)

Примеры ориентированы на контейнер с именем `payments-qa-project-kafka-1` и broker на `localhost:9092`.
Заменяйте `payments-qa-project-kafka-1`, `<topic>`, `<group>` на свои значения.

Ниже — команды + короткое объяснение, зачем каждая команда полезна в контексте тестирования.

---

## 1) Попасть в контейнер (интерактивный shell)
- С bash:
  docker exec -it payments-qa-project-kafka-1 bash

- Если bash нет (sh):
  docker exec -it payments-qa-project-kafka-1 sh

Зачем в тестировании:
- Внутри контейнера можно запускать утилиты/скрипты и быстро диагностировать проблемы (проверить конфигурацию, версии, доступность бинарников). Полезно при расследовании фейлов тестов или при конфигурационных проблемах.

---

## 2) Однострочные команды (без интерактивного shell)
- Список топиков:
  docker exec -it payments-qa-project-kafka-1 kafka-topics --bootstrap-server localhost:9092 --list

Зачем:
- Убедиться, что нужные топики созданы перед прогоном тестов (smoke/integ tests). Быстрое подтверждение окружения.

- Описание топика:
  docker exec -it payments-qa-project-kafka-1 kafka-topics --bootstrap-server localhost:9092 --describe --topic <topic>

Зачем:
- Проверить количество партиций, реплик, лидеров. Это важно для тестов производительности, тестов устойчивости (failover) и для понимания, как сообщения распределяются.

---

## 3) Найти kafka-утилиты, если команды не в PATH
- Поиск бинарников:
  docker exec -it payments-qa-project-kafka-1 bash -lc "find / -maxdepth 4 -type f -name 'kafka-topics*' 2>/dev/null || find / -maxdepth 4 -type f -name '*kafka*' 2>/dev/null"

Зачем:
- Иногда в образе утилиты лежат не в PATH. Нужна для быстрого запуска инструментов в CI/debugging.

- Частые места:
  /usr/bin, /opt/confluent/bin, /usr/local/bin

Если нашли путь, используйте его:
  docker exec -it payments-qa-project-kafka-1 /opt/confluent/bin/kafka-topics --bootstrap-server localhost:9092 --list

Зачем:
- Надёжный способ запускать команды в скриптах CI, если PATH непредсказуем.

---

## 4) Просмотр сообщений (consumer)
- Чтение всех сообщений с начала:
  docker exec -it payments-qa-project-kafka-1 kafka-console-consumer --bootstrap-server localhost:9092 --topic <topic> --from-beginning

Зачем:
- Проверка того, что продьюсеры действительно отправили сообщения; удобно для валидации схемы/полезной нагрузки в ручных и интеграционных тестах.

- Вывести только N сообщений:
  docker exec -it payments-qa-project-kafka-1 kafka-console-consumer --bootstrap-server localhost:9092 --topic <topic> --from-beginning --max-messages 20

Зачем:
- Быстрый осмотр нескольких сообщений без бесконечного стрима — удобно при отладке.

- Показать ключ и timestamp (если поддерживается):
  docker exec -it payments-qa-project-kafka-1 kafka-console-consumer --bootstrap-server localhost:9092 --topic <topic> --from-beginning --max-messages 20 --property print.key=true --property print.timestamp=true

Зачем:
- В тестах важно проверять ключи (routing/partitioning), а также таймстемпы (проверка задержек, правильности времени события).

- Прочитать сообщения только новых (tail режим):
  docker exec -it payments-qa-project-kafka-1 kafka-console-consumer --bootstrap-server localhost:9092 --topic <topic>

Зачем:
- Наблюдение за поведением системы в реальном времени при выполнении теста (например, запускается сценарий, и вы проверяете, что события публикуются).

- Прочитать конкретную партицию и оффсет:
  docker exec -it payments-qa-project-kafka-1 kafka-console-consumer --bootstrap-server localhost:9092 --topic payments --partition 0 --offset 170 --max-messages 10

Зачем:
- Проверка порядковости сообщений, повторная проверка проблемных оффсетов при расследовании багов.

---

## 5) Запись в топик (producer)
- Интерактивный producer:
  docker exec -it payments-qa-project-kafka-1 kafka-console-producer --broker-list localhost:9092 --topic <topic>
  # вводите строки вручную, Enter — отправка

- Отправить одно сообщение из команды:
  echo '{"user_id":1,"amount":100}' | docker exec -i payments-qa-project-kafka-1 kafka-console-producer --broker-list localhost:9092 --topic <topic> --property "parse.key=false"

Зачем:
- Генерация тестовых сообщений для интеграционных тестов: позитивные/негативные сценарии, тесты на валидацию, тесты на idempotency/дедупликацию.
- Удобно для воспроизведения багов (послать сообщение, которое вызывает ошибку в consumer).

---

## 6) Consumer-groups и оффсеты
- Описать consumer-group:
  docker exec -it payments-qa-project-kafka-1 kafka-consumer-groups --bootstrap-server localhost:9092 --describe --group <group>

Зачем:
- Проверка lag'а и оффсетов: важно для тестов надёжности и гарантии доставки (at-least-once/at-most-once). Позволяет увидеть, что consumer реально потребляет сообщения.

- Показать все группы:
  docker exec -it payments-qa-project-kafka-1 kafka-consumer-groups --bootstrap-server localhost:9092 --all-groups --describe

Зачем:
- Диагностика, если несколько сервисов читают из топика; помогает проверить, не влияют ли тестовые consumers на продовые.

- Получить earliest/latest оффсеты:
  docker exec -it payments-qa-project-kafka-1 kafka-run-class kafka.tools.GetOffsetShell --broker-list localhost:9092 --topic <topic> --time -1   # latest
  docker exec -it payments-qa-project-kafka-1 kafka-run-class kafka.tools.GetOffsetShell --broker-list localhost:9092 --topic <topic> --time -2   # earliest

Зачем:
- Оценить размер очереди/накопление сообщений; полезно для проверок retention и для планирования повторного потребления сообщений.

---

## 7) Дамп топика в файл на хосте
- Сохранить вывод consumer в файл на хосте:
  docker exec -i payments-qa-project-kafka-1 kafka-console-consumer --bootstrap-server localhost:9092 --topic <topic> --from-beginning --timeout-ms 1000 > /tmp/topic_dump.json

Зачем:
- Создать артефакт теста — можно сохранять сообщения для пост-анализа, регрессионного сравнения, или для использования в тестах на корректность схемы/значений.

---

## 8) Логи и диагностика контейнера
- Посмотреть логи контейнера:
  docker logs -f payments-qa-project-kafka-1

Зачем:
- Понять, почему брокер не стартует, или почему клиенты не подключаются; важная часть root-cause анализа при падении тестов.

- Проверить конфиги (advertised.listeners и др.):
  docker exec -it payments-qa-project-kafka-1 bash -lc "grep -R \"advertised.listeners\\|listeners\\|broker.id\" /etc /opt / | head -n 50"

Зачем:
- Часто проблемы с соединением связаны с неверными advertised.listeners — эти команды помогают быстро найти причину.

---

## 9) Полезные советы и частые тестовые сценарии
- Проверки схемы/формата:
  - Считать N сообщений и прогнать через jsonschema/jq, чтобы убедиться, что структура ожидаемая.
- Проверки порядка:
  - Отправлять упорядоченные элементы с одинаковым ключом и проверять порядок при потреблении из соответствующей партиции.
- Проверки устойчивости:
  - Перезапускать брокер/потребителя и смотреть, как изменяются оффсеты и lag.
- Проверки idempotency / дубликатов:
  - Послать одно и то же сообщение несколько раз, проверить, что consumer/сервис корректно обрабатывает дубликаты.
- Нагрузочные проверки:
  - Использовать массовую отправку или отдельные инструменты (kcat/producer scripts) и смотреть retention/throughput/latency.
- Контроль артефактов:
  - Всегда сохраняйте дампы/логи при неудаче теста — это упрощает анализ.

---

## 10) Быстрые примеры (копировать и подставлять)
- Список топиков:
  docker exec -it payments-qa-project-kafka-1 kafka-topics --bootstrap-server localhost:9092 --list

- Вывести 10 сообщений с начала (и посмотреть ключи/время):
  docker exec -it payments-qa-project-kafka-1 kafka-console-consumer --bootstrap-server localhost:9092 --topic payments --from-beginning --max-messages 10 --property print.key=true --property print.timestamp=true

- Описать consumer-groups:
  docker exec -it payments-qa-project-kafka-1 kafka-consumer-groups --bootstrap-server localhost:9092 --all-groups --describe

- Дамп топика в файл:
  docker exec -i payments-qa-project-kafka-1 kafka-console-consumer --bootstrap-server localhost:9092 --topic payments --from-beginning --timeout-ms 1000 > /tmp/payments_dump.json

---

## 11) Что делать, если что-то не работает
- Команда "not found" — найдите путь к утилите и используйте полный путь.
- Ошибки подключения — проверьте `advertised.listeners` в логах и попробуйте адрес/порт, указанный там.
- Нет сообщений — проверьте retention, убедитесь, что producer пишет в тот же топик/partition, и что вы читаете с нужного оффсета.
- Если пришлёте вывод конкретной команды и/или логи контейнера — помогу проанализировать и составить точную команду для исправления.




kafka-console-consumer
Что делает: простой консольный consumer, читает сообщения из топика и выводит их в stdout.
Для чего в тестировании: быстрый просмотр сообщений, валидация payload, проверка порядка и таймингов, наблюдение за событиями в реальном времени.
Пример: docker exec -it payments-qa-project-kafka-1 kafka-console-consumer --bootstrap-server localhost:9092 --topic <topic> --from-beginning --max-messages 20

kafka-console-producer
Что делает: отправляет строки из stdin в указанный топик (producer).
Для чего в тестировании: генерировать тестовые события вручную или в скриптах, воспроизводить баги, проверять реакцию consumers.
Пример: docker exec -it payments-qa-project-kafka-1 kafka-console-producer --broker-list localhost:9092 --topic <topic> echo '{"id":1}' | docker exec -i payments-qa-project-kafka-1 kafka-console-producer --broker-list localhost:9092 --topic <topic>

kafka-topics
Что делает: список/создание/описание/изменение топиков.
Для чего в тестировании: убедиться, что топики созданы с нужными партициями/репликами, проверить состояние.
Пример: docker exec -it payments-qa-project-kafka-1 kafka-topics --bootstrap-server localhost:9092 --list docker exec -it payments-qa-project-kafka-1 kafka-topics --bootstrap-server localhost:9092 --describe --topic <topic>

kafka-consumer-groups
Что делает: показывает оффсеты, lag и состояние consumer group.
Для чего в тестировании: проверка, что consumers реально читают, измерение lag, диагностика задержек и гарантии доставки.
Пример: docker exec -it payments-qa-project-kafka-1 kafka-consumer-groups --bootstrap-server localhost:9092 --describe --group <group>

kafka-run-class kafka.tools.GetOffsetShell
Что делает: показывает earliest/latest оффсеты для партиций топика.
Для чего в тестировании: измерить объём накопленных сообщений, оценить retention/lag.
Пример: docker exec -it payments-qa-project-kafka-1 kafka-run-class kafka.tools.GetOffsetShell --broker-list localhost:9092 --topic <topic> --time -1

kafka-broker-api-versions
Что делает: запрашивает версии API, которые поддерживает брокер.
Для чего в тестировании: быстро проверить доступность брокера и совместимость клиента.
Пример: docker exec -it payments-qa-project-kafka-1 kafka-broker-api-versions --bootstrap-server localhost:9092

kafka-producer-perf-test / kafka-consumer-perf-test
Что делает: встроенные перфоманс-тесты для генерации/потребления сообщений с измерением throughput/latency.
Для чего в тестировании: нагрузочные проверки, базовая оценка производительности брокера/сети.
Пример: docker exec -it payments-qa-project-kafka-1 kafka-producer-perf-test --topic <topic> --num-records 10000 --record-size 200 --throughput 1000 --producer-props bootstrap.servers=localhost:9092

kafka-verifiable-producer / kafka-verifiable-consumer
Что делает: инструменты для проверяемой отправки/получения сообщений (используются в тестах на корректность).
Для чего в тестировании: end-to-end проверка доставки и согласованности (напр., при автотестах кластера).
Пример: docker exec -it payments-qa-project-kafka-1 kafka-verifiable-producer --broker-list localhost:9092 --topic <topic> --num-records 100

kafka-reassign-partitions
Что делает: утилита для переселения партиций между брокерами (reassignment).
Для чего в тестировании: тестировать поведение при ребалансе/перераспределении, проверить устойчивость при изменении топологии.
Пример: docker exec -it payments-qa-project-kafka-1 kafka-reassign-partitions --execute --reassignment-json-file reassignment.json --bootstrap-server localhost:9092

kafka-configs
Что делает: просмотр/изменение конфигураций брокеров/топиков/clients.
Для чего в тестировании: менять retention, cleanup.policy, max.message.bytes и т.п. для тестовых сценариев.
Пример: docker exec -it payments-qa-project-kafka-1 kafka-configs --bootstrap-server localhost:9092 --entity-type topics --entity-name <topic> --describe

kafka-delete-records
Что делает: удаляет записи до указанного оффсета (truncate) для партиций.
Для чего в тестировании: очищать топик между тестами, воспроизводить сценарии с отсутствием старых данных.
Пример: docker exec -it payments-qa-project-kafka-1 kafka-delete-records --bootstrap-server localhost:9092 --offset-json-file offsets.json

kafka-acls
Что делает: управление ACL (доступом) в Kafka.
Для чего в тестировании: проверять поведение при наличии/отсутствии прав, тесты безопасности.
Пример: docker exec -it payments-qa-project-kafka-1 kafka-acls --authorizer-properties zookeeper.connect=... --add --allow-principal User:tester --operation Read --topic <topic>

kafka-log-dirs
Что делает: показывает места хранения логов партиций на брокерах, выводит usage/replica info.
Для чего в тестировании: диагностика дискового пространства/реплик.
Пример: docker exec -it payments-qa-project-kafka-1 kafka-log-dirs --bootstrap-server localhost:9092 --describe --broker-list 1

kafka-streams-application-reset
Что делает: помогает сбросить состояние Kafka Streams приложения (offsets, state stores).
Для чего в тестировании: подготовить окружение для повторного запуска streams-приложений в тестах.
Пример: docker exec -it payments-qa-project-kafka-1 kafka-streams-application-reset --application-id <app> --bootstrap-servers localhost:9092 --input-topics <topic>

Дополнительно (Confluent / Mirror / Admin утилиты)
Confluent CLI и дополнительные утилиты (kafka-rest, control-center, mirror-maker) полезны в специфических окружениях; используются для интеграционных тестов с Confluent-пакетом.
Короткие рекомендации по использованию в контейнере и в CI

Всегда указывать --bootstrap-server корректно (используйте localhost внутри контейнера или имя сервиса внутри docker-network).
Для автоматизации тестов используйте однострочные docker exec команды и логируйте вывод в артефакт (файл).
Для idempotent/чистых тестов: используйте kafka-delete-records или создавайте отдельные временные топики, а по завершении удаляйте их.
Для перф-тестов и нагрузочных тестов используйте kafka-producer-perf-test и kafka-consumer-perf-test, затем проверяйте метрики/latency.

