alter table "public"."notifications" drop constraint "notifications_chat_id_fkey";

create table "public"."emoji" (
    "emoji_id" uuid not null,
    "creation_time" timestamp with time zone not null default now(),
    "emoji" character varying,
    "message_id" uuid not null,
    "user_id" uuid not null
);


alter table "public"."emoji" enable row level security;

CREATE UNIQUE INDEX chat_history_message_id_key ON public.chat_history USING btree (message_id);

CREATE UNIQUE INDEX chats_chat_id_key ON public.chats USING btree (chat_id);

CREATE UNIQUE INDEX emoji_pkey ON public.emoji USING btree (message_id, emoji_id, user_id);

alter table "public"."emoji" add constraint "emoji_pkey" PRIMARY KEY using index "emoji_pkey";

alter table "public"."chat_history" add constraint "chat_history_message_id_key" UNIQUE using index "chat_history_message_id_key";

alter table "public"."chats" add constraint "chats_chat_id_key" UNIQUE using index "chats_chat_id_key";

alter table "public"."emoji" add constraint "emoji_message_id_fkey" FOREIGN KEY (message_id) REFERENCES chat_history(message_id) ON UPDATE CASCADE ON DELETE CASCADE not valid;

alter table "public"."emoji" validate constraint "emoji_message_id_fkey";

alter table "public"."emoji" add constraint "emoji_user_id_fkey" FOREIGN KEY (user_id) REFERENCES auth.users(id) not valid;

alter table "public"."emoji" validate constraint "emoji_user_id_fkey";


