[[_TOC_]]

# Documentation destinée au développeur

L'application `flaskrpg` propose un mini-blog. Elle sert de tutoriel
pour la mise en œuvre de PostgreSQL, SQLAlchemy, Python et Flask pour
fabriquer une application Web.

## Documentation

*   [`README-ADMIN.md`](README-ADMIN.md) (markdown) -- Les instructions
    permettant d'utiliser l'application `flaskrpg` : création de la base
    de données de développement et de la base de données de test,
    création de l'environnement virtuel, commandes pour tester et
    développer l'application en direct, configuration pour déployer
    l'application dans un serveur Web (Apache), commandes pour effectuer
    les tests.

*   le présent fichier -- Documentation destinée au développeur.

> La pluparart des blocs de texte présentés comme le présent bloc font
> références à des documentations, cours ou tutoriel externes (ou plus
> généralement à des connaissances censées être acquises par ailleurs).

> Mais il y a aussi de blocs «Todo» indiquant des améliorations ou des
> corrections à faire dans l'application.

## Base de données

Les données sont stockées dans une base PostgreSQL. Le modèle des
données est décrit par le fichier `sql/schema-postgresql.sql`. Il repose
sur trois tables: `user` (les utilisateurs), `post` (les articles du
blog) et `star` (les étoiles).

Note: dans ce fichier SQL, le mot clé `user` ayant un usage spécial dans
PostgreSQL, on doit utiliser (`"user"`) lorsqu'on désigne la table.

Il y a une association de type 1:N de `user` vers `post` qui permet
d'identifier l'auteur de chaque article.

Il y a une association de type N:M entre `user` et `post` via la table
intermédiaire `star` pour savoir à quel article un auteur a accordé une
étoile. **Règles de gestion**: un auteur donne ou non une étoile à un
article, un auteur ne peut pas accorder d'étoile à ses propres articles.

## Le code de l'application Flask `flaskrpg`

L'application Flask `flaskrpg` est codée dans le répertoire `flaskrpg`.

Le fichier `flaskrpg/__init__.py` décrit la création et l'initialisation
de l'application. La configuration se fait par lecture d'un fichier dont
le nom est donnée par la variable d'environnement `FLASKRPG_SETTINGS` et
placé dans les répertoires `instance`.

Exemple pour lancer l'application en lisant le fichier de configuration
`instance/development.py`:

```bash
% FLASKRPG_SETTINGS=development.py flask --help
```

Un fichier de configuration définit (au moins) les constantes suivantes:

- `TRACE` (booléen) pour activer de traces d'activités (pour déboguer
  par exemple).
  
- `TRACE_MAPPING` (booléen) pour tracer en particulier l'automapping
  entre la base de données et les classes Python.
  
