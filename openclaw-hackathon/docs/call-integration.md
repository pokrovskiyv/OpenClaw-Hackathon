# Интеграция звонков через ClawdTalk для 6-агентной страховой системы

## 1) Цель интеграции

Сделать входящий телефонный канал для ранее зарегистрированного клиента при ДТП, где голосовой диалог ведётся через `ClawdTalk`, а бизнес-решение внутри разговора проходит через минимум 6 агентов пайплайна хакатона:

1. Front Desk
2. Claims Officer
3. Assessor
4. Fraud Analyst
5. Senior Reviewer
6. Finance

Ключевая идея: `ClawdTalk` даёт телефонию (STT/TTS + номер + WebSocket), а OpenClaw остаётся оркестратором агентной логики и инструментов.

## Критичное уточнение по вашему сценарию

Звонок обрабатываем как кейс **только для ранее зарегистрированного клиента** с действующей страховкой. Поэтому до запуска 6 агентов всегда делаем короткий pre-auth этап.

---

## 2) Что подтверждено по документации

По `clawdtalk.com` и `team-telnyx/clawdtalk-client`:

- ClawdTalk работает через **исходящее WebSocket-подключение** клиента (`ws-client.js`) к серверу (`/ws`), без публичного экспонирования вашего gateway.
- Голосовой поток: телефон → Telnyx STT → ClawdTalk → WebSocket-клиент → OpenClaw gateway (`/v1/chat/completions`) → ответ обратно в TTS.
- Для углублённых запросов клиент использует вызов `sessions_send` через endpoint `POST /tools/invoke`.
- Для SMS используется API вида `POST /v1/messages/send` (клиентский код).
- Для исходящих звонков используется `POST /v1/calls`.
- В gateway обязательно разрешить `sessions_send` в allowlist, иначе voice-проксирование в основной агент не сработает.

По OpenClaw-материалам проекта:

- Gateway-центричная архитектура и явное управление tools/policies.
- Есть поддержка multi-agent routing и последовательной передачи контекста между ролями.
- Для хакатона требуется 6-ролевой пайплайн с объяснимыми бизнес-решениями.

---

## 2.1) Технический протокол интеграции (как это работает по шагам)

Ниже — фактический runtime-поток на основе `clawdtalk-client`.

1. `scripts/connect.sh start` поднимает `node scripts/ws-client.js`.
2. `ws-client.js` подключается к `wss://clawdtalk.com/ws` и отправляет auth:

```json
{
  "type": "auth",
  "api_key": "cc_live_***",
  "owner_name": "...",
  "agent_name": "..."
}
```

3. Сервер присылает события `type: "event"`, например:
   - `context_request` (старт звонка),
   - `message|transcription|transcript` (распознанная речь),
   - `deep_tool_request` (сложный запрос),
   - `call.ended`.
4. При распознанной речи клиент вызывает OpenClaw gateway:
   - `POST /v1/chat/completions`
   - заголовки:
     - `Authorization: Bearer <gateway_token>`
     - `x-clawdbot-agent-id: main`
     - `x-clawdbot-session-key: voice-call-<call_id>`
5. Если модель запросила tool calls, `ws-client.js` вызывает:
   - `POST /tools/invoke`
   - тело: `{ "tool": "<name>", "args": {...}, "sessionKey": "voice" }`
6. Для «глубоких» задач или SMS клиент использует:
   - `POST /tools/invoke` с `tool: "sessions_send"`
   - `sessionKey: "agent:<mainAgentId>:main"`
7. Голосовой ответ отправляется в ClawdTalk WebSocket:

```json
{
  "type": "response",
  "call_id": "clk_...",
  "text": "Короткий ответ клиенту"
}
```

8. При завершении звонка отправляется внутренняя сводка в main session через `sessions_send`.

---

## 2.2) Минимальный gateway-конфиг для рабочего канала

```json
{
  "gateway": {
    "http": {
      "endpoints": {
        "chatCompletions": {
          "enabled": true
        }
      }
    },
    "tools": {
      "allow": ["sessions_send"]
    },
    "auth": {
      "token": "${GATEWAY_TOKEN}"
    }
  }
}
```

`skill-config.json` (минимум):

```json
{
  "api_key": "${CLAWDTALK_API_KEY}",
  "server": "https://clawdtalk.com",
  "max_conversation_turns": 20
}
```

---

## 2.3) Где именно вставить проверку «зарегистрированный клиент»

Проверку делаем в `Main Voice Orchestrator` сразу после первого meaningful transcript, до запуска роли Front Desk.

Технически это 3 коротких шага:

1. `lookup_customer_by_phone(call.from_number)`
2. `verify_pin(customer_id, pin)`
3. `lookup_active_policy(customer_id)`

