import datetime

from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from .models import Game, Player, Statistic, Score

User = get_user_model()


class BgTrackerTests(TestCase):

    def setUp(self):
        self.user = User.objects.create(username='bob', email='bob@ex.com')
        self.user.set_password('123')
        self.user.save()
        self.client.login(email='bob@ex.com', password='123')
        games = ['a feast for odin', 'terraforming mars', 'too many bones', 'catan',
                 'Through the Ages: A New Story of Civilization']
        self.games = []
        for game in games:
            game = Game.objects.create(game_name=game, image=f'{game}.com')
            game.user_id.add(self.user)
            self.games.append(game)

    def test_game_list(self):
        resp = self.client.get(reverse('game_list'))
        game = Game.objects.create(game_name='eldritch horror', image='eldritch_horror.com')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(list(resp.context['games']), self.games)
        self.assertNotIn(game, list(resp.context['games']))

    def test_game_page(self):
        bob = Player.objects.create(username='bob', user_friend=self.user)
        game = Game.objects.get(game_name='catan')
        Statistic.objects.create(user_id=self.user, game_id=game.id, stats_name='first game',
                                 duration=datetime.time(0, 2, 30),
                                 comments='its fine', winner=bob, game_date=datetime.date(2022, 6, 4))
        Statistic.objects.create(user_id=self.user, game_id=game.id, stats_name='second game',
                                 duration=datetime.time(1, 2, 30),
                                 comments='its fine again', winner=bob, game_date=datetime.date(2020, 6, 4))
        resp = self.client.get(reverse('game_page', kwargs={'game_slug': 'catan'}))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.context['game'], game)
        self.assertEqual(resp.context['game_stat'].count(), 2)

    def test_add_player(self):
        resp = self.client.post(reverse('add_player'), {'username': 'john'})
        self.assertEqual(resp.status_code, 302)
        assert Player.objects.get(username='john')

    def test_players_list(self):
        players_name = ['john', 'helga', 'marie', 'joe']
        players = [Player.objects.create(username=name, user_friend=self.user) for name in players_name[:3]]
        resp = self.client.get(reverse('players_list'))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(players, list(resp.context['players']))

    def test_add_game(self):
        Game.objects.create(game_name='eldritch horror', image='eldritch_horror.com')
        # if game exists for user
        resp = self.client.post(reverse('add_game'), {'game_name': 'terraforming mars'}, follow=True)
        self.assertTemplateUsed(resp, 'bg_tracker/games_list.html')

        # if game exists for DB, not user
        resp = self.client.post(reverse('add_game'), {'game_name': 'eldritch horror'}, follow=True)
        self.assertTemplateUsed(resp, 'bg_tracker/add_game.html')

        # if new game
        resp = self.client.post(reverse('add_game'), {'game_name': 'War of the Ring: Second Edition '}, follow=True)
        self.assertTemplateUsed(resp, 'bg_tracker/game_list.html')

        # if game_name incorrect
        resp = self.client.post(reverse('add_game'), {'game_name': 'asdasqw'}, follow=True)
        messages = [m.message for m in get_messages(resp.wsgi_request)]
        self.assertTemplateUsed(resp, 'bg_tracker/add_game.html')
        self.assertIn('The name of the game is incorrect or the game does not exist', messages)

    def test_add_stats(self):
        bob = Player.objects.create(username='bob', user_friend=self.user)
        john = Player.objects.create(username='john', user_friend=self.user)
        resp = self.client.post(reverse('add_stats', kwargs={'game_slug': 'catan'}),
                                {'stats_name': 'first game', 'duration': '00:02:30', 'comments': 'its fine',
                                 'winner': '1', 'players': ['1', '2'], 'game_date': '2022-06-04'},
                                follow=True
                                )
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'bg_tracker/add_score.html')
        assert Statistic.objects.last()
        last_stat = Statistic.objects.last()
        self.assertEqual(last_stat.winner, bob)
        self.assertEqual(list(last_stat.players.all()), [bob, john])
        self.assertEqual(last_stat.stats_name, 'first game')
        self.assertEqual(last_stat.game_date, datetime.date(2022, 6, 4))
        self.assertEqual(last_stat.comments, 'its fine')
        self.assertEqual(last_stat.duration, datetime.time(0, 2, 30))

    def test_add_score(self):
        Player.objects.create(username='bob', user_friend=self.user)
        Player.objects.create(username='john', user_friend=self.user)
        self.client.post(reverse('add_stats', kwargs={'game_slug': 'catan'}),
                         {'stats_name': 'first game', 'duration': '00:02:30', 'comments': 'its fine',
                          'winner': '1', 'players': ['1', '2'], 'game_date': '2022-06-04'},
                         follow=True
                         )
        last_stat = Statistic.objects.last()

        resp_get = self.client.get(reverse('add_score', kwargs={'game_slug': 'catan', 'stat_id': last_stat.id}))
        self.assertEqual(resp_get.context['form'].total_form_count(), 2)

        data = {'form-TOTAL_FORMS': '2',
                'form-INITIAL_FORMS': '0',
                'form-MIN_NUM_FORMS': '0',
                'form-MAX_NUM_FORMS': '1000',
                'form-0-player': '1',
                'form-0-score': '13',
                'form-0-id': '',
                'form-1-player': '2',
                'form-1-score': '21',
                'form-1-id': '', }

        resp_post = self.client.post(reverse('add_score', kwargs={'game_slug': 'catan', 'stat_id': last_stat.id}),
                                     data, follow=True)
        self.assertEqual(resp_post.status_code, 200)
        self.assertTemplateUsed(resp_post, 'bg_tracker/game_page.html')
        assert Score.objects.all()
        scores = Score.objects.filter(stats=last_stat)
        self.assertQuerysetEqual(scores, Statistic.objects.last().score_set.all(), ordered=False)
        self.assertEqual(scores[0].player.username, 'bob')
        self.assertEqual(scores[1].player.username, 'john')
        self.assertEqual(scores[0].score, 13)
        self.assertEqual(scores[1].score, 21)

    def test_game_stat_page(self):
        game = Game.objects.get(game_name='catan')
        bob = Player.objects.create(username='bob', user_friend=self.user)
        john = Player.objects.create(username='john', user_friend=self.user)
        stat = Statistic.objects.create(user_id=self.user, game_id=game.id, stats_name='first game',
                                        duration=datetime.time(0, 2, 30),
                                        comments='its fine', winner=bob, game_date=datetime.date(2022, 6, 4))
        score_0 = Score.objects.create(player=bob, score=14, stats=stat)
        score_1 = Score.objects.create(player=john, score=66, stats=stat)
        stat.score_set.add(score_0, score_1)

        resp = self.client.get(reverse('game_stat', kwargs={'game_slug': game.slug, 'stat_id': stat.id}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'bg_tracker/game_stat.html')
        self.assertEqual(resp.context['game_stat'], stat)
        self.assertEqual(list(resp.context['scores']), [score_0, score_1])

        # test for delete stat
        resp = self.client.post(reverse('game_stat', kwargs={'game_slug': game.slug, 'stat_id': stat.id}),
                                {'stat_id': stat.id}, follow=True)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'bg_tracker/game_page.html')
        self.assertFalse(Statistic.objects.filter(id=stat.id))

    def test_overall_game_stat(self):
        Player.objects.create(username='bob', user_friend=self.user)
        resp = self.client.get(reverse('overall_game_stats', kwargs={'game_slug': 'catan'}))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'bg_tracker/overall_game_stat.html')
