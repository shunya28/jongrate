from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class GameMode(models.Model):
    """
    対局モードを表す。
    - name: 「東風戦」「半荘戦」など
    """
    name = models.CharField(max_length=20)


class GameInfo(models.Model):
    """
    対局情報を表す。
    - dt: 対局日時
    - mode: 対局モード
    """
    dt = models.DateTimeField()
    mode = models.ForeignKey(GameMode, on_delete=models.PROTECT)


class Player(models.Model):
    """
    プレイヤー情報を表す。
    - name: プレイヤー名
    """
    name = models.CharField(max_length=20)


class GameResult(models.Model):
    """
    対局結果を表す。
    - game: 対局情報
    - player: プレイヤー
    - score: playerがこの対局で得た点数
    - rank: playerのこの対局における順位
    """
    game = models.ForeignKey(GameInfo, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.PROTECT)
    score = models.IntegerField()
    rank = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
