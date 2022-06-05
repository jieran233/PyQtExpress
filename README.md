# PyQtExpress
 简易的快递查询工具 - 基于PyQt5编写

[![State-of-the-art Shitcode](https://img.shields.io/static/v1?label=State-of-the-art&message=Shitcode&color=7B5804)](https://github.com/trekhleb/state-of-the-art-shitcode)

## Usage

### 下载Release

[Releases · jieran233/PyQtExpress (github.com)](https://github.com/jieran233/PyQtExpress/releases)

### 或从源码打包

> 参见：[PyInstaller Manual — PyInstaller 5.1 documentation](https://pyinstaller.org/en/stable/)

```
pyinstaller -F -w -n PyQtExpress main.py
```

### 运行

#### 编辑 list.txt

`list.txt` 记录了要查询的快递单号和快递公司编号

以下是一份正确的list.txt示例，其中包含了自带的注释，参考本示例及其注释即可完成编辑：

```
# 格式：快递单号 快递公司编号
# 快递公司编号参见 express_completes_code.txt
# 不要修改上述内容
75884717911052 ZTO
75884341031756 ZTO
```

#### 编辑 config.ini

`config.ini`记录了API相关的配置设置，如token。**默认填写了我的token，虽然您可以不用修改，即使用我的token调用API，但我还是更建议您自行注册API账号，使用您自己的token（完全免费）**

使用的API为 [ALAPI](http://www.alapi.cn/) ，注册登录后在控制台即可找到token，粘贴填入即可。

