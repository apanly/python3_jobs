#!/bin/sh

sync(){
    cmd="cd /data/www/private_deploy/jobs  ;  git fetch --all ; git reset --hard origin/master"
    echo "\033[32m"$cmd
    eval $cmd
    DATE=`date +%Y%m%d%H%M%S`
    echo $DATE > /data/www/release_version/python3_jobs
    return 0
}

reload() {
    cmd="export ops_config='production' && /data/www/vir_python3/bin/uwsgi --reload /data/www/logs/python3_jobs/app.pid"
    echo "\033[32m"$cmd
    eval $cmd
    return 0
}

stop() {
    cmd="export ops_config='production' && /data/www/vir_python3/bin/uwsgi --stop /data/www/logs/python3_jobs/app.pid"
    echo "\033[32m"$cmd
    eval $cmd
    return 0
}

start() {
    cmd="export ops_config='production' && /data/www/vir_python3/bin/uwsgi --ini /data/www/private_deploy/python3_jobs/uwsgi.ini"
    echo "\033[32m"$cmd
    eval $cmd
    return 0
}

case "$1" in
    sync)
        sync
        ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    reload)
        reload
        ;;
    *)
        echo "Usage: sh release.sh {sync|start|stop|reload}" >&2
        exit 3
        ;;
esac