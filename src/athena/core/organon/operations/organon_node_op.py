# --- Create Queries ---
CREATE_USER_NODE_QUERY = """
MERGE (u:User {uuid: $uuid})
ON CREATE SET u = {
    uuid: $uuid,
    user_id: $user_id,
    platform_handles: $platform_handles,
    name: $name,
    platform: $platform,
    summary: $summary,
    classification: $classification,
    last_summary_update: $last_summary_update,
    created_at: $created_at,
    updated_at: $updated_at
}
ON MATCH SET u += {
    user_id: $user_id,
    platform_handles: $platform_handles,
    name: $name,
    platform: $platform,
    summary: $summary,
    classification: $classification,
    last_summary_update: $last_summary_update,
    updated_at: $updated_at
}
RETURN u
"""

CREATE_ROOM_NODE_QUERY = """
MERGE (r:Room {uuid: $uuid})
ON CREATE SET r = {
    uuid: $uuid,
    room_id: $room_id,
    platform: $platform,
    name: $name,
    room_type: $room_type,
    community_id: $community_id,
    summary: $summary,
    created_at: $created_at,
    updated_at: $updated_at
}
ON MATCH SET r += {
    room_id: $room_id,
    platform: $platform,
    name: $name,
    room_type: $room_type,
    community_id: $community_id,
    summary: $summary,
    updated_at: $updated_at
}
RETURN r
"""

CREATE_MESSAGE_NODE_QUERY = """
MERGE (m:Message {uuid: $uuid})
ON CREATE SET m = {
    uuid: $uuid,
    message_id: $message_id,
    room_id: $room_id,
    user_id: $user_id,
    platform: $platform,
    content: $content,
    engagement_score: $engagement_score,
    embedding: $embedding,
    created_at: $created_at,
    updated_at: $updated_at
}
ON MATCH SET m += {
    room_id: $room_id,
    user_id: $user_id,
    platform: $platform,
    content: $content,
    engagement_score: $engagement_score,
    embedding: $embedding,
    updated_at: $updated_at
}
RETURN m
"""

CREATE_CLUSTER_NODE_QUERY = """
MERGE (c:Cluster {uuid: $uuid})
ON CREATE SET c = {
    uuid: $uuid,
    room_id: $room_id,
    start_time: $start_time,
    end_time: $end_time,
    keywords: $keywords,
    messages: $messages,
    embeddings: $embeddings,
    platform: $platform,
    created_at: $created_at,
    updated_at: $updated_at
}
ON MATCH SET c += {
    room_id: $room_id,
    start_time: $start_time,
    end_time: $end_time,
    keywords: $keywords,
    messages: $messages,
    embeddings: $embeddings,
    platform: $platform,
    updated_at: $updated_at
}
RETURN c
"""

CREATE_COMMUNITY_NODE_QUERY = """
MERGE (c:Community {uuid: $uuid})
ON CREATE SET c = {
    uuid: $uuid,
    community_id: $community_id,
    name: $name,
    description: $description,
    created_at: $created_at,
    updated_at: $updated_at,
    platform: $platform
}
ON MATCH SET c += {
    community_id: $community_id,
    name: $name,
    description: $description,
    updated_at: $updated_at,
    platform: $platform
}
RETURN c
"""

CREATE_ENTITY_NODE_QUERY = """
MERGE (e:Entity {uuid: $uuid})
ON CREATE SET e = {
    uuid: $uuid,
    name: $name,
    entity_type: $entity_type,
    embedding: $embedding,
    created_at: $created_at,
    updated_at: $updated_at,
    platform: $platform
}
ON MATCH SET e += {
    name: $name,
    entity_type: $entity_type,
    embedding: $embedding,
    updated_at: $updated_at,
    platform: $platform
}
RETURN e
"""

CREATE_PREFERENCE_NODE_QUERY = """
MERGE (p:Preference {uuid: $uuid})
ON CREATE SET p = {
    uuid: $uuid,
    preference_id: $preference_id,
    preference_type: $preference_type,
    description: $description,
    embedding: $embedding,
    created_at: $created_at,
    updated_at: $updated_at,
    platform: $platform
}
ON MATCH SET p += {
    preference_id: $preference_id,
    preference_type: $preference_type,
    description: $description,
    embedding: $embedding,
    updated_at: $updated_at,
    platform: $platform
}
RETURN p
"""

# --- Fetch Queries ---
FETCH_USER_NODE_QUERY = """
MATCH (u:User {uuid: $uuid})
RETURN u
"""

FETCH_ROOM_NODE_QUERY = """
MATCH (r:Room {uuid: $uuid})
RETURN r
"""

FETCH_MESSAGE_NODE_QUERY = """
MATCH (m:Message {uuid: $uuid})
RETURN m
"""

FETCH_CLUSTER_NODE_QUERY = """
MATCH (c:Cluster {uuid: $uuid})
RETURN c
"""

FETCH_COMMUNITY_NODE_QUERY = """
MATCH (c:Community {uuid: $uuid})
RETURN c
"""

FETCH_ENTITY_NODE_QUERY = """
MATCH (e:Entity {uuid: $uuid})
RETURN e
"""

FETCH_PREFERENCE_NODE_QUERY = """
MATCH (p:Preference {uuid: $uuid})
RETURN p
"""

FETCH_USERS_NODE_QUERY = """
MATCH (u:User)
WHERE u.uuid IN $uuids
RETURN u
"""

FETCH_ROOMS_NODE_QUERY = """
MATCH (r:Room)
WHERE r.uuid IN $uuids
RETURN r
"""

FETCH_MESSAGES_NODE_QUERY = """
MATCH (m:Message)
WHERE m.uuid IN $uuids
RETURN m
"""

FETCH_CLUSTERS_NODE_QUERY = """
MATCH (c:Cluster)
WHERE c.uuid IN $uuids
RETURN c
"""

FETCH_COMMUNITIES_NODE_QUERY = """
MATCH (c:Community)
WHERE c.uuid IN $uuids
RETURN c
"""

FETCH_ENTITIES_NODE_QUERY = """
MATCH (e:Entity)
WHERE e.uuid IN $uuids
RETURN e
"""

FETCH_PREFERENCES_NODE_QUERY = """
MATCH (p:Preference)
WHERE p.uuid IN $uuids
RETURN p
"""

