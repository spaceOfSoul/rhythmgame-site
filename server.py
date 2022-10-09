from flask import Flask, render_template, request, redirect, url_for, session, abort
# from flask_socketio import SocketIO, join_room, leave_room, emit
from flask_wtf.csrf import CSRFProtect
from pymongo import MongoClient

from dotenv import load_dotenv
import os
import glob

import secrets
from Crypto.Hash import SHA256
import re

load_dotenv()

#앱 초기화
app = Flask(__name__)

#config
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['DEBUG'] = True

#크로스사이트 위조 요청 대비 csrf 토큰 인증
csrf = CSRFProtect(app)
csrf.init_app(app)

#몽고DB 클라이언트
mongo_client = MongoClient(os.environ.get('DB_URL'))

#=========================================================================================
#기타 함수

#=========================================================================================

# home page request
@app.route('/', methods=["GET", "POST"])
def index():
    if request.method == "POST":
        print()
    return render_template("index.html")

# login page request
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == "POST":
        id = request.form.get('id')
        pw = request.form.get('pw')
        
        #mongodb 클라이언트
        member = mongo_client.onlineClass.member
        
        # state = 0 : None
        # state = 1 : 아이디 공란
        # state = 2 : 비번 공란
        # state = 3 : 아이디 비번 불일치
        # state = 4 : 로그인 실패 10번
        # state = 5 : 이미 다른 브라우저에서 로그인함
        
        if id == "":#아이디 공란
            return render_template("login.html",state = 1)
        if pw == "":#비번 공란
            return render_template("login.html",state = 2)
        
        if member.count_documents({"id" : id}): # 아이디 일치
            x=member.find_one({'id':id})
            
            if x['loginFailedCount'] >= 50: # 로그인 실패횟수가 10번을 넘어갈 시
                return render_template("login.html",state = 4)
            
            salt = x['salt']
            hash_obj = SHA256.new()
            hash_obj.update(bytes(pw + salt, 'utf-8'))
            h =hash_obj.hexdigest()
            if x['password'] == h: # 비밀번호가 일치할 시
                
                # 이미 로그인이 되어 있다면
                if x['isLogined'] != 0:
                    return render_template('login.html',state=5)
                
                session['_id'] = {"id" :id, "nickname" : x['name'], 'authentication' : 0}
                member.update_one({'id':id},{"$set":{'loginFailedCount':0}})
                return redirect(url_for('index'))
            else: # 비밀번호가 일치하지 않을 시
                x['loginFailedCount'] += 1 #유저 데이터의 로그인 실패횟수 증가
                member.update_one({'id':id},{"$set":{'loginFailedCount':x['loginFailedCount']}})
                
        #아이디 혹은 비번 불일치
        return render_template("login.html",state = 3)
    
    #로그인 화면 렌더링
    return render_template('login.html',state=0)

# signup page request
@app.route('/signup', methods=['GET','POST'])
def signup():
    if request.method == "POST":
        print()
    return render_template("signup.html")

# my page request
@app.route('/myPage', methods=['GET','POST'])
def myPage():
    if request.method == "POST":
        print()
    return render_template("myPage.html")

# song list page
# parse song-list.txt, and rendering template with list data
@app.route('/song-list',methods = ['Get','POST'])
def song_list():
    lst = []
    with open('static/beatmaps/song-list.txt', 'r') as f:
        lines = f.readlines()
        for line in lines:
            title, artist = line.split(',')
            lst.append([title, artist])
    return render_template('songList.html', lst = lst)

# game page
@app.route('/game/<string:song_name>', methods = ['GET', 'POST'])
def single_game(song_name):
    if request.method == "POST":
        print(song_name)
    
    note_info=[]
    
    stack_leniency = 0 # float
    preview_time = 0 # int
    countdown = 0 # int
    
    artist = ''
    title = ''
    
    
    for i in glob.glob("static/beatmaps/" + song_name + "/*.osu"):
        with open(i, "r") as f:
            lines = f.readlines()
            
            # section 구분
            # section = 1 : General
            # section = 2 : HitObjects
            # scetion = 4 : Metadata
            # section = other : 구별을 주기는 해야할거같아서 넣음.(section 유지한 채로 쭉쭉 밀면 안됨)
            section = 0
            
            for line in lines: # 구역 구별
                if line == '[General]\n':
                    section = 1
                elif line == '[HitObjects]\n':
                    section = 2
                elif line == '[Editor]\n':
                    section = 3
                elif line == '[Metadata]\n':
                    section = 4
                elif line == '[Difficulty]\n':
                    section = 5
                elif line == '[Events]\n':
                    section = 6
                elif line == '[TimingPoints]\n':
                    section = 7
                elif line == '[Colours]\n':
                    section = 8
                else: # 데이터 읽기
                    if section == 1: # General
                        if 'StackLeniency' in line:
                            tmp = line.split(':')
                            stack_leniency = float(tmp[1])
                        elif 'PreviewTime' in line:
                            tmp = line.split(':')
                            preview_time = int(tmp[1])
                        elif 'Countdown' in line:
                            tmp = line.split(':')
                            countdown = int(tmp[1])
                    elif section ==2: # HitObject
                        tmp = line.replace(':',',')
                        tmp = tmp.split(',')
                        note_info.append([int(tmp[0]),int(tmp[2]),int(tmp[5])])
                    elif section == 4: # Metadata
                        if 'Artist' in line:
                            tmp = line.split(':')
                            tmp[1] =  tmp[1].replace('\n','')
                            artist = tmp[1]
                        elif 'TitleUnicode' in line:
                            tmp = line.split(':')
                            tmp[1] =  tmp[1].replace('\n','')
                            title = tmp[1]
    
    data = {"noteInfo" : note_info,
            'stackLeniency' : stack_leniency,
            'previewTime' : preview_time,
            'countdown' : countdown,
            "songName" : title,
            "songWriter" : artist,
            "root":"beatmaps/"+song_name+"/audio.mp3"
            }
    
    return render_template("game.html", data = data)

#-------------------------------------------------------
# testing pages
#-------------------------------------------------------
# @app.route('/test1', methods = ['GET'])
# def test1():
#     lst = []
#     with open('', 'r') as f:
#         lines = f.readlines()
#         for line in lines:
#             title, artist = line.split(',')
#             print('title : ' + title + 'artist'+ artist)
#     return render_template("testPage/fileRead_test.html", lst)

if __name__ == '__main__':
    app.run()