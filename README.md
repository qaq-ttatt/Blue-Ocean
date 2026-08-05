# Blue-Ocean
Our future lies in the vast ocean of stars

## LangChain 智能体 Demo

`demo_agent/` 下是一个基于 LangChain + LangGraph 的 ReAct 智能体小示例，自带两个自定义工具：

- `calculator`：安全的四则算术表达式求值（AST 白名单，不用裸 `eval`）
- `current_time`：返回当前本地日期时间

### 快速开始

```bash
# 1. 创建虚拟环境并安装依赖
python -m venv .venv
.venv/Scripts/pip install -r requirements.txt

# 2. 配置模型（支持 OpenAI 及任意兼容 OpenAI 协议的服务商）
cp .env.example .env   # 填入 OPENAI_API_KEY，按需改 OPENAI_MODEL / OPENAI_BASE_URL

# 3. 运行
.venv/Scripts/python -m demo_agent.main "帮我算一下 (123 + 45) * 2"  # 单次提问
.venv/Scripts/python -m demo_agent.main        # 不带参数则进入交互式对话
.venv/Scripts/python -m demo_agent.main -r     # 交互式对话，并恢复上次会话历史
```

会话历史保存在根目录 `chat_history.json`（已加入 `.gitignore`）。

### 结构

```
demo_agent/
├── tools.py   # 自定义工具定义（@tool 装饰器）
├── agent.py   # ChatOpenAI + create_react_agent 构建智能体
└── main.py    # 命令行入口（单次提问 / 交互式）
```
