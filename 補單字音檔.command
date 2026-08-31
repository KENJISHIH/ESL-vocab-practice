#!/bin/bash
# 雙擊就跑：補 ESL 練習網還缺的單字音檔（Gemini Achernar TTS）
# 每日上限 100 次，撞到每日配額自動中止整批；冪等，隔天再雙擊一次就接著補。
cd "$(dirname "$0")" || exit 1

echo "===== 開始補單字音檔（$(date '+%Y-%m-%d %H:%M')）====="
python3 tools/batch_tts.py --all
tts_status=$?

# 有新音檔才 commit + push（只鎖 audio/，不碰其他工作）
# 注意：即使因配額中止（exit 2），已產生的音檔一樣要推上去
if [ -n "$(git status --porcelain audio/)" ]; then
    git add audio/
    git commit -m "audio: daily batch TTS top-up ($(date '+%Y-%m-%d'))"
    git push origin main && echo "✅ 已推上 GitHub Pages"
else
    echo "（這次沒有新增音檔）"
fi

if [ "$tts_status" -eq 2 ]; then
    echo "⛔ 今天配額用完了，已產生的音檔都已保留並推上去；明天再雙擊一次就會接著補。"
fi

remaining=$(python3 tools/export_tts.py | grep "快取無" | grep -oE '[0-9]+' | head -1)
echo "===== 完成，還缺約 ${remaining:-?} 字 ====="
echo "按任意鍵關閉視窗..."
read -n 1
