if [[ -z "${TGBOT_API_TOKEN}" ]]; then
    echo specify bot token
    exit 1
fi
if [[ -z "${USER_ID}" ]]; then
    echo specify user id
    exit 1
fi

if [[ ! -z "${PRE}" ]]; then
    docker compose up premake_queues --build
fi
docker compose up bot --build -d