
SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

CREATE EXTENSION IF NOT EXISTS "pgsodium" WITH SCHEMA "pgsodium";

CREATE EXTENSION IF NOT EXISTS "pg_graphql" WITH SCHEMA "graphql";

CREATE EXTENSION IF NOT EXISTS "pg_stat_statements" WITH SCHEMA "extensions";

CREATE EXTENSION IF NOT EXISTS "pgcrypto" WITH SCHEMA "extensions";

CREATE EXTENSION IF NOT EXISTS "pgjwt" WITH SCHEMA "extensions";

CREATE EXTENSION IF NOT EXISTS "supabase_vault" WITH SCHEMA "vault";

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA "extensions";

CREATE EXTENSION IF NOT EXISTS "vector" WITH SCHEMA "public";

CREATE OR REPLACE FUNCTION "public"."get_user_email_by_user_id"("user_id" "uuid") RETURNS TABLE("email" "text")
    LANGUAGE "plpgsql" SECURITY DEFINER
    AS $$
BEGIN
  RETURN QUERY SELECT au.email::text FROM auth.users au WHERE au.id = user_id;
END;
$$;

ALTER FUNCTION "public"."get_user_email_by_user_id"("user_id" "uuid") OWNER TO "postgres";

CREATE OR REPLACE FUNCTION "public"."get_user_id_by_user_email"("user_email" "text") RETURNS TABLE("user_id" "uuid")
    LANGUAGE "plpgsql" SECURITY DEFINER
    AS $$
BEGIN
  RETURN QUERY SELECT au.id::uuid FROM auth.users au WHERE au.email = user_email;
END;
$$;

ALTER FUNCTION "public"."get_user_id_by_user_email"("user_email" "text") OWNER TO "postgres";

CREATE OR REPLACE FUNCTION "public"."match_summaries"("query_embedding" "public"."vector", "match_count" integer, "match_threshold" double precision) RETURNS TABLE("id" bigint, "document_id" "uuid", "content" "text", "metadata" "jsonb", "embedding" "public"."vector", "similarity" double precision)
    LANGUAGE "plpgsql"
    AS $$
#variable_conflict use_column
BEGIN
    RETURN QUERY
    SELECT
        id,
        document_id,
        content,
        metadata,
        embedding,
        1 - (summaries.embedding <=> query_embedding) AS similarity
    FROM
        summaries
    WHERE 1 - (summaries.embedding <=> query_embedding) > match_threshold
    ORDER BY
        summaries.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

ALTER FUNCTION "public"."match_summaries"("query_embedding" "public"."vector", "match_count" integer, "match_threshold" double precision) OWNER TO "postgres";

CREATE OR REPLACE FUNCTION "public"."match_vectors"("query_embedding" "public"."vector", "match_count" integer, "p_brain_id" "uuid") RETURNS TABLE("id" "uuid", "brain_id" "uuid", "content" "text", "metadata" "jsonb", "embedding" "public"."vector", "similarity" double precision)
    LANGUAGE "plpgsql"
    AS $$
#variable_conflict use_column
BEGIN
    RETURN QUERY
    SELECT
        vectors.id,
        brains_vectors.brain_id,
        vectors.content,
        vectors.metadata,
        vectors.embedding,
        1 - (vectors.embedding <=> query_embedding) AS similarity
    FROM
        vectors
    INNER JOIN
        brains_vectors ON vectors.id = brains_vectors.vector_id
    WHERE brains_vectors.brain_id = p_brain_id
    ORDER BY
        vectors.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

ALTER FUNCTION "public"."match_vectors"("query_embedding" "public"."vector", "match_count" integer, "p_brain_id" "uuid") OWNER TO "postgres";

SET default_tablespace = '';

SET default_table_access_method = "heap";

CREATE TABLE IF NOT EXISTS "public"."api_keys" (
    "key_id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "user_id" "uuid",
    "api_key" "text",
    "creation_time" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    "deleted_time" timestamp without time zone,
    "is_active" boolean DEFAULT true
);

ALTER TABLE "public"."api_keys" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."brain_subscription_invitations" (
    "brain_id" "uuid" NOT NULL,
    "email" character varying(255) NOT NULL,
    "rights" character varying(255)
);

