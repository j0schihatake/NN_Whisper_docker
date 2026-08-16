# NN_Whisper_docker

Как запустить (с постоянным томом для кэша модели, чтобы `large-v3` (~2.88 ГБ) не перекачивался
заново при каждом перезапуске контейнера):

```
docker build -t whisper:local .

# Именованный том создаётся docker'ом от root — контейнер работает под whisper-user (uid 1000),
# так что права нужно поправить один раз перед первым запуском, иначе загрузка модели упадёт
# с PermissionError:
docker run --rm -v whisper-model-cache:/cache alpine:latest chown -R 1000:1000 /cache

docker run -d --name whisper \
  -p 28084:28084 \
  -v whisper-model-cache:/home/whisper-user/whisper/.cache/whisper \
  whisper:local
```

`large-v3` требует заметного объёма памяти при загрузке весов в оперативную память (порядка
6-7 ГБ) — проверено, что при лимите памяти Docker Desktop VM ниже этого контейнер убивается по
OOM ещё на этапе `torch.load`, независимо от того, откуда докачивается сама модель.

Если этот репозиторий выложен рядом с `javader_java` (как `modules/NN_Whisper_docker`), поднимать
вручную командами выше не обязательно — он уже заведён как сервис `whisper` в едином
`javader/compose.yaml` (`chown`-шаг оттуда тоже уже сделан за вас через `whisper-cache-init`).
Том там объявлен как `external` — на совсем свежей машине его нужно создать один раз
(`docker volume create whisper-model-cache`), Compose сам внешний том не создаёт:

```
docker compose -p javader -f javader/compose.yaml up -d whisper
```

Ссылки:

https://lablab.ai/t/whisper-api-flask-docker                      - с апи

https://hub.docker.com/r/onerahmet/openai-whisper-asr-webservice  - образ

https://github.com/openai/whisper                                 - репозиторий

https://github.com/sovse/base_rus_whisper_stt                     - дообученная русская модель

Сборка из dockerHub для экономии времени:

https://hub.docker.com/r/onerahmet/openai-whisper-asr-webservice

https://github.com/openai/whisper

Как протестировать API?

Вы можете протестировать API, отправив POST-запрос на маршрут http://localhost:28084/whisper с файлом в нем. Тело должно быть form-data.

Вы можете использовать следующую команду curl для тестирования API:

curl -F "file=@D:/Develop/NeuronNetwork/Whisper/docker_mi/NN_whisper_docker/whisper/example/nana-in-my-dreams.wav" http://localhost:28084/whisper
