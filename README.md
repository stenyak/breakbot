Breakbot
========

Description
-----------

Breakbot is a software that serves as gateway between several communication protocols.

It was started as a way to scratch one of the author's own itch, i.e. to **break** free from the walled garden that WhatsApp is, and to be able to use a proper computer with a proper screen and a proper keyboard (I hate long chats in tiny screens).

It currently supports:

 * WhatsApp group chats <-> IRC rooms gatewaying.
 * WhatsApp phone numbers <-> IRC nick conversion.
 * WhastApp image and video attachments.
 * Private messaging

Things it does **not** currently support:

 * DCC send, topic changes, etc.
 * Other protocols such as XMPP or ICQ.

### Contributing

Contact info is at the bottom of this document.

### Disclaimer

Breakbot is in early stages, lacks documentation everywhere, needs refactoring, may set fire to your computer, take your jobs... the usual drill. Just don't blame me for any problem it causes.


Getting started
---------------

### Requisites

You'll need a WhatsApp account (phone number + password) that Breakbot will use.

Note that WhatsApp does **not** allow simultaneous connections, so you may want to get a secondary phone number for your Breakbot (e.g.: buy a second SIM card, or get a free number at [fonyou](http://www.fonyou.es), etc). Otherwise the bot would log you out of your phone's WhatsApp client.

You can register a WhatsApp account for your number without an actual physical phone, by following step #4 in the list below.

### Configuration

Note: all phone numbers must be specified as `international number` without `00` or `+`. *E.g: Spanish number `600600600` would become `34600600600`*

Steps:

1. Clone the Breakbot repo.
2. Get the dependencies installed by running `./get_libs.sh`.
3. Add your bots to whatever WhatsApp group chats you want to bridge.
4. [optional] Register the phone number against WhatsApp account using the last two options of `python Yowsup/yowsup-cli -h`.
5. Initial setup: open `config.json`, go to `config` section, and customize all the fields.
 * `wa_password` is the base64-encoded password as returned by the `--exists` option of [yowsup-cli](https://github.com/tgalal/yowsup/wiki/yowsup-cli)
 * `wa_phone` is the phone number used by the bot to connect to WhatsApp. See `Requisites` above.
 * `irc_*` parameters are what you expect.
 * `bot_owner_nick` is the IRC nick of the bot owner (needed for private messaging).
6. Make sure your bot nick and phone are also in the contact list.
7. Run `python bot.py` so that it connects to WhatsApp
 * Watch the screen for strings matching `NNN-NNN@g.us`. Those are the WhastApp group chats. Write them down somewhere.
 * Control+C to stop Breakbot.
8. Final setup: open `config.json`, go to `contacts` section, and:
 * Add the desired WhatsApp **group chats** you wrote down to that list, together with the **IRC rooms** you want them bridged to.
 * Add the **phone numbers** and what **IRC nick** they map to.

### Running

Just cross your fingers, run `python bot.py` and wait for your bot to appear at the specified IRC channels (should take about 5-10 seconds with a proper connection).

Once connected, everything you say on IRC should appear on WhastApp and vice versa.

Contact
------

You can notify me about problems and feature requests at the [issue tracker](https://github.com/stenyak/breakbot/issues)

Feel free to hack the code and send me GitHub pull requests, or traditional patches too; I'll be more than happy to merge them.

The author Bruno Gonzalez can be reached at [stenyak@stenyak.com](mailto:stenyak@stenyak.com) and `/dev/null` for personal praise and insults, respectively.

