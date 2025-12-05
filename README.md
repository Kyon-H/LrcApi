# LrcApi

forked from [HisAtri/LrcApi](https://github.com/HisAtri/LrcApi)

修改内容：

- 增加对本地封面的支持：优先从本地查找封面图片
- 修改 build.sh，解决构建本地 Docker 镜像失败问题
- 完善测试脚本

---



默认监听 28883 端口，API 地址 `http://0.0.0.0:28883/lyrics` ；新版 API 地址 `http://0.0.0.0:28883/jsonapi` ；封面 API 地址 `http://0.0.0.0:28883/cover` 。

### 启动参数

| 参数     | 类型 | 默认值 |
| -------- | ---- | ------ |
| `--port` | int  | 28883  |
| `--auth` | str  |        |

`--auth`参数用于 header 鉴权，留空则跳过鉴权。验证 header 中的`Authorization`或`Authentication`字段。如果鉴权不符合，则返回 403 响应。

也可以使用环境变量`API_AUTH`定义，其优先性低于`--auth`参数，但是更容易在 Docker 中部署。`-e API_AUTH=自定义一个鉴权key`

## 使用方法

创建`/config/config.json`文件（可选）

```json
{
    "server": {
        "ip": "0.0.0.0",
        "port": 8080
    },
    "auth": {
        "xxxxxx":"rw"
    }
}
```

### 二进制文件

上传至运行目录，`./lrcapi --port 8080 --auth 自定义一个鉴权key`

### Python 源文件

拉取本项目；或者下载后上传至运行目录，解压 tar.gz

安装依赖：`pip install -r requirements.txt`

启动服务：`python3 app.py --port 8080 --auth 自定义一个鉴权key`

### Docker 部署方式

```bash
docker buildx build --network=host -t lrcapi:local .
```

如果你正在使用 Navidrome，请将你的音乐文件目录映射到 Docker 内目录；例如如果你音乐存储的目录是`/www/path/music`，请将启动命令中的映射修改为 `/www/path/music:/www/path/music`

然后访问 `http://0.0.0.0:28883/lyrics` 或新版 API `http://0.0.0.0:28883/jsonapi`

图片 API 地址为 `http://0.0.0.0:28883/cover`

注意：图片返回目前采用反向代理策略，可能存在一定的上下行流量消耗和延迟。

支持使用 Nginx 或 Apache 进行反向代理与 SSL。

### 搭建Pytest测试环境

虚拟环境（可选）

```shell
python3.10 -m venv venv
source .venv/bin/activate
(venv) pip3 install -r requirements.txt
```

另外安装 pytest 和 dotenv

```shell
pip3 install pytest dotenv
```

创建`/config/config.json`文件

```json
{
    "server": {
        "ip": "0.0.0.0",
        "port": 8080
    },
    "auth": {
        "aabbccdd":"rw"
    }
}
```

项目根目录创建 `.env` 文件，内容如下：

```
AUTH_TOKEN=aabbccdd
```

执行命令：

```shell
pytest -q --collect-only # 查看发现的测试用例
pytest # 执行全部测试
pytest -vs tests/test_app.py::test_cover_route # 执行单个测试
```

vscode设置pytest后更方便测试和debug

![image-20251205235913086](https://raw.githubusercontent.com/kyon-h/image/master/typora/image-20251205235913086.png)
