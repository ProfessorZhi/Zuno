# Windows 下安装 MinIO

本文档说明如何在 Windows 本机安装 MinIO，并让 Zuno 使用该对象存储服务。

## 1. 准备目录

先创建一个目录，例如：

```powershell
D:\minio
```

再创建数据目录：

```powershell
D:\minio\data
```

## 2. 下载 MinIO

在 `D:\minio` 目录中打开 PowerShell，执行：

```powershell
Invoke-WebRequest -Uri "https://dl.min.io/aistor/minio/release/windows-amd64/minio.exe" -OutFile "minio.exe"
.\minio.exe --version
```

## 3. 获取 License

较新的 MinIO Windows 版本需要 License 才能使用完整管理界面。可以到官方页面申请个人版本 License：

- <https://www.min.io/download/aistor-server?platform=windows>

下载后将 License 文件放到：

```powershell
D:\minio\minio.license
```

## 4. 启动 MinIO

执行：

```powershell
.\minio.exe server D:\minio\data --license D:\minio\minio.license
```

## 5. 配置管理员账号

如果需要修改默认管理员账号，可执行：

```powershell
setx MINIO_ROOT_USER admin
setx MINIO_ROOT_PASSWORD admin123
```

修改后，记得同步更新 Zuno 本地配置中的对象存储访问参数。

## 6. 配置 Bucket 权限

确保 MinIO 服务正在运行，然后打开控制台：

```text
http://127.0.0.1:9001
```

进入对应 bucket，为需要公开读写的路径授予合适权限。

如果你沿用默认开发配置，注意把 Zuno 使用的 bucket 名称和访问参数保持一致。

## 7. 说明

- 如果你通过 Docker 启动整套服务，通常不需要单独处理这份 Windows 本地安装流程。
- 本文档面向本机开发环境，不建议直接照搬到生产环境。
