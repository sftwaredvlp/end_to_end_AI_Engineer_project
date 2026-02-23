#!/bin/bash
# Chat API'yi denemek için:
#   ./test_chat.sh
#   ./test_chat.sh "mesajın"

MESSAGE="${*:-calisma1/merhaba.txt dosyasını oku}"
URL="http://127.0.0.1:8000/api/chat/"

BODY=$(echo "$MESSAGE" | python3 -c "import json,sys; print(json.dumps({'message': sys.stdin.read().strip()}))")
echo "Gönderilen: $MESSAGE"
echo "---"
curl -s -X POST "$URL" -H "Content-Type: application/json" -d "$BODY"
echo ""
