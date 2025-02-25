# --- Message Edge Queries ---
CREATE_MESSAGE_POSTED_IN_ROOM_QUERY = """
MATCH (m:Message {uuid: $message_uuid}), (r:Room {uuid: $room_uuid})
MERGE (m)-[p:POSTED_IN]->(r)
ON CREATE SET p.created_at = $created_at, p.updated_at = $updated_at
ON MATCH SET p.updated_at = $updated_at
RETURN m, p, r
"""

CREATE_MESSAGE_BELONGS_TO_CLUSTER_QUERY = """
MATCH (m:Message {uuid: $message_uuid}), (c:Cluster {uuid: $cluster_uuid})
MERGE (m)-[b:BELONGS_TO]->(c)
ON CREATE SET b.created_at = $created_at, b.updated_at = $updated_at
ON MATCH SET b.updated_at = $updated_at
RETURN m, b, c
"""

# --- User Edge Queries ---
CREATE_USER_BELONGS_TO_ROOM_QUERY = """
MATCH (u:User {uuid: $user_uuid}), (r:Room {uuid: $room_uuid})
MERGE (u)-[b:BELONGS_TO]->(r)
ON CREATE SET b.created_at = $created_at, b.updated_at = $updated_at
ON MATCH SET b.updated_at = $updated_at
RETURN u, b, r
"""

CREATE_USER_POSTED_IN_ROOM_QUERY = """
MATCH (u:User {uuid: $user_uuid}), (r:Room {uuid: $room_uuid})
MERGE (u)-[p:POSTED_IN]->(r)
ON CREATE SET p.created_at = $created_at, p.updated_at = $updated_at
ON MATCH SET p.updated_at = $updated_at
RETURN u, p, r
"""

# --- Topic Edge Queries ---
CREATE_CLUSTER_RELATED_TO_TOPIC_QUERY = """
MATCH (c:Cluster {uuid: $cluster_uuid}), (t:Entity {uuid: $topic_uuid})
MERGE (c)-[r:RELATED_TO]->(t)
ON CREATE SET r.created_at = $created_at, r.updated_at = $updated_at
ON MATCH SET r.updated_at = $updated_at
RETURN c, r, t
"""

CREATE_USER_RELATED_TO_TOPIC_QUERY = """
MATCH (u:User {uuid: $user_uuid}), (t:Entity {uuid: $topic_uuid})
MERGE (u)-[r:RELATED_TO]->(t)
ON CREATE SET r.created_at = $created_at, r.updated_at = $updated_at
ON MATCH SET r.updated_at = $updated_at
RETURN u, r, t
"""

CREATE_ROOM_RELATED_TO_TOPIC_QUERY = """
MATCH (r:Room {uuid: $room_uuid}), (t:Entity {uuid: $topic_uuid})
MERGE (r)-[r:RELATED_TO]->(t)
ON CREATE SET r.created_at = $created_at, r.updated_at = $updated_at
ON MATCH SET r.updated_at = $updated_at
RETURN r, r, t
"""