ALTER TABLE "public"."brain_subscription_invitations" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."brains" (
    "brain_id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "name" "text" NOT NULL,
    "status" "text",
    "description" "text",
    "model" "text",
    "max_tokens" integer,
    "temperature" double precision,
    "openai_api_key" "text",
    "prompt_id" "uuid",
    "last_update" timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE "public"."brains" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."brains_users" (
    "brain_id" "uuid" NOT NULL,
    "user_id" "uuid" NOT NULL,
    "rights" character varying(255),
    "default_brain" boolean DEFAULT false
);

ALTER TABLE "public"."brains_users" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."brains_vectors" (
    "brain_id" "uuid" NOT NULL,
    "vector_id" "uuid" NOT NULL,
    "file_sha1" "text"
);

ALTER TABLE "public"."brains_vectors" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."chat_history" (
    "message_id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "chat_id" "uuid" NOT NULL,
    "user_message" "text",
    "assistant" "text",
    "message_time" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    "prompt_id" "uuid",
    "brain_id" "uuid"
);

ALTER TABLE "public"."chat_history" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."chats" (
    "chat_id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "user_id" "uuid",
    "creation_time" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    "history" "jsonb",
    "chat_name" "text"
);

ALTER TABLE "public"."chats" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."knowledge" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "file_name" "text",
    "url" "text",
    "brain_id" "uuid" NOT NULL,
    "extension" "text" NOT NULL,
    CONSTRAINT "knowledge_check" CHECK (((("file_name" IS NOT NULL) AND ("url" IS NULL)) OR (("file_name" IS NULL) AND ("url" IS NOT NULL))))
);

ALTER TABLE "public"."knowledge" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."knowledge_vectors" (
    "knowledge_id" "uuid" NOT NULL,
    "vector_id" "uuid" NOT NULL,
    "embedding_model" "text" NOT NULL
);

ALTER TABLE "public"."knowledge_vectors" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."migrations" (
    "name" character varying(255) NOT NULL,
    "executed_at" timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE "public"."migrations" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."notifications" (
    "id" "uuid" DEFAULT "gen_random_uuid"() NOT NULL,
    "datetime" timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    "chat_id" "uuid",
    "message" "text",
    "action" character varying(255) NOT NULL,
    "status" character varying(255) NOT NULL
);

ALTER TABLE "public"."notifications" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."prompts" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "title" character varying(255),
    "content" "text",
    "status" character varying(255) DEFAULT 'private'::character varying
);

ALTER TABLE "public"."prompts" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."stats" (
    "time" timestamp without time zone,
    "chat" boolean,
    "embedding" boolean,
    "details" "text",
    "metadata" "jsonb",
    "id" integer NOT NULL
);

ALTER TABLE "public"."stats" OWNER TO "postgres";

ALTER TABLE "public"."stats" ALTER COLUMN "id" ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME "public"."stats_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);

CREATE TABLE IF NOT EXISTS "public"."summaries" (
    "id" bigint NOT NULL,
    "document_id" "uuid",
    "content" "text",
    "metadata" "jsonb",
    "embedding" "public"."vector"(1536)
);

ALTER TABLE "public"."summaries" OWNER TO "postgres";

CREATE SEQUENCE IF NOT EXISTS "public"."summaries_id_seq"
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

ALTER TABLE "public"."summaries_id_seq" OWNER TO "postgres";

ALTER SEQUENCE "public"."summaries_id_seq" OWNED BY "public"."summaries"."id";

CREATE TABLE IF NOT EXISTS "public"."user_daily_usage" (
    "user_id" "uuid" NOT NULL,
    "email" "text",
    "date" "text" NOT NULL,
    "daily_requests_count" integer
);

ALTER TABLE "public"."user_daily_usage" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."user_identity" (
    "user_id" "uuid" NOT NULL,
    "openai_api_key" character varying(255)
);

ALTER TABLE "public"."user_identity" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."user_settings" (
    "user_id" "uuid" NOT NULL,
    "models" "jsonb" DEFAULT '["gpt-3.5-turbo"]'::"jsonb",
    "daily_chat_credit" integer DEFAULT 20,
    "max_brains" integer DEFAULT 3,
    "max_brain_size" integer DEFAULT 10000000
);

