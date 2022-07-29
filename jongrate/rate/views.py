from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.conf import settings
# from django.utils.timezone import make_aware
import datetime
from pytz import timezone
from rate.models import Player, GameInfo, GameResult, GameMode


class Index(View):
    def get(self, request):
        context = {}
        return render(request, 'rate/index.html', context)


class Data(View):
    def get(self, request):
        player_list = [p.name for p in Player.objects.all()]
        gamemode_list = [g.name for g in GameMode.objects.all()]

        # gr_raw = GameResult.objects.all()
        # gr_list = []
        # for gr in gr_raw:

        #     gr_dict = {
        #         'game_dt': gr.game.dt,
        #     }
        #     gr_list.append(gr_dict)

        gi_raw_list = GameInfo.objects.all().order_by('-dt', '-pk')
        gr_list = []
        for gi in gi_raw_list:
            gr = GameResult.objects.filter(game=gi).order_by('rank')
            gr_dict = {
                'game_dt': gi.dt,
                'game_mode': gi.mode.name,
            }

            for i in range(len(gr)):
                gr_dict[f'rank{i+1}'] = gr[i].player.name + '：' + str(gr[i].score)
            
            gr_list.append(gr_dict)

        context = {
            'player_list': player_list,
            'gm_list': gamemode_list,
            'gr_list': gr_list,
        }
        return render(request, 'rate/data.html', context)

    def post(self, request):

        # 対局情報の保存
        gm = GameMode.objects.get(name=request.POST['gamemode'])
        naive_dt = datetime.datetime.fromisoformat(request.POST['datetime'])
        aware_dt = naive_dt.replace(tzinfo=timezone(settings.TIME_ZONE))
        gi = GameInfo.objects.create(dt=aware_dt, mode=gm)

        # 対局結果の保存
        for i in range(4):
            GameResult.objects.create(
                game=gi,
                player=Player.objects.get(name=request.POST[f'player{i+1}']),
                score=request.POST[f'score{i+1}'],
                rank=request.POST[f'rank{i+1}']
            )

        context = {}
        return redirect(reverse('rate:data'), context)


class Rate(View):
    def get(self, request):
        context = {}
        return render(request, 'rate/rate.html', context)


class Settings(View):
    def get(self, request):
        context = {}
        return render(request, 'rate/settings.html', context)

    def post(self, request):
        new_player = request.POST.get('new-player', False)
        new_gm = request.POST.get('new-gm', False)

        if new_player:
            Player.objects.create(name=new_player)

        if new_gm:
            GameMode.objects.create(name=new_gm)

        context = {}
        return render(request, 'rate/settings.html', context)
