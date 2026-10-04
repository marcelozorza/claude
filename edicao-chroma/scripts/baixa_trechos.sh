#!/bin/bash
cd "${VIDEO_DIR:-./trabalho}"
while read id name; do
  [ -f clips/${name}_c3.mp4 ] && continue
  for try in 1 2 3; do curl -sSL -o eps/$name.mp4 "https://drive.usercontent.google.com/download?id=$id&export=download&confirm=t" && break; sleep 3; done
  d=$(~/bin/ffmpeg -nostdin -i eps/$name.mp4 2>&1 | grep -oP 'Duration: \K[0-9:.]+' | awk -F: '{print $1*3600+$2*60+$3}')
  i=1; for f in 0.18 0.42 0.68; do
    s=$(echo "$d*$f" | bc)
    ~/bin/ffmpeg -nostdin -loglevel error -y -ss $s -i eps/$name.mp4 -t 3 -an -vf "scale=540:960:force_original_aspect_ratio=increase,crop=540:960,fps=30" -c:v libx264 -crf 20 -preset fast clips/${name}_c$i.mp4
    ~/bin/ffmpeg -nostdin -loglevel error -y -ss $(echo "$s+1" | bc) -i eps/$name.mp4 -frames:v 1 -vf "scale=540:960:force_original_aspect_ratio=increase,crop=540:960" clips/${name}_c$i.jpg
    i=$((i+1)); done
  echo "$name $d" >> eps/done.txt
  rm -f eps/$name.mp4
done < eps/list.txt
echo FIM >> eps/done.txt
