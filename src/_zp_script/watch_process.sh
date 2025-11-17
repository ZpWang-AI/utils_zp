process="$( ps -def | grep zp | grep -v grep | grep -v watch_process )"
# echo "$process"

echo -e "\n= python ============="
echo "$process" | grep " python "
echo "$process" | grep "/python "
echo -e "======================\n"

echo -e "= sh ================="
echo "$process" | grep " sh "
echo -e "======================\n"

echo -e "= others ============="
echo "$process" | grep -v " sh " | grep -v " python " | grep -v "/python "
echo -e "======================\n"


