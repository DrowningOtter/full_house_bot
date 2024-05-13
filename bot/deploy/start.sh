while getopts "dbs" opt; do
    case $opt in 
        d)
            option_d=true
            ;;
        b)
            option_b=true
            ;;
        s)
            option_start=true
            ;;
        \?)
            echo incorrect option
            exit 1
            ;;
    esac
done

if [[ ! -z "${PRE}" ]]; then
    docker compose up premake_queues --build
fi
args=""
if [[ "$option_b" = true ]]; then
    # args+=" --build"
    docker build -t tgbot_image ../
fi

if [[ "$option_d" = true ]]; then
    args+=" -d"
fi

if [[ -z "${TGBOT_API_TOKEN}" && "$option_start" != true ]]; then
    echo specify bot token
    exit 1
fi
if [[ -z "${USER_ID}" ]]; then
    echo specify user id
    exit 1
fi

# docker compose up bot $args --no-recreate
if [[ "$option_start" = true ]]; then
    docker start bot_$USER_ID
else
    docker run --network local_debug_botnet -e TGBOT_API_TOKEN=$TGBOT_API_TOKEN -e USER_ID=$USER_ID --name bot_$USER_ID $args -v ./../../bot_site/media:/media tgbot_image
fi