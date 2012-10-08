# Try to rename "README" to "README.txt"
# -> Permission denied
# -> elFinder client sends two additional requests

_=1349287655876
answer=42
cmd=rename
name=README.txt
target=l1_UkVBRE1F

{"error":["errRename","README"],"debug":{"connector":"php","phpver":"5.4.4-7","time":0.028625965118408,"memory":"1543Kb \/ 1515Kb \/ 128M","upload":"","volumes":[{"id":"l1_","name":"localfilesystem","mimeDetect":"internal","imgLib":"gd"}],"mountErrors":[]}}

_=1349287656009
answer=42
cmd=tree
target=l1_Lw

{"tree":[{"mime":"directory","ts":1349277815,"read":1,"write":1,"size":0,"hash":"l1_Lw","volumeid":"l1_","name":"files","locked":1,"dirs":1},{"mime":"directory","ts":1349287043,"read":1,"write":1,"size":0,"hash":"l1_c29tZV9kaXI","name":"some_dir","phash":"l1_Lw"}],"debug":{"connector":"php","phpver":"5.4.4-7","time":0.033825159072876,"memory":"1542Kb \/ 1516Kb \/ 128M","upload":"","volumes":[{"id":"l1_","name":"localfilesystem","mimeDetect":"internal","imgLib":"gd"}],"mountErrors":[]}}

_=1349287656001
answer=42
cmd=open
init=1
target=l1_Lw
tree=1

{"cwd":{"mime":"directory","ts":1349277815,"read":1,"write":1,"size":0,"hash":"l1_Lw","volumeid":"l1_","name":"files","locked":1,"dirs":1},"options":{"path":"files","url":"","tmbUrl":"","disabled":["extract"],"separator":"\/","copyOverwrite":1,"archivers":{"create":["application\/x-tar","application\/x-gzip","application\/x-bzip2","application\/zip","application\/x-rar","application\/x-7z-compressed"],"extract":[]}},"files":[{"mime":"directory","ts":1349277815,"read":1,"write":1,"size":0,"hash":"l1_Lw","volumeid":"l1_","name":"files","locked":1,"dirs":1},{"mime":"directory","ts":1349287043,"read":1,"write":1,"size":0,"hash":"l1_c29tZV9kaXI","name":"some_dir","phash":"l1_Lw"},{"mime":"unknown","ts":1349277814,"read":1,"write":1,"size":252,"hash":"l1_UkVBRE1F","name":"README","phash":"l1_Lw"}],"api":"2.0","uplMaxSize":"2M","netDrivers":["ftp"],"debug":{"connector":"php","phpver":"5.4.4-7","time":0.023961067199707,"memory":"1543Kb \/ 1522Kb \/ 128M","upload":"","volumes":[{"id":"l1_","name":"localfilesystem","mimeDetect":"internal","imgLib":"gd"}],"mountErrors":[]}}

