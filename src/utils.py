import re
import sys
from datetime import datetime, timedelta
import os
url_pattern = re.compile(r"http(s)?://([\w\-]+\.)+[\w\-]+(\/[\w\- ./?%&=]*)?")
date_pattern = re.compile("(^\d{4}/\d{2}/\d{2})\([月火水木金土日]\)$")
cancel_pattern = re.compile("^.*がメッセージの送信を取り消しました$")

def read_line(filename):
    with open(filename, "rb") as fp:
        contents_ = fp.readlines()[2::]
    contents = []
    while len(contents_)>0:
        content = contents_.pop(0)
        while content.endswith(b"\r\n")==False:
            content+=contents_.pop(0)
        content = content.decode()
        content = content.replace("\n","")
        if content.strip():
            contents.append(content.strip())

    date = datetime.fromtimestamp(0)
    result = []
    for content in contents:
        date_match = date_pattern.match(content)
        if date_match:
            date = datetime.strptime(date_match.group(1), "%Y/%m/%d")
            continue
        content = content.split("\t")
        if len(content)<3:
            continue #日程調整、電話他
        timestamp = content[0]
        speaker = content[1]
        content = " ".join(content[2:])
        if content[0]=='"' and content[-1]=='"':
            content = content[1:-1]
        for remove in ("[スタンプ]", "[写真]", "[アルバム]", "(null)", "[ノート]", "(emoji)", "[投票]", "メッセージの送信を取り消しました", "[動画]"):
            content = content.replace(remove, "")
        content = cancel_pattern.sub("", content)
        if re.match("^\s*$", content):
            continue
        content = url_pattern.sub("<<<URL>>>", content)
        hour, minute = timestamp.split(":")
        timestamp = date+timedelta(hours=int(hour),minutes=int(minute))
        result.append([timestamp, speaker, content])
    return result
    
def process_line(target_speaker, conv_th=3600, seq_th=120, filename=""):
    contents = read_line(filename)
    with open("{0}_line.txt".format(target_speaker), "a") as fp:
        for i, content in enumerate(contents):
            if i==0:
                continue
            timestamp, speaker, content = content
            if speaker!=target_speaker:
                continue
            
            part1 = ""
            index = i-1
            another_speaker = contents[index][1]
            if another_speaker == target_speaker:
                continue
            before_timestamp = contents[index][0]
            if timestamp-before_timestamp>timedelta(seconds=conv_th): #会話の間隔があきすぎ。別の会話。
                continue
            while index>0 and contents[index][1]==another_speaker and before_timestamp-contents[index][0] < timedelta(seconds=seq_th):
                part1 = contents[index][2] + " " + part1
                index-=1
            
            part2 = ""
            index = i
            while index<len(contents) and contents[index][1]==target_speaker and contents[index][0] - timestamp < timedelta(seconds=seq_th):
                part2 += " " + contents[index][2]
                index+=1
            fp.write(part1+"[SEP]"+part2)
            fp.write("\n")

        



    



if __name__=="__main__":
    for filename in os.listdir("."):
        if "[LINE]" in filename:
            process_line("塚田 恵理", filename=filename)