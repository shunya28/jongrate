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
                gr_dict[f'rank{i+1}'] = gr[i].player.name + \
                    '：' + str(gr[i].score)

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

        rate_list = self.mori_calc_rate()
        graph_data = {}
        context = {
            'graph_data': graph_data
        }
        return render(request, 'rate/rate.html', context)

    def mori_calc_rate(self):

        player_list = [p.name for p in Player.objects.all()]

        # 順位表の初期化
        # 順位表は2次元配列で、各行が各プレイヤーの順位履歴に対応する
        # 行のインデックスとplayer_listのインデックスは対応する
        rank_list = []
        for _ in range(len(player_list)):
            rank_list.append([])

        info_list = GameInfo.objects.all().order_by('dt', 'pk')
        for info in info_list:

            # ある対局での4人の対局結果情報を取得する
            res_list = GameResult.objects.filter(game=info)

            # player_listをres_listの名前と順に照らし合わせ、対局の参加者を探す
            # 参加した人のところには順位を、参加していない人のところには0を
            # 順位表に追加する
            for p_idx in range(len(player_list)):
                did_name_match = False
                for res_idx in range(len(res_list)):
                    if player_list[p_idx] == res_list[res_idx].player.name:
                        rank_list[p_idx].append(res_list[res_idx].rank)
                        did_name_match = True
                        break

                if not did_name_match:
                    rank_list[p_idx].append(0)

        # レート表の初期化。構造は順位表と同じ
        # レートの初期値は1000
        rate_list = [[1000]] * len(player_list)

        for game_num in range(len(rank_list[0])):

            for p1 in range(len(player_list)):

                # この局(game_num)に参加していないプレイヤーのレートは変動しない
                if rank_list[p1][game_num] == 0:
                    rank_list[p1].append(rank_list[p1][game_num])
                    continue

                # 上の処理を全員に対して行うためにわざと1回多くループを回してる
                # このbreakが無いと、下のforで配列外参照が起きる
                if p1 == (len(player_list) - 1):
                    break

                for p2 in range(p1 + 1, len(player_list)):

                    if rank_list[p2][game_num] == 0:
                        continue

                    p1_rate = rate_list[p1][-1]
                    p2_rate = rate_list[p2][-1]

                    w = p2_rate / p1_rate
                    w = 2 if w > 2 else w
                    w = 0.5 if w < 0.5 else w

                    new_p1_rate = p1_rate + int(30 * w)
                    new_p2_rate = p2_rate - int(30 * w)

                    if rank_list[p1][game_num] < rank_list[p2][game_num]:
                        new_p1_rate = p1_rate - int(30 * w)
                        new_p2_rate = p2_rate + int(30 * w)

                    rate_list[p1].append(new_p1_rate)
                    rate_list[p2].append(new_p2_rate)

        return rate_list


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
