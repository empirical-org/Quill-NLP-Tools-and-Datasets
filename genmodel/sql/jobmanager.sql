/* Create Jobs Table */
CREATE TABLE jobs (
  id integer PRIMARY KEY NOT NULL,
  name varchar,
  meta jsonb
);


/* Create Droplets Table
 * 
 * droplets can be deleted by tag, so tagging a droplet with it's job_id might
 * be a sensible choice so that all droplets can be deleted at once.
 * https://developers.digitalocean.com/documentation/v2/#deleting-droplets-by-tag
 *
 */
CREATE TABLE droplets (
  id integer PRIMARY KEY NOT NULL,
  uid	integer NOT NULL,
  job_id integer NOT NULL,
  name	varchar NOT NULL,
  memory	integer,
  vcpus	integer,
  disk	integer,
  locked	boolean,
  created_at	varchar,
  status	varchar,
  backup_ids	varchar[],
  snapshot_ids	varchar[],
  features	varchar[],
  region	jsonb,
  image	jsonb,
  size	jsonb,
  size_slug	varchar,
  networks	jsonb,
  kernel	jsonb,
  next_backup_window	jsonb,
  tags	varchar[],
  volume_ids	varchar[],
  meta jsonb
);

/* Create Labled Data Table */
CREATE TABLE labled_data (
  id integer PRIMARY KEY NOT NULL,
  data jsonb NOT NULL,
  label varchar NOT NULL,
  job_id integer NOT NULL,
  meta jsonb
);

/* Create Reductions Table */
CREATE TABLE reductions (
  id integer PRIMARY KEY NOT NULL,
  reduction varchar NOT NULL,
  job_id integer NOT NULL,
  meta jsonb
);

/* Create Vectors Table */
CREATE TABLE vectors (
  id integer PRIMARY KEY NOT NULL,
  vector jsonb NOT NULL,
  label varchar NOT NULL,
  job_id integer NOT NULL,
  meta jsonb
);

