@echo off
echo 正在复制backend目录到ASD_Agent项目...
xcopy /E /I /Y "e:\TencentRecord\xwechat_files\wxid_q3omonsd512m12_8f6b\msg\file\2026-01\backend" "e:\PythonProject\ASD_Agent\backend"
echo.
echo 复制完成！
echo 现在可以将ASD_Agent文件夹拖拽到魔搭创空间部署了。
pause
