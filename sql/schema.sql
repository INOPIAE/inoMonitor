DROP TABLE IF EXISTS website;
CREATE TABLE website (website_id serial NOT NULL,
                   url VARCHAR(200) NOT NULL,
                   entered timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
                   deleted timestamp NULL,
                   PRIMARY KEY(website_id));

DROP TABLE IF EXISTS testcase;
CREATE TABLE testcase (testcase_id serial NOT NULL,
                   testcase VARCHAR(200) NOT NULL,
                   PRIMARY KEY(testcase_id));

DROP TABLE IF EXISTS testresult;
DROP TYPE IF EXISTS "testresult_type";
CREATE TYPE "testresult_type" AS ENUM ('good', 'false');
CREATE TABLE testresult (testresult_id serial NOT NULL,
                   website_id INTEGER NOT NULL,
                   testcase_id INTEGER NOT NULL,
                   testresult testresult_type NOT NULL,
                   status_code INTEGER NOT NULL,
                   response_message VARCHAR(200) NOT NULL,
                   entered timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
                   PRIMARY KEY(testresult_id));

DROP TABLE IF EXISTS schema_version;
CREATE TABLE schema_version (version INTEGER NOT NULL);
INSERT INTO schema_version(version) VALUES(1);
