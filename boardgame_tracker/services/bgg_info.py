from libbgg.apiv1 import BGG


def get_bgg_info(game_name):
    # Search for a game by its name in the BGG database and extract game poster.
    conn = BGG()
    game_name = conn.search(game_name.lower(), exact=True)
    game_id = game_name['boardgames']['boardgame']['objectid']
    game_img = conn.get_game(game_id)['boardgames']['boardgame']['image']['TEXT']
    return game_img
