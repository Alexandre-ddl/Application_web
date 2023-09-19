INSERT INTO "user" ("username", "password") VALUES
('polo', 'pbkdf2:sha256:150000$yYDumTmh$dd0b82d936ec3d5058f43809d2e1b363d41f9b158039b58921c67ac19042391f'),
('toto', 'pbkdf2:sha256:150000$tXe6g8kL$bb202dd48e19184b234132628a23807ff128d7c3c5d2aa4d2eccb55c50ba5a9f');

INSERT INTO "post" ("author_id", "created", "title", "body") VALUES
(2,      '2020-12-22 09:17:09.93821',    'aaaa', 'aaaa'),
(1,      '2020-12-22 10:04:07.47829',    'bbbb', 'bbbb');

INSERT INTO "star" ("user_id", "post_id") VALUES
(1,     1);

