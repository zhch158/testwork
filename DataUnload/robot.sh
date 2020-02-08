#robot.exe -d X:/Temp -v Y_M:2019-01 -v DATADIR:X:/Temp/201901 -t '下载项目投入明细' yusys_sy.robot
if [ $# != 1 ]
then
	echo "Usage $0 yyyy-mm"
	exit 1
fi
yyyymm=$1
robot.exe -d X:/Temp/log yusys_login.robot
robot.exe -d X:/Temp/log -v Y_M:$yyyymm yusys_sy.robot
