#======= 前端
# 下载到本地
git clone https://github.com/Unagi-cq/THChatUI
# 进入web ui目录
cd ./thchat-ui
# 安装npm依赖
npm install
# 本地运行
cd thchat-ui
npm run serve
G:\GitHub\Git-Test\THChatUI\thchat-ui>npm run serve

#======= 后端
# 后端环境
# conda env remove --name thchat
# conda create -n thchat python=3.10 -y
# conda activate thchat
# pip install transformers langchain==0.3.14 langchain-community flask flask-cors accelerate langserve fastapi langchain_huggingface
# pip install sse_starlette uvicorn websocket-client pyjwt
# pip install dashscope tavily-python pypdf faiss-gpu faiss-cpu zhipuai
# 后端接口
# 后端链接： http://localhost:8080/chat/stream
conda activate thchat
G:\GitHub\Git-Test\THChatUI>python thchat-server/llm/chat/4_langchain_DeepSeek_chat.py
G:\GitHub\Git-Test\THChatUI>python thchat-server/llm/chat/4_langchain_TongyiQwen_chat.py
