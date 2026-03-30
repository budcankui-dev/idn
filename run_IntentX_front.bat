@echo off
REM 切换到指定目录
cd /d thchat-ui

REM 运行npm serve命令
npm run serve

REM 脚本执行完成后暂停，等待用户按任意键退出
pause