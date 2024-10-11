# 待修复问题：
1. 日志文件中的日志打印了两份 --- **Fixed**：问题莫名其妙消失了
2. pyinstaller打包后的程序，运行时提示找不到src --- **Fixed**：test子目录不与src重名，from的src省略
3. test_stop_after_start用例测试未通过 --- **Fixed**：通过@patch.object方法打桩的多个mocker作为测试函数入参顺序应相反
4. 异步弹出MessageBox，导致进程异常退出 --- **Fixed**：所有窗口都关闭导致QApplication退出，setQuitOnLastWindowClosed设置为False解决
5. 备份路径斜杠错误 --- **Fixed**：PySide6的路径格式固定为/而非\，使用os.path.normpath转换即可

# 易用性提升：
1. 适配未使用PySide6库的父项目

    父项目不引用PySide6时，可不安装PySide6库，程序可正常运行

# 补充用例测试：
