

```markdown:README.md
# Python业务脚本集合

## 项目简介
这是一个基于Flask的Web服务项目，提供了多个实用的业务接口，包括文件处理、时间服务、GitLab数据统计、Webhook处理等功能。项目采用模块化设计，具有统一的响应格式和错误处理机制。

## 主要功能
1. **Markdown文件管理**
   - 保存Markdown文件
   - 获取文件目录结构
   - 支持多级目录管理

2. **时间服务**
   - 获取北京时间
   - 获取香港时间
   - 获取日本时间
   - 支持多时区配置

3. **GitLab统计**
   - 获取用户提交记录
   - 统计提交次数和频率
   - 生成提交数据报告

4. **自动构建系统**
   - 支持Git分支切换
   - 自动执行构建命令
   - 文件压缩和下载

5. **文件处理服务**
   - 文件下载代理
   - 视频流处理
   - 临时文件管理

6. **Webhook服务**
   - 自动部署支持
   - Git仓库同步
   - 构建流程自动化

## 技术栈
- Python 3.x
- Flask Web框架
- PostgreSQL数据库
- Flask-CORS跨域支持
- python-dotenv环境变量管理

## 项目结构
```
project/
├── app.py              # 应用主入口
├── routes/            # 路由模块
│   ├── markdown_route.py
│   ├── time.py
│   ├── gitlab.py
│   ├── webhook.py
│   ├── video_route.py
│   ├── file_download.py
│   ├── command_executor.py
│   └── LoveLetter.py
├── utils/            # 工具类
│   └── request.py    # 统一响应处理
└── requirements.txt  # 项目依赖
```README.md

## 环境要求
- Python 3.x
- PostgreSQL数据库
- Node.js (用于部分构建功能)
- Git

## 环境变量配置
项目使用.env文件管理环境变量，需要配置以下变量：
```
DB_NAME=数据库名
DB_USER=数据库用户名
DB_PASSWORD=数据库密码
DB_HOST=数据库主机
DB_PORT=数据库端口
MD_SAVE_PATH_ROOT=Markdown文件保存路径
AUTO_BUILD_SHELL_PATH=自动构建脚本路径
ZIP_DIRECTORY_PATH=压缩文件存储路径
```

## 安装使用
1. 克隆项目
```bash
git clone [项目地址]
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，填入相应配置
```

4. 运行项目
```bash
python app.py
```

## API文档
所有API遵循统一的响应格式：
```json
{
    "code": 200,
    "message": "操作信息",
    "body": {
        // 响应数据
    }
}
```

## 贡献指南
欢迎提交Issue和Pull Request来完善项目。

## 开源协议
MIT License
```

