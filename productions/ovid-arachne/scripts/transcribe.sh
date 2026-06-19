#!/usr/bin/env bash
# Whisper word-timestamp transcription of the downsampled Book-3 audio.
# Reads OPENAI_API_KEY from recursive-eco/apps/flow/.env.local (never printed).
# Usage: bash transcribe.sh /tmp/ovid/whisper.mp3 /tmp/ovid/whisper.json
set -e
IN="${1:-/tmp/ovid/whisper.mp3}"
OUT="${2:-/tmp/ovid/whisper.json}"
ENVF="C:/Users/ferna/OneDrive/Documentos/GitHub/recursive-eco/apps/flow/.env.local"
KEY=$(grep -E '^OPENAI_API_KEY=' "$ENVF" | head -1 | cut -d= -f2- | tr -d '"' | tr -d "'" | tr -d '\r' | xargs)
[ -z "$KEY" ] && { echo "no OPENAI_API_KEY"; exit 1; }
echo "transcribing $IN (Whisper word timestamps)..."
curl -s https://api.openai.com/v1/audio/transcriptions \
  -H "Authorization: Bearer $KEY" \
  -F file=@"$IN" \
  -F model=whisper-1 \
  -F response_format=verbose_json \
  -F "timestamp_granularities[]=word" > "$OUT"
python -c "import json,sys;d=json.load(open('$OUT',encoding='utf-8'));print('OK words:',len(d.get('words',[])),'| duration:',round(d.get('duration',0),1),'s') if 'words' in d else print('ERROR:',str(d)[:300])"
