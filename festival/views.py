from django.shortcuts import render , redirect
from django.db import connection, transaction
from common.models import Booth, Boothstamp, Contestparticipant, AuthUser, Contestvote
from common import utils
from django.http import JsonResponse
from datetime import datetime

def main(req):
	return render(req, 'festival/festival_main.html')

def my_custom_sql(self):
	with connection.cursor() as cursor:
		cursor.execute("UPDATE bar SET FOO = 1 WHERE baz = %s", [self.baz])
		cursor.execute("SELECT foo FROM bar WHERE baz= %s", [self.baz])
		row = cursor.fetchone()
	return row

def foodtruck (req):
	return render(req, 'festival/foodtruck.html')

def festmap (req):
	return render(req, 'festival/festmap.html')

def stamp (req):
	query = ""
	if req.user.is_authenticated:
		# 회원일 경우 회원 정보 포함
		query = "select B.booth_id , B.booth_nm , BS.stmp_count from Booth as B join (select count(1) as stmp_count from BoothStamp where bt_account_id = " + str(req.user.id) + ") as BS;"
	else :
		# 회원이 아닌 경우 부스 정보만 출력
		query = "select booth_id , booth_nm from Booth;"

	with connection.cursor() as cursor:
		cursor.execute(query)
		rows = cursor.fetchall()
	
	expanded_rows = []
	expanded_rows = utils.query_expand(rows , cursor)

	return render(req, 'festival/stamp.html',{
		'data' : expanded_rows
	})

def stamp_data (req):
    with connection.cursor() as cursor:
        cursor.execute("select * from BoothStamp;")
        rows = cursor.fetchall()
    
    expanded_rows = []
    expanded_rows = utils.query_expand(rows , cursor)
    
    result_list = {'result': 1, 'data': expanded_rows}
    return JsonResponse(result_list, json_dumps_params={'ensure_ascii': False})


def stamp_visit(req):
	return render(req , 'festival/stamp.visit.html')

def stamp_visit_detail(req , pk):
	if not req.user.is_authenticated :
		return render(req , 'festival/stamp.visit.detail.html' , { 
			'mesg' : '로그인이 필요합니다!<br/>메뉴에서 간편 로그인을 해주세요'
		})

	stamp_history = Boothstamp.objects.filter(bt_account_id=req.user.id , booth_id=pk)
	if(stamp_history):
		return render(req , 'festival/stamp.visit.detail.html' , { 
			'mesg' : '이미 방문한 부스입니다<br/>참여해주셔서 감사합니다!'
		})

	current_referer = req.META.get('HTTP_REFERER')
	isQr = req.GET.get('isQr')
	if not isQr :
		isQr = 0
	else :
		isQr = 1
	
	booth = Booth.objects.get(booth_id=pk)
	new_stamp = Boothstamp(bt_account_id = req.user.id , booth_id=pk, created_dt = datetime.now(), bt_referer_url=current_referer,bt_is_qr=isQr)
	new_stamp.save()
	return render(req , 'festival/stamp.visit.detail.html' , { 
		'booth' : booth,
		'mesg' : '참여해주셔서 감사합니다!'
	})

# 투표
def talent_select(req):
	if req.user.is_authenticated :
		cur_vote = Contestvote.objects.filter(cv_account_id=req.user.id , is_main=1)
		if cur_vote :
			return redirect('talent')

	cp_vote = Contestvote.objects.all()
	contestparticipant=Contestparticipant.objects.all().order_by('cont_participant_order')
	
	return render(req, 'festival/talent.html', 
	{
		'cp' : contestparticipant,
		'is_main' : 1
	})

# 투표 결과 나타내는 함수
def talent (req):
	return render(req, 'festival/talent_contest.html',
	{
		'is_main' : 1
	})

## 특별상 투표 관련

## 투표 
def talent_spe_vote(req):
	if req.user.is_authenticated :
		cur_vote = Contestvote.objects.filter(cv_account_id=req.user.id , is_main=0)
		if cur_vote :
			return redirect('talent_spe_result')

	cp_vote = Contestvote.objects.all()
	contestparticipant=Contestparticipant.objects.all().order_by('cont_participant_order')
	
	return render(req, 'festival/talent.html', 
	{
		'cp' : contestparticipant,
		'is_main' : 0
	})

## 결과
def talent_spe_result(req):
	return render(req, 'festival/talent_contest.html',{
		'is_main' : 0
	})


def cheer(req):
	return render(req, 'festival/cheer_contest.html')

def popup1(req):
	return render(req, 'festival/foodtruck1.html')

def signin(req) :
	return render(req , 'festival/auth/signin.html')

def signup(req) :
	return render(req , 'festival/auth/signup.html')

def signout(req) : 
	print("signout")

