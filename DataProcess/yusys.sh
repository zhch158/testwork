#python yusys-detail-excel.py -c yusys-detail-excel.yaml -w F:/workspace/python/data -d 201912
if [ $# != 1 ]
then
	echo "Usage $0 yyyymm"
	exit 1
fi
yyyymm=$1
python yusys-detail-excel.py -c yusys-detail-excel.yaml -w F:/workspace/python/data -d $yyyymm
