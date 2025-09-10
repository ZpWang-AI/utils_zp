while true; do
    # =======================
    {cmd}
    # =======================

    pid=$!
    wait $pid
    status=$?
    if [ $status -eq 0 ]; then
        echo "> SH: Successfully completed."
        break
    else
        echo "> SH: Retry."
        sleep 1
    fi
done