Если любой шаг неуспешен:

- отправить `type=response` с отказом/инструкцией,
- прервать пайплайн 6 ролей.

Если успешно:

- записать в контекст:

```json
{
  "verification": {
    "caller_id_match": true,
    "pin_verified": true,
    "policy_active": true,
    "verified": true
  }
}
```

---

## 2.4) Минимальный алгоритм оркестратора (технический MVP)

```text
on_call_start(call_id):
  init claim_context

on_user_transcript(text):
  if !claim_context.verification.verified:
    run pre-auth (phone -> pin -> policy)
    if fail: respond + stop

  collect incident basics

  run Front Desk
  run Claims Officer
  run Assessor
  run Fraud Analyst
  run Senior Reviewer
  run Finance

  build voice_short + internal_full
  send voice_short to caller
  persist internal_full
```

---

## 2.5) Команды запуска для демо (операционный минимум)

```bash
cd ~/clawd/skills/clawdtalk-client
./setup.sh
./scripts/connect.sh start
./scripts/connect.sh status
```

Проверка health перед демо:

- WebSocket = connected
- `sessions_send` разрешён в gateway tools allowlist
- pre-auth lookup endpoints доступны

---

## 3) Самая простая архитектура для хакатона (рекомендуемая)

```text
Клиент звонит -> ClawdTalk/Telnyx (STT/TTS) -> WebSocket client (clawdtalk-client)
-> OpenClaw Gateway -> Main Voice Orchestrator
-> (Pre-auth: Caller ID + PIN + policy lookup)
-> Последовательно: Front Desk -> Claims Officer -> Assessor -> Fraud Analyst -> Senior Reviewer -> Finance
-> Короткая сводка клиенту в голос
```

### Почему так

- Телефонный UX остаётся быстрым (ClawdTalk voice loop).
- Pre-auth отсекает незарегистрированные звонки до тяжёлой агентной логики.
- Бизнес-решение формируется строго через 6 агентов, как в требованиях хакатона.
- OpenClaw может сохранять единый контекст кейса и трассировку решений.

---

## 4) Как понять, что звонит зарегистрированный клиент с полисом

Минимальный и практичный flow:

1. **Caller ID match**: по номеру телефона ищем клиента в вашей базе (`customer_id`).
2. **PIN-челлендж**: просим короткий PIN, который клиент задаёт в кабинете/при регистрации.
3. **Policy check**: проверяем, что полис активен и документы присутствуют (в вашем policy store).
4. Если любой шаг не прошёл — не запускаем 6-агентный пайплайн; переводим в fallback:

- «Не удалось подтвердить профиль, соединяю с оператором / откройте приложение для верификации».

### Почему этого достаточно для хакатона

- Используются уже доступные механики ClawdTalk (Caller ID + PIN).
- Логика простая и объяснима на защите.
- Нет необходимости строить отдельный сложный KYC-диалог в голосе.

---

## 5) Как включить 6 агентов в одном разговоре (без усложнений)

Используем один `Main Voice Orchestrator`, который после pre-auth запускает фиксированную цепочку из 6 ролей.

1. Вход звонка попадает в `main` session (это уже поддерживает `clawdtalk-client`).
2. Оркестратор собирает минимум входа по ДТП.
3. Оркестратор последовательно вызывает 6 ролей (строго по порядку).
4. Каждый агент пишет вывод в `claim_context.agent_outputs.<role>`.
5. После `Finance` клиент получает короткий ответ; полный отчёт идёт во внутренний лог.

---

## 6) Минимальные шаги внедрения

## Шаг 1. Поднять voice-канал ClawdTalk

1. Зарегистрироваться на `clawdtalk.com`, привязать номер, получить API key.
2. Установить `clawdtalk-client` skill.
3. Запустить `./setup.sh` и затем `./scripts/connect.sh start`.
4. Проверить `./scripts/connect.sh status`.

## Шаг 2. Проверить gateway-политику tools

В конфиге OpenClaw добавить allow для `sessions_send`:

```json
{
  "gateway": {
    "tools": {
      "allow": ["sessions_send"]
    }
  }
}
```

Без этого ClawdTalk-клиент не сможет проксировать сложные запросы в основной session.

## Шаг 3. Добавить pre-auth перед запуском 6 ролей

- Проверка по номеру телефона (caller -> customer).
- Проверка PIN (голосом или DTMF, если доступно в вашем канале).
- Проверка полиса и базовых документов в policy store.
- Только после статуса `verified=true` запускать 6-этапный workflow.

## Шаг 4. Настроить входной voice-agent как простой маршрутизатор

