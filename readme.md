# eggbot

This bot maps user-supplied textures onto a set of pre-defined models, renders them, and posts the result.

Written in discord.py.

## Overview

It has a single command (excluding `$reload` and `$help`):

`$map <shape> <image_data>`

`shape` can be any of the following:
- cone
- teapot
- egg
- torus
- monkey
- pyramid
- icosphere
- jay

The bot will use some logic in trying to read the second argument `image_data`:

- First, it looks for a url that ends with a supported extension. At the moment, these are just `.jpg`, and `.png`.
- Failing that, it looks for a reference to a user, either an ID or a mention (or more; it uses d.py's user command converter)
- Then it looks for an emoji. At the moment it only works with custom emojis; standard Unicode emojis have an associated URL but it's an SVG.
- Finally, if you give the `image_data` argument as `attachment` or `a` it will look for the first attachment in the message that has a `.jpg` or `.png` extension and use that.

## Hosting

I don't have any objections to people hosting this locally, so do as you wish.

The only real thing to note is that the `$reload` command uses my user ID for checking admin rights, so you'll want to change that (in `main.py`). Other than that, the bot looks for a token for a bot account in `token.txt`, so supply one for it there.