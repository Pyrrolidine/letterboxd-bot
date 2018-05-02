# Letterboxd Bot

This is a [Discord](https://discordapp.com/) bot for [Letterboxd](https://letterboxd.com/) requests such as getting the page of a film, crew person, user or review.

## Commands

**!helplb**

Display the commands with descriptions.

**!film/!movie**

Search a film on Letterboxd and returns an embed link with informations.

**!director/!actor**

Search the specified person and returns an embed link with informations.

**!user**

Returns an embed link to the Letterboxd member profile, displaying their featured favourites, location and number of films watched.

**!review**

Returns the review or a list of reviews from the specified user and film.  
Example: !review porkepik story floating weeds  
Gets Porkepik's review of A Story of Floating Weeds (1934)

**!checklb**

Checks if Letterboxd.com is down.

**!del**

Deletes the last message by the bot inside the channel. The bot needs the "manage messages" permission for this command to work.

## To-Do

Master branch:  
- [x] Make !review embed, displaying the date of the review and the rating, if one there is, instead of having only the first review embed.

Experimental branch:  
- [ ] Switch file history system to a database.
