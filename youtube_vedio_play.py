   media = instance.media_new(movie)
   media_list = instance.media_list_new([movie]) #A list of one movie

   player = instance.media_player_new()
   player.set_media(media)

   #Create a new MediaListPlayer instance and associate the player and playlist with it

   list_player =  instance.media_list_player_new()
   list_player.set_media_player(player)
   list_player.set_media_list(media_list)