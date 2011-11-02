cat << EOF | mail -s $6 $7

hostname and tty:
$1

min date_max date_min mag_max mag:
$2

Starting time:
$3
End time:
$4

Total time:
$5

EOF