ALTER TABLE "public"."user_settings" OWNER TO "postgres";

CREATE TABLE IF NOT EXISTS "public"."vectors" (
    "id" "uuid" DEFAULT "extensions"."uuid_generate_v4"() NOT NULL,
    "content" "text",
    "file_sha1" "text",
    "metadata" "jsonb",
    "embedding" "public"."vector"(1536)
);

ALTER TABLE "public"."vectors" OWNER TO "postgres";

ALTER TABLE ONLY "public"."summaries" ALTER COLUMN "id" SET DEFAULT "nextval"('"public"."summaries_id_seq"'::"regclass");

ALTER TABLE ONLY "public"."api_keys"
    ADD CONSTRAINT "api_keys_api_key_key" UNIQUE ("api_key");

ALTER TABLE ONLY "public"."api_keys"
    ADD CONSTRAINT "api_keys_pkey" PRIMARY KEY ("key_id");

ALTER TABLE ONLY "public"."brain_subscription_invitations"
    ADD CONSTRAINT "brain_subscription_invitations_pkey" PRIMARY KEY ("brain_id", "email");

ALTER TABLE ONLY "public"."brains"
    ADD CONSTRAINT "brains_pkey" PRIMARY KEY ("brain_id");

ALTER TABLE ONLY "public"."brains_users"
    ADD CONSTRAINT "brains_users_pkey" PRIMARY KEY ("brain_id", "user_id");

ALTER TABLE ONLY "public"."brains_vectors"
    ADD CONSTRAINT "brains_vectors_pkey" PRIMARY KEY ("brain_id", "vector_id");

ALTER TABLE ONLY "public"."chat_history"
    ADD CONSTRAINT "chat_history_pkey" PRIMARY KEY ("chat_id", "message_id");

ALTER TABLE ONLY "public"."chats"
    ADD CONSTRAINT "chats_pkey" PRIMARY KEY ("chat_id");

ALTER TABLE ONLY "public"."knowledge"
    ADD CONSTRAINT "knowledge_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."knowledge_vectors"
    ADD CONSTRAINT "knowledge_vectors_pkey" PRIMARY KEY ("knowledge_id", "vector_id", "embedding_model");

ALTER TABLE ONLY "public"."migrations"
    ADD CONSTRAINT "migrations_pkey" PRIMARY KEY ("name");

ALTER TABLE ONLY "public"."notifications"
    ADD CONSTRAINT "notifications_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."prompts"
    ADD CONSTRAINT "prompts_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."stats"
    ADD CONSTRAINT "stats_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."summaries"
    ADD CONSTRAINT "summaries_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."user_daily_usage"
    ADD CONSTRAINT "user_daily_usage_pkey" PRIMARY KEY ("user_id", "date");

ALTER TABLE ONLY "public"."user_identity"
    ADD CONSTRAINT "user_identity_pkey" PRIMARY KEY ("user_id");

ALTER TABLE ONLY "public"."user_settings"
    ADD CONSTRAINT "user_settings_pkey" PRIMARY KEY ("user_id");

ALTER TABLE ONLY "public"."vectors"
    ADD CONSTRAINT "vectors_pkey" PRIMARY KEY ("id");

ALTER TABLE ONLY "public"."api_keys"
    ADD CONSTRAINT "api_keys_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id");

ALTER TABLE ONLY "public"."brain_subscription_invitations"
    ADD CONSTRAINT "brain_subscription_invitations_brain_id_fkey" FOREIGN KEY ("brain_id") REFERENCES "public"."brains"("brain_id");

ALTER TABLE ONLY "public"."brains"
    ADD CONSTRAINT "brains_prompt_id_fkey" FOREIGN KEY ("prompt_id") REFERENCES "public"."prompts"("id");

ALTER TABLE ONLY "public"."brains_users"
    ADD CONSTRAINT "brains_users_brain_id_fkey" FOREIGN KEY ("brain_id") REFERENCES "public"."brains"("brain_id");

ALTER TABLE ONLY "public"."brains_users"
    ADD CONSTRAINT "brains_users_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id");

ALTER TABLE ONLY "public"."brains_vectors"
    ADD CONSTRAINT "brains_vectors_brain_id_fkey" FOREIGN KEY ("brain_id") REFERENCES "public"."brains"("brain_id");

