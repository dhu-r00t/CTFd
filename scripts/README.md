## 如何部署新生赛/暑期集训平台
By EZForever

~~果然程序员最讨厌的事就是没有文档/写文档~~

### 0. 系统配置

下文的配置过程以阿里云ECS上的Debian9.9系统为例。使用其他服务器或操作系统的，请自行调整构建步骤。

#### 0.1 镜像源

阿里云的Debian系统已经配置好了apt和pip的镜像源，所以不用额外操作。

#### 0.2 确保系统在最新状态

```sh
apt update && apt upgrade -y
python2 -m pip install -U pip
pip2 install -U setuptools # 没有这一步的话，阿里云ECS上部署的时候第1.3步会出错
```

### 1. CTFd服务配置

#### 1.1 为CTFd服务创建低权限用户

这一步是为了提升安全性，因为只有CTFd本身不是运行在docker里的。

```sh
useradd -s /usr/sbin/nologin -r -M ctfd
```

#### 1.2 部署CTFd平台文件

```sh
mkdir -p /opt/ctfd && cd /opt/ctfd
git clone https://github.com/EZForever/CTFd
chown -R ctfd:ctfd CTFd # 更改文件所有者，使得ctfd用户有权访问克隆下来的repo
```

#### 1.3 安装CTFd依赖

```sh
pip2 install -r CTFd/requirements.txt
```

#### 1.4 安装systemd unit

```sh
cp CTFd/scripts/ctfd.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable ctfd.service
```

#### 1.5 启动CTFd服务

确保4000端口开放，然后：

```sh
service ctfd start
```

访问主机的4000端口，进行CTFd初始化配置。

之后就可以使用`service ctfd {start|stop|status}`操作这一服务，或者使用`journalctl _SYSTEMD_UNIT=ctfd.service`查看服务运行日志。

**注意**：如果服务启动失败，它会无限重启。建议在启动服务之后过几秒检查一下服务运行状态，如果发现服务开始重启了，立刻停止服务并检查运行日志。

### 2. docker服务配置

#### 2.1 安装docker和docker-compose

```sh
wget https://get.docker.com/ -O - | sh
pip install docker-compose
```

#### 2.2 配置docker镜像源

否则，在构建镜像时pull比较大的镜像会很吃力。

```sh
vi /etc/docker/daemon.json
service docker reload
```

`/etc/docker/daemon.json`的内容如下（这里使用了中科大的镜像源）：
```json
{
    "registry-mirrors": [ "https://docker.mirrors.ustc.edu.cn" ]
}
```

#### 2.3 建立docker-compose文件夹结构

```sh
cd /opt/ctfd
mkdir -p docker/test && cd docker
vi docker-compose.yml
vi test/Dockerfile
```

`docker-compose.yml`的内容如下：
```yml
version: "2"

services:
    test: # 这个test容器一方面是为了测试，另一方面是为了避免没放题的时候没有容器可供启动导致服务无限重启
        build: ./test # 从test子目录（中的Dockerfile）构建镜像
        port:
            - "4001:80" # 容器内的80端口映射到容器外的4001端口
        restart: always
```

`test/Dockerfile`的内容如下：
```Dockerfile
FROM nginx # 以nginx镜像为基础构建镜像

# 不对镜像进行任何操作（这只是个测试用容器）

EXPOSE 80 # 向外暴露80端口
```

#### 2.4 安装systemd unit

```sh
cp ../CTFd/scripts/ctfd_docker.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable ctfd_docker.service
```

#### 1.5 启动docker服务

确保4001端口开放，然后：

```sh
service ctfd_docker start
```

访问主机的4001端口，应该可以看到“Welcome to Nginx”的页面。

之后就可以使用`service ctfd_docker {start|stop|status}`操作这一服务，或者使用`journalctl _SYSTEMD_UNIT=ctfd_docker.service`查看服务运行日志。

**注意**：如果服务启动失败，它会无限重启。建议在启动服务之后过几秒检查一下服务运行状态，如果发现服务开始重启了，立刻停止服务并检查运行日志。

### 3. 放web/pwn题所需的docker容器

#### 3.1 准备文件

如果想要使用已经配好的容器，忽略这一步。

在`/opt/ctfd/docker`下建立新的子文件夹（下文以`web1`为例），将构建镜像所需的文件和Dockerfile放进去。

#### 3.2 改`docker-compose.yml`

在`services:`下新增加一段：

- 如果使用已经配好的容器：
```yml
     web1: # service名称，注意不能包含大写字母
        image: python:3-buster # 容器的基础镜像名称
        container_name: my_container # 配好的容器名称
        port: # 对外暴露的端口，可以存在多组
            - "4002:80" # 容器内的80端口映射到容器外的4002端口
        restart: always # 容器启动失败或运行结束时重启
```

- 如果从Dockerfile构建镜像：
```yml
    web1: # service名称，注意不能包含大写字母
        build: ./web1 # 放置所需文件和Dockerfile的文件夹
        port: # 对外暴露的端口，可以存在多组
            - "4002:80" # 容器内的80端口映射到容器外的4002端口
        restart: always # 容器启动失败或运行结束时重启
```

**注意**：yml文件不支持使用Tab缩进。

#### 3.3 重启docker服务

```sh
service ctfd_docker stop
service ctfd_docker start
```

访问`docker-compose.yml`中指定的端口进行测试。第一次构建镜像时，因为要pull所需的基础镜像，所以需要一点时间。可以检查docker服务的运行状态和运行日志了解构建进程。

