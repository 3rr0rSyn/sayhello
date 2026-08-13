# SayHello

*Say hello to the world.*

> 基于《[Flask Web 开发实战](https://helloflask.com/book/1)》的示例应用。

本分支已升级为支持现代 Python（3.11+）和 Flask 3.x，并带有简易留言管理后台。

## 功能

- 发布与浏览留言
- 管理后台：增删改查、搜索、分页
- 兼容 Python 3.11 / 3.12 / 3.13

## 安装

克隆项目：
```bash
$ git clone https://github.com/3rr0rSyn/sayhello.git
$ cd sayhello
```

创建虚拟环境并安装依赖：

```bash
$ python3 -m venv .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
```

初始化数据库并运行：

```bash
$ flask initdb
$ flask run
 * Running on http://127.0.0.1:5000/
```

也可以生成测试数据：

```bash
$ flask forge
```

## 管理后台

访问 `/admin/`，默认密码为 `admin`。  
**注意：** 生产环境请务必通过环境变量 `ADMIN_PASSWORD` 修改默认密码。

## 部署

使用宝塔面板部署请参考 [宝塔部署.md](宝塔部署.md)。

## 开源协议

本项目基于 MIT 协议开源，详见 [LICENSE](LICENSE) 文件。
