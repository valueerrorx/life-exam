echo "sudo apt install python3-pyqt5 pyqt5-dev-tools qttools5-dev-tools"
echo "Converting ..."

pyuic5 MyCustomWidget.ui > MyCustomWidget.py

echo "done"
