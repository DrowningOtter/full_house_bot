#!/bin/bash

docker ps | while IFS= read -r line; do
    # Проверяем, содержит ли текущая строка нужное слово
    if [[ "$line" == *tgbot_image* ]]; then
        # Если да, выводим её
        cont_id=$(echo $(echo $line | awk '{print $1}'))
        docker exec -t $cont_id kill -SIGUSR1 1
    fi
done