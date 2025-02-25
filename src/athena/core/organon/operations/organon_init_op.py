ORGANON_INIT_QUERIES = [
    # # --- Node Constraints (Uniqueness) ---
    # # User: user_id is globally unique (we'll handle generation)
    # "CREATE CONSTRAINT user_user_id_unique IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE",
    # # Room: room_id is globally unique
    # "CREATE CONSTRAINT room_room_id_unique IF NOT EXISTS FOR (r:Room) REQUIRE r.room_id IS UNIQUE",
    # # Message: message_id is globally unique
    # "CREATE CONSTRAINT message_message_id_unique IF NOT EXISTS FOR (m:Message) REQUIRE m.message_id IS UNIQUE",
    # # Cluster: cluster_id is globally unique
    # "CREATE CONSTRAINT cluster_cluster_id_unique IF NOT EXISTS FOR (c:Cluster) REQUIRE c.cluster_id IS UNIQUE",
    # # Community: community_id is globally unique
    # "CREATE CONSTRAINT community_community_id_unique IF NOT EXISTS FOR (c:Community) REQUIRE c.community_id IS UNIQUE",
    # # Entity: uuid is globally unique
    # "CREATE CONSTRAINT entity_uuid_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.uuid IS UNIQUE",
    # # Preference: preference_id is globally unique
    # "CREATE CONSTRAINT preference_preference_id_unique IF NOT EXISTS FOR (p:Preference) REQUIRE p.preference_id IS UNIQUE",
    # # --- Node Indexes ---
    # "CREATE INDEX user_user_id_index IF NOT EXISTS FOR (u:User) ON (u.user_id)",
    # "CREATE INDEX room_room_id_index IF NOT EXISTS FOR (r:Room) ON (r.room_id)",
    # "CREATE INDEX message_message_id_index IF NOT EXISTS FOR (m:Message) ON (m.message_id)",
    # "CREATE INDEX message_date_index IF NOT EXISTS FOR (m:Message) ON (m.created_at)",
    # "CREATE INDEX room_type_index IF NOT EXISTS FOR (r:Room) ON (r.room_type)",
    # "CREATE INDEX room_platform_index IF NOT EXISTS FOR (r:Room) ON (r.platform)",
    # "CREATE INDEX message_platform_index IF NOT EXISTS FOR (m:Message) ON (m.platform)",
    # "CREATE INDEX community_community_id_index IF NOT EXISTS FOR (c:Community) ON (c.community_id)",
    # # --- Vector Index (for Message Embeddings) ---
    # """
    #             CREATE VECTOR INDEX message_embeddings IF NOT EXISTS
    #             FOR (m:Message) ON (m.embedding)
    #             OPTIONS {
    #                 indexConfig: {
    #                     `vector.similarity_function`: 'cosine'
    #                 }
    #             }
    #         """,
    # # --- Vector Index (for Entity Name Embeddings) ---
    # """
    #             CREATE VECTOR INDEX entity_name_embeddings IF NOT EXISTS
    #             FOR (e:Entity) ON (e.embedding)
    #             OPTIONS {indexConfig: {
    #                 `vector.similarity_function`: 'cosine'
    #             }}
    #         """,
    # # --- Vector Index (for Preference description Embeddings) ---
    # """
    #             CREATE VECTOR INDEX preference_description_embeddings IF NOT EXISTS
    #             FOR (p:Preference) ON (p.embedding)
    #             OPTIONS {indexConfig: {
    #                 `vector.similarity_function`: 'cosine'
    #             }}
    #         """,
]

CLEAR_ORGANON_QUERIES = [
    "MATCH (n) DETACH DELETE n",
]

GET_INDEXES_QUERY = "SHOW INDEXES"
GET_CONSTRAINTS_QUERY = "SHOW CONSTRAINTS"

DROP_INDEX_QUERY = "DROP INDEX {name} IF EXISTS"
DROP_CONSTRAINT_QUERY = "DROP CONSTRAINT {name} IF EXISTS"