- Входной агент должен:
  - распознать, что это ДТП-кейс,
  - инициировать `claim_id`,
  - собрать первичные поля (кто, где, когда, номер полиса, безопасность людей),
  - передать кейс в 6-ролевой pipeline.

## Шаг 5. Реализовать единый формат межагентного контекста

Рекомендуемый каркас:

```json
{
  "claim_id": "...",
  "caller": { "customer_id": "...", "phone": "..." },
  "verification": {
    "caller_id_match": true,
    "pin_verified": true,
    "verified": true
  },
  "policy": { "policy_id": "...", "status": "..." },
  "incident": { "datetime": "...", "location": "...", "description": "..." },
  "agent_outputs": {
    "front_desk": {},
    "claims_officer": {},
    "assessor": {},
    "fraud_analyst": {},
    "senior_reviewer": {},
    "finance": {}
  },
  "final_decision": {}
}
```

## Шаг 6. Управлять голосовым latency (минимально)

Чтобы звонок не «зависал»:

- Держим 1 короткую промежуточную реплику на этап (без сложной разговорной оркестрации).
- Если шаг дольше таймаута — простая fallback-фраза и переход к следующему безопасному действию.

---

## 7) Ролевой сценарий внутри одного звонка

1. **Front Desk**: регистрация обращения и нормализация входных данных.
2. **Claims Officer**: проверка покрытия/исключений/активности полиса.
3. **Assessor**: оценка ущерба и total-loss логика.
4. **Fraud Analyst**: сигналы подозрительности и risk-score.
5. **Senior Reviewer**: финальное решение approve/deny/refer.
6. **Finance**: расчёт выплаты, deductible, запуск выплаты/или постановка в очередь.

На голос клиенту выводится только безопасная краткая версия решения; полный reasoning остаётся во внутреннем журнале.

---

## 8) Безопасность и соответствие

- Включить PIN-защиту звонка и проверку Caller ID (возможности ClawdTalk).
- Не запускать decision pipeline при `verified=false`.
- Не раскрывать внутренние fraud-правила и внутренние risk-факторы в голосовом ответе клиенту.
- Ограничить tools по принципу least privilege.
- Логировать цепочку решений 6 агентов для последующего аудита.
- Хранить секреты (API ключи и gateway token) через ENV-переменные, а не в открытом JSON.

---

## 9) Что делать прямо сейчас (практический MVP-план)

1. Подключить `clawdtalk-client` и подтвердить стабильный звонок на `main` session.
2. Добавить pre-auth (`caller_id + pin + policy lookup`) как обязательный gate.
3. Добавить в `main` обязательный workflow: последовательный вызов 6 ролей.
4. Зафиксировать контракт `claim_context` (единый JSON между ролями).
5. Добавить 2 режима ответа:
   - `voice_short` (клиенту в звонке),
   - `internal_full` (в логи/досье кейса).
6. Прогнать 7 базовых сценариев (`TC-001..TC-007`) в формате voice-in → verification → pipeline → decision.

Так вы получаете рабочую демонстрацию «телефон -> 6 агентов -> бизнес-решение», полностью в логике требований хакатона.

---

## 10) Риски и как закрыть

- **Риск:** длинные паузы в разговоре при тяжёлых шагах.
  - **Митигировать:** короткие прогресс-реплики + таймауты + fallback фразы.
- **Риск:** агент отвечает напрямую, обходя часть 6-этапного процесса.
  - **Митигировать:** жёсткое правило в системном промпте orchestrator: финальный ответ только после всех 6 ролей.
- **Риск:** `sessions_send` не разрешён в gateway.
  - **Митигировать:** preflight проверка на старте + health-check перед демо.
- **Риск:** утечка приватных данных в голосовом канале.
  - **Митигировать:** redaction policy в voice-ответах, минимум PII в озвучке.

---

## 11) Вывод

Для вашей задачи оптимален путь: **ClawdTalk как телефонный ingress + OpenClaw как оркестратор 6 страховых агентов**.

Это позволяет:

- быстро поднять рабочие звонки без публичного экспонирования gateway,
- надёжно отсечь незарегистрированные обращения через простой pre-auth,
- сохранить строгий 6-ролевой бизнес-процесс,
- объяснить решение и с точки зрения бизнес-логики, и с точки зрения системной архитектуры (критерии хакатона),
- не усложнять голосового агента сверх MVP.

## Источники

- HACKATHON.md (локальный документ проекта)
- .agents/skills/openclaw/SKILL.md (локальный skill)
- openclaw-hackathon/docs/hubs.md
- openclaw-hackathon/docs/clawhub.md
- https://clawdtalk.com/
- https://github.com/team-telnyx/clawdtalk-client (README.md, SKILL.md, setup.sh, scripts/connect.sh, scripts/ws-client.js)
