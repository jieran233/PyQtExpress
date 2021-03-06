import sys
import time
import requests
import json
import configparser  # 读写INI
from subprocess import PIPE, Popen  # 执行系统命令
# from bp import bp
from threading import Thread  # 多线程
# 结束线程
import ctypes
import inspect
# PyQt5
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt
from qt_material import apply_stylesheet
from mainWindow import *
import wmi  # WMI 查询系统版本
from win32mica import MICAMODE, ApplyMica  # Win11 Mica
import my_window_effect  # Win10 Acrylic & Win7 Aero
import darkdetect  # Auto mode detect
# Win10 toast通知
# from win10toast import ToastNotifier
# 播放提示音
# from playsound import playsound
# import winsound


class Ui_MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(Ui_MainWindow, self).__init__(parent)
        self.setupUi(self)

    def setupUi(self, MainWindow):
        super(Ui_MainWindow, self).setupUi(MainWindow)
        # self.listWidget.addItem("hello")
        # self.listWidget.addItem("world")
        # self.commandLinkButton.clicked.connect(self.buttonClicked)
        # self.commandLinkButton_3.clicked.connect(self.buttonClicked)
        # self.executeButton.clicked.connect(self.buttonClicked)

    # def buttonClicked(self):
    #     sender = self.sender()
    #     name = sender.objectName()
    #     self.statusBar().showMessage(name + ' was pressed')
    #     if (name == "commandLinkButton_2"):
    #         self.textEdit.setText("发行说明")
    #     elif (name == "commandLinkButton"):
    #         self.textEdit.setText("有什么新鲜事吗")
    #     elif (name == "commandLinkButton_3"):
    #         self.textEdit.setText("入门指南")
    #     elif (name == "executeButton"):
    #         r = self.executeCommandLine(self.commandLineEdit.text())
    #         if (r['errinfo'] == ''):
    #             QMessageBox.information(self, 'outinfo', r['outinfo'], QMessageBox.Yes, QMessageBox.Yes)
    #         else:
    #             QMessageBox.critical(self, 'errinfo', r['errinfo'], QMessageBox.Yes, QMessageBox.Yes)
    #         print(r['errinfo'])

    def load(self):
        f = open('list.txt', encoding="utf-8")
        txt = f.read()
        f.close()
        packs = txt.split()
        for i in range(8):
            del packs[0]
        return packs

    def query(self, number, com='', order='desc'):
        # 初始化
        conf = configparser.ConfigParser()
        # 配置文件的绝对路径
        # conf_path = os.path.dirname(os.path.realpath(__file__)) + "/config.ini"
        conf_path = 'config.ini'
        # print(conf_path)
        # 读取配置文件
        conf.read(conf_path)
        TOKEN = conf.get('api', "token")
        # print(TOKEN)

        url = "https://v2.alapi.cn/api/kd"
        headers = {'Content-Type': "application/x-www-form-urlencoded"}
        # print(response.text)
        code = 0
        i = 0
        dic = {}
        maxRetry = 3  # 最大重试次数
        while code != 200:
            response = requests.get(
                url + '?number=' + str(number) + '&com=' + com + '&order=' + order + '&token=' + TOKEN,
                headers=headers)
            dic = json.loads(response.text)  # 解码 JSON 数据
            code = dic['code']  # 请求状态码
            # code = 114514  # debug only
            print('code=' + str(code))
            print('----------------')
            print(dic)
            print('----------------')
            i = i + 1
            if i > 1:
                self.statusbar.showMessage('API返回失败的消息，正在进行第' + str(i - 1) + '次重试...')
                time.sleep(3)  # 冷却CD
            if i > maxRetry:
                dic = {'code': 200, 'msg': 'success', 'data': {'nu': '0', 'com': 'none', 'state': 0, 'info': [{'content': ':( 请求失败了', 'time': ''}, {'content': '', 'time': ''}, {'content': '可能的原因及解决方法:', 'time': ''}, {'content': '- 包裹正在等待揽收，API尚未收录，请稍后重试', 'time': ''}, {'content': '- QPS超过限制，请稍后重试', 'time': ''}, {'content': '- API服务器维护/故障，稍后重试或查看API官网公告 http://www.alapi.cn/', 'time': ''}, {'content': '- 运单号无效/快递公司与运单号不对应，请核实后重试', 'time': ''}, {'content': '[点击重试  Click here to try again]', 'time': ''},]}, 'time': 0, 'log_id': 0}
                break
        return dic['data']['info']

    def listItemClicked(self, item):
        sender = self.sender()
        name = sender.objectName()
        # self.statusBar().showMessage(name + ' was pressed')
        if name == "listWidget":
            itext = item.text()
            print(itext + '-----------------------')
            self.listWidget_2.clear()
            for i in range(0, len(info[itext])):
                self.listWidget_2.addItem(info[itext][i]['time'] + ' ' + info[itext][i]['content'])
            self.statusbar.showMessage('#包裹['+itext+']的最新消息# ' + info[itext][0]['time'] + ' ' + info[itext][0]['content'])
        elif name == "listWidget_2":
            itext = item.text()
            print(itext)
            if itext == ' ' + '[点击重试  Click here to try again]':
                self.main(True)

    def closeEvent(self, event):
        """
        重写closeEvent方法，实现dialog窗体关闭时执行一些代码
        :param event: close()触发的事件
        :return: None
        """
        reply = QtWidgets.QMessageBox.question(self,
                                               '',
                                               "是否要退出程序？",
                                               QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                                               QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            stop_thread(thread_01)  # 停止线程
            print(self.executeCommandLine('taskkill /IM PyQtExpress.exe /F'))  # 干爆残留进程
            event.accept()
        else:
            event.ignore()

    def executeCommandLine(self, cli):
        try:
            # 返回的是 Popen 实例对象
            proc = Popen(
                str(cli),  # cmd特定的查询空间的命令
                stdin=None,  # 标准输入 键盘
                stdout=PIPE,  # -1 标准输出（演示器、终端) 保存到管道中以便进行操作
                stderr=PIPE,  # 标准错误，保存到管道
                shell=True)

            # print(proc.communicate()) # 标准输出的字符串+标准错误的字符串
            outinfo, errinfo = proc.communicate()
            outinfo = outinfo.decode('gbk')
            errinfo = errinfo.decode('gbk')
            infos = {'outinfo': outinfo, 'errinfo': errinfo}
            # print(outinfo.decode('gbk'))  # 外部程序(windows系统)决定编码格式
            # print(errinfo.decode('gbk'))
            return infos
        except Exception as e:
            print('\033[0;31m' + str(e.args) + '\033[0m')
            return

    # def playNotification(self):
    #     if sys.platform == 'win32':
    #         filename = 'notification.wav'
    #         winsound.PlaySound(filename, winsound.SND_FILENAME)

    def winver(self):
        w = wmi.WMI()
        os_info = w.Win32_OperatingSystem()[0]
        os_name = os_info.Name.encode('utf8').split(b'|')[0]
        obj = w.Win32_ComputerSystem()[0]
        # 解决乱码 参考资料https://cloud.tencent.com/developer/article/1737555
        # 字符串类str有一个encode() 方法，它是字符串向比特流的编码过程。
        # bytes类则有一个decode() 方法，它是比特流向字符串的解码过程。
        # 要解决的问题是将bytes类型的内容以汉字的形式输出，但是该部分内容是字符串类型。因此首先需要将该str转换成bytes类型，再decode解码为str输出。
        # 方法补充：如果我们直接定义bytes类型的变量，也可以直接使用str(s, ‘utf8′)的方式输出汉字
        os_name = str(os_name, 'utf8')
        os_name_ = os_name.split(' ')
        return os_name_[2]

    def main(self, notRepeat=False):
        print('\n')
        packs = self.load()
        print("packs:")
        print(packs)
        nums = []
        coms = []

        # if sys.platform == 'win32':
        #     msg = ToastNotifier()
        for i in range(len(packs)):
            if i % 2 == 0:
                nums.append(packs[i])
            else:
                coms.append(packs[i])
        print("nums:")
        print(nums)
        print("coms:")
        print(coms)
        global info
        info = {}

        # 单击触发绑定的槽函数
        self.listWidget.itemClicked.connect(self.listItemClicked)
        self.listWidget_2.itemClicked.connect(self.listItemClicked)
        self.listWidget_2.addItem('Loading...')

        while True:
            info.clear()
            print('-----------共有包裹: ' + str(len(nums)) + ' 个')
            for i in range(len(nums)):
                inums = nums[i]
                icoms = coms[i]
                self.statusbar.showMessage('请求数据中 (' + str(i + 1) + '/' + str(len(nums)) + ')')
                info[str(inums)] = self.query(inums, icoms)
                # oldinfo.append('')
                time.sleep(1)  # 防止超过API的QPS限制
            print('info:★★★★★')
            print(info)
            print('     ★★★★★')

            self.statusbar.clearMessage()
            self.listWidget.clear()
            self.listWidget_2.clear()
            keys = list(info.keys())
            print(keys)
            for i in range(0, len(keys)):
                self.listWidget.addItem(keys[i])
                # latestinfo = info[][0]['time'] + ' ' + info[][0]['content']
                # print(latestinfo)

            # for i in range(len(info)):
            #     # if (oldinfo[i] != ''):
            #     if info[i] != oldinfo[i]:
            #         print('latest info:')
            #         latestinfo = info[i][0]['time'] + ' ' + info[i][0]['content']
            #         print(latestinfo)
            #         expressinfo = '由' + coms[0] + '承运的包裹' + nums[0] + ': '
            #         self.statusbar.showMessage(expressinfo + latestinfo)
            #         # msg.show_toast(expressinfo, latestinfo)
            #         thread_02 = Thread(target=msg.show_toast, args=(expressinfo, latestinfo,))
            #         thread_02.start()
            #         bpbp = True
            #     oldinfo[i] = info[i]

            # self.listWidget_2.clear()
            # for i in range(0, len(infos)):
            #     self.listWidget_2.addItem(infos[i]['time'] + ' ' + infos[i]['content'])
            interval = self.spinBox.value()
            print(interval)
            if notRepeat == True:
                return
            time.sleep(interval)



def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # 实例化类
    mainWindow = Ui_MainWindow()
    # setup stylesheet
    apply_stylesheet(app, theme='dark_teal.xml')
    # 窗口效果
    winver = mainWindow.winver()
    # winver = '10'
    if winver == '11':  # Win11 Mica
        # 必须用样式表使背景透明，别用 setAttribute(Qt.WA_TranslucentBackground)，不然界面会卡顿
        mainWindow.setStyleSheet("background:transparent")
        hwnd = mainWindow.winId().__int__()  # On a PyQt/PySide window
        # mode = darkdetect.isDark()
        mode = MICAMODE.DARK  # Dark mode mica effect
        ApplyMica(hwnd, mode)
    elif winver == '10':  # Win10 Acrylic
        mainWindow.setStyleSheet("background:transparent")
        mainWindow.windowEffect = my_window_effect.WindowEffect()
        mainWindow.windowEffect.setAcrylicEffect(int(mainWindow.winId()))
    elif winver == '7' or mainWindow.winver().lower() == 'vista':  # Win7 Aero
        mainWindow.setStyleSheet("background:transparent")
        mainWindow.windowEffect = my_window_effect.WindowEffect()
        mainWindow.windowEffect.setAeroEffect(int(mainWindow.winId()))

    mainWindow.show()

    thread_01 = Thread(target=mainWindow.main)
    # 启动线程01
    thread_01.start()

    sys.exit(app.exec_())
