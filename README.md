# stargazer
![license-gpl-3.0-only](https://img.shields.io/badge/license-GPL--3.0--only-blue?label=license&link=https%3A%2F%2Fspdx.org%2Flicenses%2FGPL-3.0-only.html)

stargazer is a tool for automating the creation and synchronization of Space Station 14-related pages on the 
[starcup wiki](https://wiki.starcup.cc/).

Example: [Entity:AnomalyLiquid](https://wiki.starcup.cc/w/Entity:AnomalyLiquid)

## Usage
Copy `.env.example` to `.env` and reconfigure it to match your database. stargazer expects a PostgreSQL database, but may be 
easily reconfigured to use any database that [sqlalchemy](https://www.sqlalchemy.org/) supports. See `src/main.py` and 
`alembic/env.py`.

[Database migrations](https://en.wikipedia.org/wiki/Schema_migration) are managed with 
[alembic](https://alembic.sqlalchemy.org/en/latest/). Run the following command to perform the necessary migrations, 
which will automatically create the database schema on the first run.

```commandline
alembic upgrade head
```

### pywikibot
pywikibot, the library which stargazer uses to interface with mediawiki, manages configuration and state on-disk. You
will need to use pywikibot scripts to generate configuration files for your wiki.

Alternative documentation in case of difficulties: https://charlesreid1.com/wiki/Pywikibot

Start by installing pywikibot through pip.
```commandline
python -m pip install pywikibot
```

For this example, we will assume we have a MediaWiki instance at `https://wiki.example.null`, and we'll name it `example`.

```commandline
pwb generate_family_file "https://wiki.example.null" "example"
```

You should now have a file at `families/example_family.py`.

Generate a bot password for your wiki account if you don't have one yet. Name it whatever you want, but we will assume 
the name `stargazer-bot` for this example. You should grant the following 
permissions:
* Edit existing pages
* Create, edit, and move pages
* Upload new files
* Upload, replace, and move files

Now, we'll use the `login.py` script to generate the `user-config.py` file.

```commandline
pwb login
```

Once you have finished configuring your login, you should have a file `user-config.py` which looks something like this:
```
family = 'example'
mylang = 'en'
usernames['example']['en'] = 'My username'
password_file = "user-password.py"
```

... and a file `user-password.py` resembling this:
```
('My username', BotPassword('stargazer-bot', 'MySuperSecretBotPassword'))
```

Blast off 🚀
```commandline
python main.py <path to ss14 codebase directory> <edit summary (e.g. "stargazer: first run")>
```
