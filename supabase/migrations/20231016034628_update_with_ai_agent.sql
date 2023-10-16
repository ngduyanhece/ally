create table "public"."brains_meta_brains" (
    "meta_brain_id" uuid not null,
    "brain_id" uuid not null
);


create table "public"."meta_brains" (
    "meta_brain_id" uuid not null default gen_random_uuid(),
    "name" text not null,
    "status" text,
    "description" text,
    "model" text,
    "max_tokens" integer,
    "temperature" double precision,
    "openai_api_key" text,
    "last_update" timestamp without time zone default CURRENT_TIMESTAMP
);


create table "public"."meta_brains_users" (
    "meta_brain_id" uuid not null,
    "user_id" uuid not null,
    "rights" character varying(255),
    "default_meta_brain" boolean default false
);


alter table "public"."api_keys" add column "email" text;

alter table "public"."user_identity" add column "email" text;

alter table "public"."user_settings" add column "max_meta_brains" integer default 2;

CREATE UNIQUE INDEX meta_brains_brains_pkey ON public.brains_meta_brains USING btree (meta_brain_id, brain_id);

CREATE UNIQUE INDEX meta_brains_pkey ON public.meta_brains USING btree (meta_brain_id);

CREATE UNIQUE INDEX meta_brains_users_pkey ON public.meta_brains_users USING btree (meta_brain_id, user_id);

alter table "public"."brains_meta_brains" add constraint "meta_brains_brains_pkey" PRIMARY KEY using index "meta_brains_brains_pkey";

alter table "public"."meta_brains" add constraint "meta_brains_pkey" PRIMARY KEY using index "meta_brains_pkey";

alter table "public"."meta_brains_users" add constraint "meta_brains_users_pkey" PRIMARY KEY using index "meta_brains_users_pkey";

alter table "public"."brains_meta_brains" add constraint "brains_meta_brains_brain_id_fkey" FOREIGN KEY (brain_id) REFERENCES brains(brain_id) ON UPDATE CASCADE ON DELETE CASCADE not valid;

alter table "public"."brains_meta_brains" validate constraint "brains_meta_brains_brain_id_fkey";

alter table "public"."brains_meta_brains" add constraint "brains_meta_brains_meta_brain_id_fkey" FOREIGN KEY (meta_brain_id) REFERENCES meta_brains(meta_brain_id) ON UPDATE CASCADE ON DELETE CASCADE not valid;

alter table "public"."brains_meta_brains" validate constraint "brains_meta_brains_meta_brain_id_fkey";

alter table "public"."meta_brains_users" add constraint "meta_brains_users_meta_brain_id_fkey" FOREIGN KEY (meta_brain_id) REFERENCES meta_brains(meta_brain_id) ON UPDATE CASCADE ON DELETE CASCADE not valid;

alter table "public"."meta_brains_users" validate constraint "meta_brains_users_meta_brain_id_fkey";

alter table "public"."meta_brains_users" add constraint "meta_brains_users_user_id_fkey" FOREIGN KEY (user_id) REFERENCES auth.users(id) not valid;

alter table "public"."meta_brains_users" validate constraint "meta_brains_users_user_id_fkey";


