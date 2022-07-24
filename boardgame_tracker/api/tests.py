import json
import datetime

from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from api.serializers import PlayerSerializer, GameSerializer, StatsSerializer
from bg_tracker.models import Player, Game, Statistic, Score

User = get_user_model()


class PlayerAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username='bob', email='bob@ex.com')
        self.user_2 = User.objects.create(username='joe', email='joe@ex.com')
        self.client.force_login(self.user)
        Player.objects.create(username='marie', user_friend=self.user)
        Player.objects.create(username='helga', user_friend=self.user_2)

    def test_get(self):
        response = self.client.get(reverse('players'))
        serializer_data = PlayerSerializer(Player.objects.filter(user_friend=self.user), many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_post(self):
        data = {'username': 'john'}
        json_data = json.dumps(data)
        response = self.client.post(reverse('players'), data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(Player.objects.filter(user_friend=self.user).count(), 2)
        self.assertEqual(Player.objects.last().user_friend, self.user)


class GameAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username='bob', email='bob@ex.com')
        self.user_2 = User.objects.create(username='joe', email='joe@ex.com')
        self.client.force_login(self.user)

        games = ['a feast for odin', 'terraforming mars', 'too many bones', 'catan',
                 'Through the Ages: A New Story of Civilization']
        for game in games[:-1]:
            game = Game.objects.create(game_name=game, image=f'{game}.com')
            game.user_id.add(self.user)

        game = Game.objects.create(game_name=games[-1], image=f'{games[-1]}.com')
        game.user_id.add(self.user_2)

    def test_list(self):
        user_games = self.user.game_set.all()
        response = self.client.get(reverse('game-list'))
        serializer_data = GameSerializer(user_games, many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_create(self):
        url = reverse('game-list')

        # if game exists for user
        response = self.client.post(url, data=json.dumps({'game_name': 'catan', 'image': 'https://catan.com'}),
                                    content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(self.user.game_set.all().count(), 4)

        # if game exists for DB, not user
        response = self.client.post(url, data=json.dumps(
            {'game_name': 'Through the Ages: A New Story of Civilization',
             'image': 'https://tta.com'}), content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(self.user.game_set.count(), 5)

        # if new game
        response = self.client.post(url, data=json.dumps(
            {'game_name': 'Arkham Horror',
             'image': 'https://ah.com'}), content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(self.user.game_set.count(), 6)
        self.assertEqual(Game.objects.count(), 6)

    def test_destroy(self):
        url = reverse('game-detail', kwargs={'slug': 'catan'})
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(self.user.game_set.count(), 3)

    def test_retrieve(self):
        expected_data = {
            "id": 4,
            "game_name": "catan",
            "url": "/game/catan",
            "image": "catan.com",
            "game_stats": []
        }
        url = reverse('game-detail', kwargs={'slug': 'catan'})
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data, expected_data)


class StatsAPIViewTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username='bob', email='bob@ex.com')
        self.user_2 = User.objects.create(username='joe', email='joe@ex.com')
        self.client.force_login(self.user)

        game = Game.objects.create(game_name='catan', image=f'catan.com')
        game.user_id.add(self.user)
        game.user_id.add(self.user_2)

        bob = Player.objects.create(username='bob', user_friend=self.user)
        john = Player.objects.create(username='john', user_friend=self.user)

        Statistic.objects.create(user_id=self.user, game_id=game.id,
                                 stats_name='first game',
                                 duration=datetime.time(0, 2, 30),
                                 comments='its fine', winner=bob,
                                 game_date=datetime.date(2022, 6, 4))
        Statistic.objects.create(user_id=self.user, game_id=game.id,
                                 stats_name='second game',
                                 duration=datetime.time(1, 2, 30),
                                 comments='its fine again', winner=john,
                                 game_date=datetime.date(2020, 6, 4))

    def test_create(self):
        url = reverse('stats-list', kwargs={'game_slug': 'catan'})
        data = {
            'stats_name': 'First stat',
            'game_date': f'{datetime.date(2022, 6, 4)}',
            'duration': f'{datetime.time(1, 2, 30)}',
            'comments': 'fine',
            'winner': {'username': 'bob'},
            'players': [{'username': 'bob'}, {'username': 'john'}]
        }
        json_data = json.dumps(data)

        response = self.client.post(url, data=json_data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(Statistic.objects.count(), 3)
        self.assertEqual(Statistic.objects.last().user_id, self.user)

    def test_list(self):
        url = reverse('stats-list', kwargs={'game_slug': 'catan'})
        response = self.client.get(url)
        serializer_data = StatsSerializer(Statistic.objects.all(), many=True).data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_retrieve(self):
        url = reverse('stats-detail', kwargs={'game_slug': 'catan', 'pk': 1})
        serializer_data = StatsSerializer(Statistic.objects.get(pk=1)).data
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(serializer_data, response.data)

    def test_destroy(self):
        url = reverse('stats-detail', kwargs={'game_slug': 'catan', 'pk': 1})
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)
        self.assertEqual(Statistic.objects.count(), 1)

    def test_retrieve_now_owner(self):
        self.client.force_login(self.user_2)
        url = reverse('stats-detail', kwargs={'game_slug': 'catan', 'pk': 1})
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    def test_destroy_now_owner(self):
        self.client.force_login(self.user_2)
        url = reverse('stats-detail', kwargs={'game_slug': 'catan', 'pk': 1})
        response = self.client.delete(url)
        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)
        self.assertEqual(Statistic.objects.count(), 2)


class ScoreAPITestcase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(username='bob', email='bob@ex.com')
        self.client.force_login(self.user)

        game = Game.objects.create(game_name='catan', image=f'catan.com')
        game.user_id.add(self.user)

        bob = Player.objects.create(username='bob', user_friend=self.user)
        john = Player.objects.create(username='john', user_friend=self.user)

        self.stat = Statistic.objects.create(user_id=self.user, game_id=game.id,
                                             stats_name='first game',
                                             duration=datetime.time(0, 2, 30),
                                             comments='its fine', winner=bob,
                                             game_date=datetime.date(2022, 6, 4))
        self.stat.players.add(bob)
        self.stat.players.add(john)

    def test_create(self):
        url = reverse('score', kwargs={'game_slug': 'catan', 'pk': 1})
        data = json.dumps({
            'stats_id': 1,
            'player': 1,
            'score': 30
        })

        data_2 = json.dumps({
            'stats_id': 1,
            'player': 2,
            'score': 44
        })

        response = self.client.post(url, data=data, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(Score.objects.count(), 1)
        response_2 = self.client.post(url, data=data_2, content_type='application/json')
        self.assertEqual(status.HTTP_201_CREATED, response_2.status_code)
        self.assertEqual(Score.objects.count(), 2)
        self.assertEqual(Score.objects.filter(stats=self.stat).count(), 2)