- `SECRET_KEY` (chaîne de caractères) sert à chiffrer les données de
  session (d'authentification par exemple) envoyées au navigateur pour
  qu'il puisse les renvoyer ensuite. Lors de la mise en exploitation,
  cette chaîne peut être choisie aléatoirement et doit être conservée
  secrète.
  
- `SQLALCHEMY_ENGINE_ECHO` (booléen) permet de tracer les requêtes SQL
  envoyées par l'application.
  
- `SQLALCHEMY_DATABASE_URI` (url) l'url de connexion à la base de
  données PostgreSQL.

Il y a actuellement deux fichiers de configuration: l'un
(`instance/development.py`) destiné au développement et le second
(`instance/test.py`) destiné aux tests automatisées.

Après la lecture du fichier de configuration, l'initialisation continue
par l'import du fichier `flaskrpg/db.py` qui assure la liaison avec la
base de données (voir description plus loin).

Ensuite vient le chargement de l'interface Web décrite par des routes
codées dans différents `blueprints` (c'est du vocabulaire Flask). Pour
obtenir la liste des routes définies par l'application:

```bash
% FLASKRPG_SETTINGS=development.py flask routes
Endpoint       Methods    Rule
-------------  ---------  --------------------------
auth.avatar    GET        /auth/avatar/<int:user_id>
auth.login     GET, POST  /auth/login
auth.logout    GET        /auth/logout
auth.register  GET, POST  /auth/register
blog.create    GET, POST  /blog/create
blog.delete    POST       /blog/<int:id>/delete
blog.index     GET        /blog/
blog.update    GET, POST  /blog/<int:id>/update
blog.vote      POST       /blog/<int:id>/voteup
root           GET        /
static         GET        /static/<path:filename>
```

La route racine `root` (dont l'url est `/`) n'est en fait qu'une
redirection vers la route `blog.index` (dont l'url est `/blog/`) . La
route `static` (dont le préfixe est `/static/`) est créée
automatiquement par Flask pour permettre l'accès aux fichiers statiques
du répertoire `flaskrpg/static`.

Les autres routes sont codées dans des blueprints. Elles concernent soit
l'authentification et la création des utilisateurs (dans le blueprint
`flaskrpg/auth.py` dont le préfixe des url est `/auth`) soit la gestion
des articles du blog (dans le blueprint `flaskrpg/blog.py` dont le
préfixe des url est `/blog`).

Dans l'application `flaskrpg`, toutes les routes qui modifient les
données de la base passent par une requête HTTP de type `POST` alors que
toutes les routes qui ne font que de la consultation des données
utilisent le type `GET`.

> Note: pour éviter des modifications accidentelles, un navigateur
> prévient l'utilisateur et demande son autorisation avant de recharger
> une page obtenue par `POST`.

> Notez aussi que l'url associée à une route n'est utile que lors de la
> définition de cette route. **Partout ailleurs**, quand on veut faire
> référence à cette route, il **faut** utiliser la fonction Flask
> `url_for()` auquel on passe un nom qui représente le nom de la
> fonction codant cette route afin de retrouver le bon url !

## Le lien avec la base de données (`flaskrpg/db.py`)

Le rôle principal du module `flaskrpg/db.py` est d'établir le lien entre
la base de données et l'application Flask (via SQLAlchemy).

Du point de vue du reste de l'application, ce module expose:

- la fonction `init_app()` pour établir le lien entre l'application et
  la base,

- les trois classes `User`, `Post` et `Star`,

- l'objet `db_session` qui permet d'interroger la base (en créant une
  nouvelle session à chaque nouvelle requête Web traitée).

La fonction interne `connect_db()` reçoit l'application Flask comme
paramètre afin d'en récupérer les paramètres de configuration. C'est
elle qui établit la correspondance entre les classes Python `User`,
`Post` et `Star` et les tables SQL `user`, `post` et `star`. Ces classes
sont déclarées de manière interne à la fonction est ce n'est qu'une fois
le mapping effectuée qu'on les recopie en tant que classes globales. Il
en est de même de l'objet `db_session`.

Dans cette fonction, la mise en correspondance (le _mapping_) entre
classes et tables utilisent l'automapper de SQLAlchemy pour découvrir
automatiquement les tables, leurs attributs et leurs associations. Si la
base évolue, les seuls paramètres à adapter sont le dictionnaire
`model_map` (qui met en correpondances les noms de table et les noms de
classe que l'on souhaite utiliser) et le dictionnaire `relation_map`
(qui permet de customiser le nom d'attribut donné à chaque association
découverte entre classes). Le paramètre de configuration `TRACE_MAPPING`
permet de tracer cette mise en correspondance.

> Tout cela est expliquée en détail dans le module de cours BDD (base de
> données).

### Commande de vérification de la connexion à la base

La fonction `check_db_command` permet de créer un nouvelle commande
Flask lors du lancement (via le décorateur `@click.command`):
`check-db`. Son but est de vérifier que le mapping se déroule
correctement. On pourrait y ajouter des actions de vérifications de
l'intégrité du contenu de la base. Cette nouvelle commande s'utilise
lors du lancement de l'application:

```bash
% FLASKRPG_SETTINGS=development.py flask check-db
```

Si tout se passe bien, elle n'affiche rien (à moins que `TRACE_MAPPING`
soit positionné à `True`).

### Comment utiliser ce module dans les autres modules

Il faut importer les classes nécessaires (qui ne seront utilisables que
lorsque la connexion avec PostgreSQL a été établi donc lorsque
l'application Flask aura été initialisée):

```python
from flaskrpg.db import User, Post, Star, db_session
```

> Note: une bonne pratique consiste à n'importer que ce qu'on utilise
> réellement.

## Les routes (les `blueprint`)

### Les routes concernant l'authentification et la création des utilisateurs (`flaskrpg/auth.py`)

Dans le fichier `flaskrpg/auth.py`, on trouve quelques fonctions
utilitaires et des routes (elles sont préfixées par le décorateur
`@bp.route`). Ces routes utilisent toutes le préfixe (d'url) `/auth`
(c'est précisé lors de la création de l'objet Blueprint `bp`).

*   La fonction utilitaire `load_logged_in_user()` sera exécutée
    systématiquement avant le traitement de toute les requêtes (grâce au
    décorateur `@bp.before_app_request`). Elle vérifie si les données de
    session (des informations transmises au navigateur via un cookie
    chiffré et qu'il renvoie alors à chaque requête) contiennent un
    attibute `user_id`.

    S'il existe, on cherche dans la base un utilisateur ayant ce
    `user_id` et si on le trouve, il est stocké dans les données
    globales de l'application (`g.user`). C'est l'utilisateur
    authentifié.

    Dans tous les autres cas (pas de données de session, id
    introuvable...), `g.user` sera à `None` (pour indiquer que
    l'utilisateur n'est pas connecté).

*   Le décorateur (la fonction utilitaire) `login_required()` est prévu
    pour décorer une route dont l'accès est réservé à un utilisateur
    connecté. Si l'utilisateur n'est pas connecté (si `g.user` est
    `None`), on redirige la requête vers la route de login
    (`auth.login`) et la route décorée n'est pas traitée. Sinon
    l'exécution normale de la route décorée a lieu.

*   La route `register()` (dont l'url est `/auth/register`) gère
    l'inscription d'un nouvel utilisateur. Elle est accessible soit par
    `GET` soit par `POST`.
    
    L'accès par `GET` affiche le formulaire d'inscription décrit par le
    template `auth/register.html`.
    
    L'accès par `POST` reçoit les donnnées soumises à partir de ce
    formulaire, les vérifie et éventuellement crée l'utilisateur.
    
    Note 1: le mot de passe n'est pas enregistré en clair. Il est salé
    et haché par la fonction `generate_password_hash()`.
    
    Note 2: l'avatar (s'il est fourni) est une image envoyée par
    l'utilisateur. Il est réduit à une image de taille 20x20 en PNG
    avant d'être enregistré (en tant que donnée binaire) dans la base de
    données.
    
    En cas d'erreur, on réaffiche le formulaire d'inscription (en
    affichant les `error` détectées).
    
    En cas de succès, l'utilisateur est créé dans la base et
    l'utilisateur est rédirigé vers la route de connexion
    (`auth.login`).

*   La route `login()` (dont l'url est `/auth/login`) gère la connexion
    d'un utilisateur déjà inscrit. Elle est accessible par `GET` ou par
    `POST`.
    
    L'accès par `GET` affiche le formulaire de connexion décrit par le
    template `auth/login.html`.
    
    L'accès par `POST` reçoit les données de connexion (le _username_ et
    le _password_) et vérifie qu'elles correspondent bien à un
    utilisateur inscrit. Note: la comparaison du mot de passe se fait
    via la fonction `check_password_hashe()`.

    Une fois l'authentification effectuée, on crée les données de
    session pour cette utilisateur et on le redirige vers la page
    d'accueil (`root`).
    
    En cas d'erreur, on réaffiche le formulaire de connexion (en
    affichant les `error` détectées).
    
*   La route `avatar()` (dont l'url est `/auth/avatar/<int:user_id>`)
    recoit via son url, le `user_id` de l'utilisateur dont on souhaite
    obtenir l'avatar.
  
    Si l'avatar existe, on renvoie l'image trouvée (l'attribut
    `avatar_content` stocke les données binaires de l'image et
    l'attribut `avatar_mimetype` indique son type MIME). Cette route
    retourne donc une image (ou une photo).
  
    Si l'avatar n'existe (ou même si l'utilisateur n'existe pas), on
    retourne une erreur HTTP 404 (Not Found).
  
*   L'accès à la route `logout()` (dont l'url est `/auth/logout`) est
    protégé par le décorateur `@login_required` (on ne peut pas se
    déconnecter si on n'est pas connecté).
    
    Cette route supprime les données de session de l'utilisateur (elles
    seront supprimées du navigateur de l'utilisateur) et redirige vers
    la page d'accueil (`root`). N'ayant plus de données de session,
    l'utilisateur sera considéré comme n'étant plus connecté.
    

### Les routes concernant la gestion des articles du blog (`flaskrpg/blog.py`).

Dans le fichier `flaskrpg/blog.py`, on trouve une fonction
utilitaire et des routes (elles sont préfixées par le décorateur
`@bp.route`). Ces routes utilisent toutes le préfixe (d'url) `/blog`
(c'est précisé lors de la création de l'objet Blueprint `bp`).


*   La route `index()` (dont l'url est `/blog/`) est librement
    accessible. Elle liste tous les articles publiés.
  
    Elle peut recevoir le paramètre `sort` (via la partie `request` de
    l'url, donc après `?`). Les valeurs possibles pour ce paramètre sont
    `by_date` (valeur par défaut, qui implique un tri des articles par
    date antechronologiqe de création) ou `by_star` (qui implique une
    tri des articles par nombre décroissant d'étoiles).

    La requête SQL à réaliser est un peu complexe puisqu'elle exploite
    deux fois l'association entre `Post` et `Star`: une première fois
    pour savoir si l'utilisateur a attribué une étoile à un article et
    une seconde fois pour compter le nombre d'étoiles accordées à un
    article.
    
    Une fois les données collectées, elle sont transmises au template
    `blog/index.html`.

*   La fonction utilitaire `get_post()` récupère depuis la base un
    article dont on fournit l'`id`. Si cet article n'existe pas, on
    stoppe la requête en cours avec l'erreur HTTP 404 (Not Found).
    
    Si l'argument optionnel `check_author` vaut `True` (c'est la valeur
    par défaut), on vérifie aussi que l'utilisateur courant est bien
    l'auteur de cet article et si ce n'est pas le cas, on stoppe la
    requête en cours avec l'erreur HTTP 403 (Forbidden).
    
    Si tout se passe bien, la fonction retourne l'objet `Post` demandé.

*   La route `create()` (dont l'url est `/blog/create`) n'est accessible
    que lorsque l'utilisateur est connecté. Elle est accessible par
    `GET` ou par `POST`.
    
    L'accès par `GET` affiche le formulaire de création d'un nouvel
    article décrit par le template `blog/create.html`.
    
    L'accès par `POST` reçoit et vérifie les données de création d'un
    nouvel article. Si les données sont correctes, l'article est créé et
    on redirige vers la liste des articles (`blog.index`).
    
    En cas d'erreur, le formulaire de création est réaffiché avec les
    erreurs détectées.
    
*   La route `update()` (dont l'url est `/blog/<int:id>/update`) n'est
    accessible que lorsque l'utilisateur est connecté. Elle est
    accessible par `GET` ou `POST`.
    
    Elle reçoit, via la route, l'`id` de l'article à modifier et elle
    essaye de le retrouver en appelant la fonction `get_post()`. Si
    l'article n'existe pas ou si l'utilisateur n'en est pas l'auteur, la
    fonction `get_post()` stoppera toute seule la requête en cours (voir
    plus haut).
    
    Une fois l'article trouvé, l'accès par `GET` affiche le formulaire
    d'édition d'article via le template `blog/update.html`.
    
    L'accès par `POST` récupère et vérifie les données fournies et
    modifie l'article en conséquence. Une fois la modification
    effectuée, l'utilisateur est redirigé vers la liste des articles
    (`blog.index`).
    
    En cas d'erreur, le formulaire d'édition est réaffiché avec les
    erreurs détectées.
    
*   La route `delete()` (dont l'url est `/blog/<int:id>/delete`) n'est
    accessible que lorsque l'utilisateur est connecté. Elle utilise la
    méthode `POST` (puisqu'elle modifie les données persistantes).

    Après avoir retrouvé l'article par son `id` (via la fonction
    `get_post()`), cette route supprime l'article de la base.
    
*   La route `vote()` (dont l'url est `/blog/<int:id>/voteup`) n'st
    accessible qu'aux utilisateurs connectés. Elle utilise la méthode
    `POST` (puisqu'elle modifie les données persistantes).
    
    Après avoir retrouvé l'article correspondant à l'`id` fourni dans
    l'url (via `get_post()`), elle vérifie si l'utilisateur connecté en
    est l'auteur et renvoie une erreur si c'est le cas.
    
    Si l'utilisateur n'est pas l'auteur de l'article, elle cheche si
    l'utilisateur avait déjà accordé une étoile à cet article. Si c'est
    le cas, elle la supprime et sionn elle la crée.
    
    Dans tous les cas, cette route se termine par une redirection vers
    la liste des articles (`blog.index`).
    
## Les templates des pages HTML générées

> Pour comprendre l'écriture et la soumission des formulaires HTML via
> HTTP, vous pouvez consulter la documentation sur [Les formulaires
> HTML](https://gsidev1.mines-albi.fr/documentation/apache-formulaire.html)
> (hébérgée sur le site
> [gsidev1.mines-albi.fr](https://gsidev1.mines-albi.fr)).

Toutes les pages Web générées par l'application `flaskrpg` sont
produites par le moteur de templates `Jinja2` (en version 3.1.2, fin
2023) en utilisant des _templates_ (des _patrons_ ou des _modèles_).

> Un template est un fichier texte (par exemple du HTML mais ça pourrait
> aussi être du XML, du CSS ou n'importe quel autre type de fichier texte)
> dans lequel on utilise des marqueurs (textuels) spéciaux pour indiquer
> les endroits où le moteur de template doit insérer des données ou
> indiquer les passages qui doivent être répétés avec des données
> différentes. Un template est donc un document générique.

Dans nos routes, nous avons fait appel à la fonction
`render_template()`. Cette fonction déclenche le moteur de templates
Jinja. On lui passe le nom d'un template et les éventuelles données
réelles à utiliser pour fabriquer une page Web complète (en instanciant
les données réelles dans le template).

> La syntaxe à utiliser au sein d'un template est complètement décrite
> dans la [Template Designer
> Documentation](https://jinja.palletsprojects.com/en/3.1.x/templates/).

Dans un premier temps, notez que les marqueurs textuels spéciaux
utilisés par Jinja sont de trois formes:

1. `{# ... #}` c'est un commentaire pour l'auteur du template.

1. `{% ... %}` C'est une directive destiné à Jinja.

1. `{{ ... }}` C'est une expession Python dont le résultat (converti en
   chaîne de caractères) sera inséré dans le template.


Nous allons maintenant décrire les différents templates utilisés par
`flaskrpg` en décrivant quelques-uns des mécanismes Jinja utilisés.

Tous les templates sont rangés dans le sous-répertoire
`flaskrpg/templates`.


>    L'application `falskrpg` utilise `bootstrap` pour gérer la
>    présentation de la plupart des éléments. Ici, nous ne rentrerons
>    pas dans les détails de son utilisation. Il faut se référer à la
>    [documentation de
>    Bootstap](https://getbootstrap.com/docs/4.6/getting-started/introduction/)
>    (lien pour la version actuellement utilisée) qui est très bien
>    rédigée et fournit plein d'exemples de code HTML/CSS.

### Les templates généraux (utilisés indirectement par d'autres)

Ce sont des templates qui ne sont jamais appelés directement depuis les
routes mais qui sont utilisés indirectement par d'autres templates.

*   `base.html` est le plus utilisé des templates utilisés
    indirectement. Il contient la trame générale de toutes les pages Web
    générées. En fait c'est une simple coquille qui accueillera le
    contenu réel.
  
    *   Du point de vue HTML, c'est une page HTML 5 complète avec son
        élément `<html>` qui contient un élément `<head>` suivi de
        l'élément `<body>`.
  
        Dans le `<head>`, on trouve un `<title>`, le chargement et une
        partie de l'initialisation de `bootstrap` (un framework CSS), le
        chargement de `fontawesome` (pour des icônes), le chargement de
        `summernote` (un mini-éditeur de texte riche) et finalement la
        feuille de style CSS spécifique à `flasrkpg`.
  
        Dans le `<body>`, on trouve l'inclusion d'une barre de menu
        (`navbar.html`) puis une série de `<div>` imbriquées contenant
        un élément `<section>`. Dans cette section, on trouve un
        `<header>`, l'inclusion des messages (`messages.html`) et le
        block `content`. La page se termine par le chargement du
        Javascript de `JQuery`, de `popper` et de `bootstrap` puis celui
        de `summernote` et enfin du code javascript spécifique à
        `flaskrpg`.

    *   Du point de vue Jinja, on utilise plusieurs fois une _expression_
        Jinja telle:
    
        ```
        {{ url_for('static', filename='js/flaskrpg.js') }}
        ```
    
        Cette expression sera remplacée par l'url de la route `static`
        de notre application `Flask`. Cela permet de retrouver un
        fichier statique (envoyé tel quel au navigateur). Tous les
        fichiers statiques sont dans le sous-répertoire
        `flaskpg/static`. Et le `filename` indique un emplacement dans
        ce sous-répertoire. Donc, dans l'exemple ci-dessus, l'expression
        complète sera remplacée par l'URL permettant d'accéder au
        fichier statique `flasrkpg/static/js/flaskrpg.js`.
    
        On trouve aussi plusieurs fois une _directive_ Jinja comme:
    
        ```
        {% include "navbar.html" %}
        ```

        Cette directive permet d'inclure le contenu d'un autre template
        (dans le cas ci-dessus, c'est le template de la barre de
        navigation). Ce template inclus sera lui aussi traité par Jinja.
    
        On trouve aussi trois fois une _directive_ Jinja telle:
    
        ```
        {% block title %}{% endblock %}
        ```
    
        Cette directive définit un bloc (`block`) nommé (ici `title`).
    
        Dans `base.html`, on trouve trois blocs nommés `title`, `header`
        et `content`. Et ils sont vides !!! En fait le template
        `base.html` n'est jamais utilisé directement. Il sera étendu
        (`extends`) par d'autres templates qui pourront customiser le
        contenu de ces trois blocs.
    
        Le bloc `title` permet de customiser le titre de la page Web
        générée (c'est une méta-information).
    
        Le bloc `header` permet de customiser le titre générale de la
        page.
    
        Le bloc `content` permet de customiser le contenu de la page.
    

    
*   `navbar.html` contient le code HTML permettant de créer la barre de
    menu d'une page HTML de l'application `flaskrpg`.
    
    D'un point de vue HTML, elle utilise une _navbar_ telle que proposée
    par bootstrap avec un logo (`navbar-brand`) puis une liste d'items
    (`nav-item`) dons certains sont des menus déroulants (`dropdown`).
    
    > Bootstrap étant _«responsive»_, si la fenêtre du navigateur n'est
    > pas assez large (par exemple sur un smartphone), la barre de
    > navigation se transforme automatiquement en un menu _«hamburger»_.
    
    D'un point de vue Jinja, il y a un test permettant d'adapter le
    contenu de la barre de navigation selon que l'utilisateur est
    connecté ou non.
    
    > Notez au passage que nous avons accès à l'objet `g` (les variables
    >     _globales_ de l'application Flask) et donc à `g.user` sans avoir
    >     besoin de le transmettre explicitement.
    
    > Notez aussi que tous les liens vers les routes de l'application sont
    >     générés par des appels à `url_for()` (NE JAMAIS CRÉER SOI-MÊME
    >     L'URL).
    
*   `message.html` permet d'afficher les messages (créés par les routes
    via l'appel à `flash()`) dans la page HTML généré. Leur présentation
    actuelle est très basique et pourrait largement être amélioré.
    
    > ToDo: améliorer la présentation des messages en distinguant par
    > exemple leur catégories (erreur, avertissement...). Voir dans la
    > documentation Flask la section [Message
    > Flashing](https://flask.palletsprojects.com/en/2.3.x/patterns/flashing/).


### Les templates liés au blueprint `auth`

*   `auth/register.html` étend le template `base.html` en définissant
    les trois blocs `header`, `title` et `content`. Il est appelé
    explicitement par la route `auth.register`.
    
    > Le mécanisme d'extension de templates est décrit en détail dans la
    > section [Template
    > Inheritance](https://jinja.palletsprojects.com/en/3.0.x/templates/#template-inheritance)
    > de la documentation de Jinja2.
    
    Le bloc `content` contient le formulaire d'inscription (pour créer
    un nouvel auteur). Il y a trois champs: `username` et
    `password` et `avatar` (qui est de type `file`).
    
    > Notez l'utilisation de l'attribut `required` pour les champs
    > `username` et `password` pour que le navigateur n'autorise pas la
    > soumission du formulaire sans valeur pour ces champs. Mais tous
    > les navigateurs ne le respectent pas et rien n'empêche un
    > utilisateur malicieux d'envoyer sa propre requête (sans passer par
    > le formulaire) avec des champs vides ou même carrément
    > absents. C'est pour cela que le route `auth.register` revérifie
    > tout cela (ON NE PEUT PAS FAIRE UNE CONFIANCE AVEUGLE AUX REQUÊTES
    > REÇUES).

    > L'envoi de fichiers via un formulaire HTML n'est pas simple à
    > gérer. Flask offre des mécanismes pour gérer cela: [Uploading
    > Files](https://flask.palletsprojects.com/en/2.3.x/patterns/fileuploads/).

*   `auth/login.hmtl`  étend le template `base.html` en définissant
    les trois blocs `header`, `title` et `content`. Il est appelé
    explicitement par la route `auth.login`.
    
    Il fonctionne sur le même principe que le template
    `auth/register.html` (sans le champ `avatar`).
    
### Les templates liés au blueprint `blog`

*   `blog/index.html` étend le template `base.html` en définissant les
    trois blocs `header`, `title` et `content`. Il est appelé
    explicitement par la route `blog.index`. Il sert de page d'accueil
    de l'application `flaskrpg`. Il affiche la liste de tous les
    articles présents dans la base.
    
    Dans le bloc `header`, il crée deux boutons permettant de choisir
    l'ordre d'affichage des articles (par ordre antéchronologique ou par
    ordre décroissant du nombre d'étoiles). Et si l'utilisateur est
    connecté, il ajoute un troisième bouton permettant d'accéder au
    formulaire de création d'un nouvel article.

    > Le code HTML de la forme `<i class="fa fa-plus"
    > aria-hidden="true"></i>` permet d'insérer des icônes de la police
    > `fontawesome`. Pour choisir une icône, faites une
    > [recherche](https://fontawesome.com/v5/search) (attention, l'accès
    > aux icônes PRO n'est pas possible avec la version gratuite
    > utilisée) puis cliquez sur l'icône voulue pour obtenir le code
    > HTML à insérer.
    
    Dans le bloc `content`, il crée une suite d'éléments `<article>` (un
    par `post`) grâce à une boucle de Jinja:
    
    ```
    {% for post in posts %}
       ...
    {% else %}
       <p>No post...</p>
    {% endfor %}
    ```
    
    > Notez l'utilisation du `else` en fin de boucle afin de traiter le
    > cas où `posts` est vide (cf. la documentation Jinja pour
    > [for](https://jinja.palletsprojects.com/en/3.0.x/templates/#for).

    Chaque article est placé dans une `card` (de bootstrap).
    
    Le `card-header` contient le titre, l'auteur (et son éventuel
    avatar), la date de création, le nombre d'étoiles accordées.
    
    Si l'utilisateur est l'auteur de l'article, l'icône d'un crayon
    (`pencil`) lui permet d'éditer son article (via la route
    `blog.update`).
    
    Si l'utilisateur est connecté mais n'est pas l'auteur de l'article,
    l'icône d'une étoile est affichée pleine ou creuse selon que
    l'utilisateur a déjà voté ou non pour cet article. De plus cette
    étoile est un bouton de soumission d'un formulaire permettant de
    changer le vote de l'utilisateur (via la route `blog.vote`).
    
    Le `card-body` contient le contenu de l'article (`post.body`). Notez
    qu'on utilise ici le filtre `safe` pour indiquer que ce contenu est
    déjà en HTML et qu'il ne faut pas le réencoder. Mais c'est un
    potentiel risque de sécurité (pour l'utilisateur) car il faudrait
    s'assurer que ce contenu en HTML est innofensif avant de l'afficher
    tel quel!
    
*   `blog/create.html` et `blog/update.html` étendent tous les deux le
    template `base.html` en définissant les trois blocs `header`,
    `title` et `content`. Ils sont appelés explicitement par la route
    `blog.create` pour le premier et par la route `blog.update` pour le
    second.
    
    Ils définissent un block `header` et un `title` légèrement différent
    pour différencier la création d'une article et la modication d'un
    article.
    
    Tous les deux incluent le template utilitaire `blog/post-form.html`
    qui leur permet de récupérer la macro Jinja `post_form.form` et de
    l'appeller en lui passant des paramètres différents (rien si on est
    en création et, si on est édition, les informations de l'article à
    éditer).
    
*   `blog/post-form.html` est un template utilitaire qui définit la
    macro Jinja `form`. Cette macro reçoit trois paramètres: le `title`,
    le `body` et l'`id` d'un article à éditer. Les valeurs par défaut
    (chaînes vides et `None`) servent lors de la création d'un article.
    
    Si l'`id` de l'article est défini, la macro crée alors un formulaire
    de suppression de l'article (via la route `blog.delete`) dont l'`id`
    HTML est `post-delete` (ce formulaire ne contient pas de bouton).
    
    La macro crée ensuite un second formulaire (vide) dont l'action
    consiste juste à activer la route `blog.index` (ce formulaire ne
    contient pas de bouton).
    
    Ensuite vient le formulaire d'édition de l'article qui contient le
    champ `title`, le champ `body` puis les deux boutons «save» et
    «cancel» et un éventuel bouton «delete» (si on édite un article
    existant, dont l'`id` est défini).
    
    Note 1: seul le bouton «save» est un bouton de soumission du
    formulaire d'édition. Les boutons «delete» et «cancel» sont chacun
    rattachés (via leur attribut HTML `form`) à l'un des deux
    formulaires sans bouton créer précédemment.
    
    Note 2: le bouton «delete» déclenchant une action d'effacement
    irréversible utilise du Javascript (via son attribut `onclick`) pour
    demander une confirmation à l'utilisateur.
    
    Note 3: le champs contenant le `body` est un élément
    `textarea`. Mais l'une des ses classes CSS est `summernote`, ce qui
    permet de le transformer en un éditeur de texte HTML riche (via
    l'extension `summernote` chargée pour le template `base.html`). Si
    bien que le contenu envoyé n'est pas un simple texte mais du HTML
    (filtré par `summernote` pour ne contenir que du contenu
    inoffensif). Mais rien n'empêche un utilisateur malicieux de passer
    outre ce filtrage (effectué côté navigateur) et ainsi envoyer du
    code HTML malicieux. Or les routes `blog.update` et `blog.create`
    stocke ce code HTML tel quel dans la base et le template
    `blog.index` affiche ce code HTML en supposant qu'il est inoffensif
    (via le filtre `safe`). C'est potentiellement dangereux pour les
    utilateurs de notre application.
    
    > Todo: filtrer côté serveur le code HTML reçu pour le `body` d'un
    > article avant de le stocker dans la base OU désactiver l'extension
    > `summernote` et supprimer le filtre `safe` lors de l'affichage du
    > `body` d'un article pour ne pas prendre en compte du HTML.
    
## Les fichiers statiques (dans le répertoire `flaskrpg/static`)

*   `css/flaskrpg-with-bootstrap.css` est une feuille de style CSS
    simple qui vient s'ajouter aux feuilles de styles CSS chargées par
    bootstrap. Elle permet de customiser quelques éléments pour des
    besoins spécifiques.
    
    > Todo: mieux documenter cette feuille de style OU utiliser le
    > générateur de CSS de bootstrap pour utiliser un bootstrap
    > customisé.
    
*   `js/flasrpg.js` est le code Javascript de l'application. Il montre
    comment créer simplement une variable Javascript `flaskrpg` qui
    contiendra tout le code de l'application (pour éviter de polluer
    l'espace de nommage Javascript) et comment attendre la fin du
    chargement de la page avant de déclencher son initilisation.
    
    Ici, la seule tâche à réaliser est de chercher dans la page tous les
    éléments dont l'attribut `class` contient `summernote` pour leur
    appliquer l'extension `summernote` (l'extension permettant
    d'utiliser un mini-éditeur de HTML).

## Les fichiers de configuration Flask et Python

*   `.flaskenv` ne sert qu'à définir le nom de l'application Flask
    lorsqu'on lance la commande `flask` (Flask le lit automatiquement
    car le package `python-dotenv` est installé dans l'envirionnement
    virtuel).
    
*   `setup.py` n'est qu'un fichier de transition indispensable qui
    permet de faire le lien avec le fichier `setup.cfg`.
    
*   `setup.cfg` définit la méta-information (`[metadata]`) de
    l'application (le nom, la version, l'auteur, la licence, etc.).
    
    Puis il indique la liste des packages Python requis pour le
    fonctionnement de l'application (via les `[options]`).
    
    La suite indique les packages nécessaires aux tests (utilisés) ou à
    la constuction d'une archive de distibution de l'application (non
    utilisée actuellement). On trouve aussi des paramètres spécifiques
    aux phases de tests (unitaires ou de couverture).

*   Le fichier `pyproject.toml` permet de configurer le système de
    construction de l'archive de distribution de l'application
    `flaskrpg` (pas utilisée actuellement).

*   Le fichier `LICENSE.rst` indique la licence du code. Il faudrait la
    clarifier!

## Déploiement de l'application dans un serveur Web (Apache par exemple)

Une application Web est rarement un site Web à elle toute seule. Le
fichier `wsgi/flaskrpg.wsgi` permet le déploiement au sein d'un site Web
préexistant (géré par Apache par exemple). Dans ce cas, l'url racine de
l'application peut-être un chemin dans l'arborescence du site Web
global. C'est là que l'utilisation systématique de `url_for()` pour
connaître l'url des routes devient absolument fondamental.

Le fichier [README-ADMIN.md](README-ADMIN.md) décrit l'utilisation de ce
fichier pour installer l'application `falskrpg` dans un serveur Apache.

> WSGI (Web Server Gateway Interface) est un standard pour le
> déploiement d'application Web Python au sein d'un serveur Web.  Nous
> avons documenté son usage au sein d'Apache mais c'est aussi utilisable
> au sein de Nginx.

## Le répertoire `flask_sqlalchemy_session`

Ce répertoire contient une version patché du module
[`flask_sqlalchemy_session`
](https://github.com/dtheodor/flask-sqlalchemy-session). Ce module
pourtant bien utile n'est plus adapté aux dernière version de
Flask. C'est pourquoi nous le fournissons dans une version patché pour
les versions récentes de Flask.

Ce module est utile pour créer une session SQLAlchemy qui se
réinitialise toutes seule à chaque traitement d'une nouvelle requête par
l'application Flask. Cette fonctionnalité qui fait partie des bonnes
pratiques n'est évidement fourni ni par SQLAlchemy (qui ne connaît pas
Flask) ni par Flask (qui n'impose pas l'utilisation de SQLAlchemy).

> Todo: trouver une meilleure solution OU distribuer cette version
> améliorée en opensource après avoir justifié le besoin, avoir prouvé
> qu'elle assure bien tout le service attendu et l'avoir correctement
> documentée.
    
## Le répertoire `tests`

Ce répertoire contient des tests unitaires (mais pas que unitaires) qui
peuvent être effectués automatiquement sur l'application `flaskrpg`.

Ils utilisent le package Python `pytest`.

*   Le fichier `tests/conftest.py` contient une fonction utilitaire
    (`execute_sql_file_with_psql`) et des fonctions permettant
    d'initialiser le contexte de certains tests (cela s'appelle des
    `fixture` dans le vocabulaire de `pytest`).

    Le fixture `init_test_db` est effectué automatiquement au début de
    chaque session de test et permet de s'assurer que la base de données
    contient bien les données de tests.

    Le fixture `test_app` crée l'application Flask `flaksrpg` de test.
    
    Le fixture `web_client` crée un client Web permettant de simuler des
    requêtes.
    
    Le fixture `db_objects` permet de récupérer les objets créés par
    `db.py` pour dialoguer avec la base de données.
    
*   Le fichier `tests/test_flaskrpg.py` contient les tests à effectuer
    par `pytest`.
    
    Chaque test est nécessairement une fonction dont le nom commence par
    `test_` (c'est le moyen utilisé par `pytest` pour trouver les
    tests). Comme les tests sont effectués dans l'ordre alphabétique,
    nous avons ajouté un numéro d'ordre logique.
    
    Note: les tests doivent être indépendants les uns des autres (on
    peut décider d'en n'effectuer que quelques-uns ou même un
    seul). Comme ils utilisent tous la même base de données et que, pour
    des raisons d'efficacité, elle n'est pas réinitialisée à chaque
    test, il faut faire en sorte que chaque test (réussi ou échoué)
    laisse la base tel q'uil l'a trouvé en arrivant.

    > Todo: mieux documenter les tests existants (leur rôle mais aussi
    > leur fonctionnement).

    > Todo -- Les tests actuels sont loin d'être exhaustifs: ils ne
    > couvreent qu'environ 60% du code. Un taux de couverture correct
    > tourne autour de 80% (le 100% idéal étant évidemment inaccessible
    > en pratique).
    


