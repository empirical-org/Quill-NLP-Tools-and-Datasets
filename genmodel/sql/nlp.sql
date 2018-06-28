
/* Create Jobs Table */
CREATE TABLE IF NOT EXISTS jobs (
  id integer PRIMARY KEY NOT NULL,
  name varchar UNIQUE,
  state varchar, -- created, running, finished, 
  created timestamp with time zone default now(),
  updated timestamp with time zone default now(),
  meta jsonb
);


/* Create Droplets Table
 * 
 * droplets can be deleted by tag, so tagging a droplet with it's job_id might
 * be a sensible choice so that all droplets can be deleted at once.
 * https://developers.digitalocean.com/documentation/v2/#deleting-droplets-by-tag
 *
 */
CREATE TABLE IF NOT EXISTS droplets (
  id integer PRIMARY KEY NOT NULL,
  uid	integer,
  job_id integer NOT NULL,
  name	varchar UNIQUE NOT NULL,
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
  created timestamp with time zone default now(),
  updated timestamp with time zone default now(),
  meta jsonb
);


/* Create Labled Data Table */
CREATE TABLE IF NOT EXISTS labled_data (
  id integer PRIMARY KEY NOT NULL,
  data jsonb NOT NULL,
  label varchar NOT NULL,
  job_id integer NOT NULL,
  created timestamp with time zone default now(),
  updated timestamp with time zone default now(),
  meta jsonb
);

/* Create Reductions Table */
CREATE TABLE IF NOT EXISTS reductions (
  id integer PRIMARY KEY NOT NULL,
  reduction varchar NOT NULL,
  job_id integer NOT NULL,
  created timestamp with time zone default now(),
  updated timestamp with time zone default now(),
  meta jsonb
);


/* Create Vectors Table */
CREATE TABLE IF NOT EXISTS vectors (
  id integer PRIMARY KEY NOT NULL,
  vector jsonb NOT NULL,
  label varchar NOT NULL,
  job_id integer NOT NULL,
  created timestamp with time zone default now(),
  updated timestamp with time zone default now(),
  meta jsonb
);

