# NN_Whisper_docker

Ссылки:

https://lablab.ai/t/whisper-api-flask-docker                      - с апи

https://hub.docker.com/r/onerahmet/openai-whisper-asr-webservice  - образ

https://github.com/openai/whisper                                 - репозиторий

https://github.com/sovse/base_rus_whisper_stt                     - дообученная русская модель

=======

Сборка из dockerHub для экономии времени:

https://hub.docker.com/r/onerahmet/openai-whisper-asr-webservice

https://github.com/openai/whisper

=======

Как протестировать API?

Вы можете протестировать API, отправив POST-запрос на маршрут http://localhost:8084/whisper с файлом в нем. Тело должно быть form-data.

Вы можете использовать следующую команду curl для тестирования API:

curl -F "file=@D:/Develop/NeuronNetwork/Whisper/docker_mi/NN_whisper_docker/whisper/example/nana-in-my-dreams.wav" http://localhost:8084/whisper

>>>>>>> test_rest
