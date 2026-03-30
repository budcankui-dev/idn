@echo off
REM 切换到指定目录
REM cd /d D:\Github\THChatUI

REM 激活conda环境
call conda activate thchat

REM 运行Python脚本
python thchat-server/llm/chat/4_langchain_TongyiQwen_chat.py

REM 脚本执行完成后暂停，等待用户按任意键退出
pause