ALTER TABLE ONLY "public"."brains_vectors"
    ADD CONSTRAINT "brains_vectors_vector_id_fkey" FOREIGN KEY ("vector_id") REFERENCES "public"."vectors"("id");

ALTER TABLE ONLY "public"."chat_history"
    ADD CONSTRAINT "chat_history_brain_id_fkey" FOREIGN KEY ("brain_id") REFERENCES "public"."brains"("brain_id");

ALTER TABLE ONLY "public"."chat_history"
    ADD CONSTRAINT "chat_history_chat_id_fkey" FOREIGN KEY ("chat_id") REFERENCES "public"."chats"("chat_id");

ALTER TABLE ONLY "public"."chat_history"
    ADD CONSTRAINT "chat_history_prompt_id_fkey" FOREIGN KEY ("prompt_id") REFERENCES "public"."prompts"("id");

ALTER TABLE ONLY "public"."chats"
    ADD CONSTRAINT "chats_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id");

ALTER TABLE ONLY "public"."knowledge"
    ADD CONSTRAINT "knowledge_brain_id_fkey" FOREIGN KEY ("brain_id") REFERENCES "public"."brains"("brain_id");

ALTER TABLE ONLY "public"."knowledge_vectors"
    ADD CONSTRAINT "knowledge_vectors_knowledge_id_fkey" FOREIGN KEY ("knowledge_id") REFERENCES "public"."knowledge"("id");

ALTER TABLE ONLY "public"."knowledge_vectors"
    ADD CONSTRAINT "knowledge_vectors_vector_id_fkey" FOREIGN KEY ("vector_id") REFERENCES "public"."vectors"("id");

ALTER TABLE ONLY "public"."notifications"
    ADD CONSTRAINT "notifications_chat_id_fkey" FOREIGN KEY ("chat_id") REFERENCES "public"."chats"("chat_id");

ALTER TABLE ONLY "public"."summaries"
    ADD CONSTRAINT "summaries_document_id_fkey" FOREIGN KEY ("document_id") REFERENCES "public"."vectors"("id");

ALTER TABLE ONLY "public"."user_daily_usage"
    ADD CONSTRAINT "user_daily_usage_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "auth"."users"("id");

GRANT USAGE ON SCHEMA "public" TO "postgres";
GRANT USAGE ON SCHEMA "public" TO "anon";
GRANT USAGE ON SCHEMA "public" TO "authenticated";
GRANT USAGE ON SCHEMA "public" TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_in"("cstring", "oid", integer) TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_in"("cstring", "oid", integer) TO "anon";
GRANT ALL ON FUNCTION "public"."vector_in"("cstring", "oid", integer) TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_in"("cstring", "oid", integer) TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_out"("public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_out"("public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_out"("public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_out"("public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_recv"("internal", "oid", integer) TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_recv"("internal", "oid", integer) TO "anon";
GRANT ALL ON FUNCTION "public"."vector_recv"("internal", "oid", integer) TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_recv"("internal", "oid", integer) TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_send"("public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_send"("public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_send"("public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_send"("public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_typmod_in"("cstring"[]) TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_typmod_in"("cstring"[]) TO "anon";
GRANT ALL ON FUNCTION "public"."vector_typmod_in"("cstring"[]) TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_typmod_in"("cstring"[]) TO "service_role";

GRANT ALL ON FUNCTION "public"."array_to_vector"(real[], integer, boolean) TO "postgres";
GRANT ALL ON FUNCTION "public"."array_to_vector"(real[], integer, boolean) TO "anon";
GRANT ALL ON FUNCTION "public"."array_to_vector"(real[], integer, boolean) TO "authenticated";
GRANT ALL ON FUNCTION "public"."array_to_vector"(real[], integer, boolean) TO "service_role";

GRANT ALL ON FUNCTION "public"."array_to_vector"(double precision[], integer, boolean) TO "postgres";
GRANT ALL ON FUNCTION "public"."array_to_vector"(double precision[], integer, boolean) TO "anon";
GRANT ALL ON FUNCTION "public"."array_to_vector"(double precision[], integer, boolean) TO "authenticated";
GRANT ALL ON FUNCTION "public"."array_to_vector"(double precision[], integer, boolean) TO "service_role";

GRANT ALL ON FUNCTION "public"."array_to_vector"(integer[], integer, boolean) TO "postgres";
GRANT ALL ON FUNCTION "public"."array_to_vector"(integer[], integer, boolean) TO "anon";
GRANT ALL ON FUNCTION "public"."array_to_vector"(integer[], integer, boolean) TO "authenticated";
GRANT ALL ON FUNCTION "public"."array_to_vector"(integer[], integer, boolean) TO "service_role";

GRANT ALL ON FUNCTION "public"."array_to_vector"(numeric[], integer, boolean) TO "postgres";
GRANT ALL ON FUNCTION "public"."array_to_vector"(numeric[], integer, boolean) TO "anon";
GRANT ALL ON FUNCTION "public"."array_to_vector"(numeric[], integer, boolean) TO "authenticated";
GRANT ALL ON FUNCTION "public"."array_to_vector"(numeric[], integer, boolean) TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_to_float4"("public"."vector", integer, boolean) TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_to_float4"("public"."vector", integer, boolean) TO "anon";
GRANT ALL ON FUNCTION "public"."vector_to_float4"("public"."vector", integer, boolean) TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_to_float4"("public"."vector", integer, boolean) TO "service_role";

GRANT ALL ON FUNCTION "public"."vector"("public"."vector", integer, boolean) TO "postgres";
GRANT ALL ON FUNCTION "public"."vector"("public"."vector", integer, boolean) TO "anon";
GRANT ALL ON FUNCTION "public"."vector"("public"."vector", integer, boolean) TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector"("public"."vector", integer, boolean) TO "service_role";

GRANT ALL ON FUNCTION "public"."cosine_distance"("public"."vector", "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."cosine_distance"("public"."vector", "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."cosine_distance"("public"."vector", "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."cosine_distance"("public"."vector", "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."get_user_email_by_user_id"("user_id" "uuid") TO "anon";
GRANT ALL ON FUNCTION "public"."get_user_email_by_user_id"("user_id" "uuid") TO "authenticated";
GRANT ALL ON FUNCTION "public"."get_user_email_by_user_id"("user_id" "uuid") TO "service_role";

GRANT ALL ON FUNCTION "public"."get_user_id_by_user_email"("user_email" "text") TO "anon";
GRANT ALL ON FUNCTION "public"."get_user_id_by_user_email"("user_email" "text") TO "authenticated";
GRANT ALL ON FUNCTION "public"."get_user_id_by_user_email"("user_email" "text") TO "service_role";

GRANT ALL ON FUNCTION "public"."hnswhandler"("internal") TO "postgres";
GRANT ALL ON FUNCTION "public"."hnswhandler"("internal") TO "anon";
GRANT ALL ON FUNCTION "public"."hnswhandler"("internal") TO "authenticated";
GRANT ALL ON FUNCTION "public"."hnswhandler"("internal") TO "service_role";

GRANT ALL ON FUNCTION "public"."inner_product"("public"."vector", "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."inner_product"("public"."vector", "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."inner_product"("public"."vector", "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."inner_product"("public"."vector", "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."ivfflathandler"("internal") TO "postgres";
GRANT ALL ON FUNCTION "public"."ivfflathandler"("internal") TO "anon";
GRANT ALL ON FUNCTION "public"."ivfflathandler"("internal") TO "authenticated";
GRANT ALL ON FUNCTION "public"."ivfflathandler"("internal") TO "service_role";

GRANT ALL ON FUNCTION "public"."l1_distance"("public"."vector", "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."l1_distance"("public"."vector", "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."l1_distance"("public"."vector", "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."l1_distance"("public"."vector", "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."l2_distance"("public"."vector", "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."l2_distance"("public"."vector", "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."l2_distance"("public"."vector", "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."l2_distance"("public"."vector", "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."match_summaries"("query_embedding" "public"."vector", "match_count" integer, "match_threshold" double precision) TO "anon";
GRANT ALL ON FUNCTION "public"."match_summaries"("query_embedding" "public"."vector", "match_count" integer, "match_threshold" double precision) TO "authenticated";
GRANT ALL ON FUNCTION "public"."match_summaries"("query_embedding" "public"."vector", "match_count" integer, "match_threshold" double precision) TO "service_role";

GRANT ALL ON FUNCTION "public"."match_vectors"("query_embedding" "public"."vector", "match_count" integer, "p_brain_id" "uuid") TO "anon";
GRANT ALL ON FUNCTION "public"."match_vectors"("query_embedding" "public"."vector", "match_count" integer, "p_brain_id" "uuid") TO "authenticated";
GRANT ALL ON FUNCTION "public"."match_vectors"("query_embedding" "public"."vector", "match_count" integer, "p_brain_id" "uuid") TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_accum"(double precision[], "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_accum"(double precision[], "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_accum"(double precision[], "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_accum"(double precision[], "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_add"("public"."vector", "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_add"("public"."vector", "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_add"("public"."vector", "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_add"("public"."vector", "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_avg"(double precision[]) TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_avg"(double precision[]) TO "anon";
GRANT ALL ON FUNCTION "public"."vector_avg"(double precision[]) TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_avg"(double precision[]) TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_cmp"("public"."vector", "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_cmp"("public"."vector", "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_cmp"("public"."vector", "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_cmp"("public"."vector", "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_combine"(double precision[], double precision[]) TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_combine"(double precision[], double precision[]) TO "anon";
GRANT ALL ON FUNCTION "public"."vector_combine"(double precision[], double precision[]) TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_combine"(double precision[], double precision[]) TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_dims"("public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_dims"("public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_dims"("public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_dims"("public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_eq"("public"."vector", "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_eq"("public"."vector", "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_eq"("public"."vector", "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_eq"("public"."vector", "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_ge"("public"."vector", "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_ge"("public"."vector", "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_ge"("public"."vector", "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_ge"("public"."vector", "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_gt"("public"."vector", "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_gt"("public"."vector", "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_gt"("public"."vector", "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_gt"("public"."vector", "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_l2_squared_distance"("public"."vector", "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_l2_squared_distance"("public"."vector", "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_l2_squared_distance"("public"."vector", "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_l2_squared_distance"("public"."vector", "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_le"("public"."vector", "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_le"("public"."vector", "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_le"("public"."vector", "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_le"("public"."vector", "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_lt"("public"."vector", "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_lt"("public"."vector", "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_lt"("public"."vector", "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_lt"("public"."vector", "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_mul"("public"."vector", "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_mul"("public"."vector", "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_mul"("public"."vector", "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_mul"("public"."vector", "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_ne"("public"."vector", "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_ne"("public"."vector", "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_ne"("public"."vector", "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_ne"("public"."vector", "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_negative_inner_product"("public"."vector", "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_negative_inner_product"("public"."vector", "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_negative_inner_product"("public"."vector", "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_negative_inner_product"("public"."vector", "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_norm"("public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_norm"("public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_norm"("public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_norm"("public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_spherical_distance"("public"."vector", "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_spherical_distance"("public"."vector", "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_spherical_distance"("public"."vector", "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_spherical_distance"("public"."vector", "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."vector_sub"("public"."vector", "public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."vector_sub"("public"."vector", "public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."vector_sub"("public"."vector", "public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."vector_sub"("public"."vector", "public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."avg"("public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."avg"("public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."avg"("public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."avg"("public"."vector") TO "service_role";

GRANT ALL ON FUNCTION "public"."sum"("public"."vector") TO "postgres";
GRANT ALL ON FUNCTION "public"."sum"("public"."vector") TO "anon";
GRANT ALL ON FUNCTION "public"."sum"("public"."vector") TO "authenticated";
GRANT ALL ON FUNCTION "public"."sum"("public"."vector") TO "service_role";

GRANT ALL ON TABLE "public"."api_keys" TO "anon";
GRANT ALL ON TABLE "public"."api_keys" TO "authenticated";
GRANT ALL ON TABLE "public"."api_keys" TO "service_role";

GRANT ALL ON TABLE "public"."brain_subscription_invitations" TO "anon";
GRANT ALL ON TABLE "public"."brain_subscription_invitations" TO "authenticated";
GRANT ALL ON TABLE "public"."brain_subscription_invitations" TO "service_role";

GRANT ALL ON TABLE "public"."brains" TO "anon";
GRANT ALL ON TABLE "public"."brains" TO "authenticated";
GRANT ALL ON TABLE "public"."brains" TO "service_role";

GRANT ALL ON TABLE "public"."brains_users" TO "anon";
GRANT ALL ON TABLE "public"."brains_users" TO "authenticated";
GRANT ALL ON TABLE "public"."brains_users" TO "service_role";

GRANT ALL ON TABLE "public"."brains_vectors" TO "anon";
GRANT ALL ON TABLE "public"."brains_vectors" TO "authenticated";
GRANT ALL ON TABLE "public"."brains_vectors" TO "service_role";

GRANT ALL ON TABLE "public"."chat_history" TO "anon";
GRANT ALL ON TABLE "public"."chat_history" TO "authenticated";
GRANT ALL ON TABLE "public"."chat_history" TO "service_role";

GRANT ALL ON TABLE "public"."chats" TO "anon";
GRANT ALL ON TABLE "public"."chats" TO "authenticated";
GRANT ALL ON TABLE "public"."chats" TO "service_role";

GRANT ALL ON TABLE "public"."knowledge" TO "anon";
GRANT ALL ON TABLE "public"."knowledge" TO "authenticated";
GRANT ALL ON TABLE "public"."knowledge" TO "service_role";

GRANT ALL ON TABLE "public"."knowledge_vectors" TO "anon";
GRANT ALL ON TABLE "public"."knowledge_vectors" TO "authenticated";
GRANT ALL ON TABLE "public"."knowledge_vectors" TO "service_role";

GRANT ALL ON TABLE "public"."migrations" TO "anon";
GRANT ALL ON TABLE "public"."migrations" TO "authenticated";
GRANT ALL ON TABLE "public"."migrations" TO "service_role";

GRANT ALL ON TABLE "public"."notifications" TO "anon";
GRANT ALL ON TABLE "public"."notifications" TO "authenticated";
GRANT ALL ON TABLE "public"."notifications" TO "service_role";

GRANT ALL ON TABLE "public"."prompts" TO "anon";
GRANT ALL ON TABLE "public"."prompts" TO "authenticated";
GRANT ALL ON TABLE "public"."prompts" TO "service_role";

GRANT ALL ON TABLE "public"."stats" TO "anon";
GRANT ALL ON TABLE "public"."stats" TO "authenticated";
GRANT ALL ON TABLE "public"."stats" TO "service_role";

GRANT ALL ON SEQUENCE "public"."stats_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."stats_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."stats_id_seq" TO "service_role";

GRANT ALL ON TABLE "public"."summaries" TO "anon";
GRANT ALL ON TABLE "public"."summaries" TO "authenticated";
GRANT ALL ON TABLE "public"."summaries" TO "service_role";

GRANT ALL ON SEQUENCE "public"."summaries_id_seq" TO "anon";
GRANT ALL ON SEQUENCE "public"."summaries_id_seq" TO "authenticated";
GRANT ALL ON SEQUENCE "public"."summaries_id_seq" TO "service_role";

GRANT ALL ON TABLE "public"."user_daily_usage" TO "anon";
GRANT ALL ON TABLE "public"."user_daily_usage" TO "authenticated";
GRANT ALL ON TABLE "public"."user_daily_usage" TO "service_role";

GRANT ALL ON TABLE "public"."user_identity" TO "anon";
GRANT ALL ON TABLE "public"."user_identity" TO "authenticated";
GRANT ALL ON TABLE "public"."user_identity" TO "service_role";

GRANT ALL ON TABLE "public"."user_settings" TO "anon";
GRANT ALL ON TABLE "public"."user_settings" TO "authenticated";
GRANT ALL ON TABLE "public"."user_settings" TO "service_role";

GRANT ALL ON TABLE "public"."vectors" TO "anon";
GRANT ALL ON TABLE "public"."vectors" TO "authenticated";
GRANT ALL ON TABLE "public"."vectors" TO "service_role";

ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON SEQUENCES  TO "service_role";

ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON FUNCTIONS  TO "service_role";

ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "postgres";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "anon";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "authenticated";
ALTER DEFAULT PRIVILEGES FOR ROLE "postgres" IN SCHEMA "public" GRANT ALL ON TABLES  TO "service_role";

RESET ALL;
