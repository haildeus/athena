### Schema Structure

#### Understanding the Nodes
- **User**: Represents either the host-user or other users in chats. The host-user is central, but other users’ data may be relevant.
- **Room**: Represents chat rooms or conversation.
- **Message**: Individual messages posted within rooms.
- **Cluster**: Groups of aggregated and prioritized messages, likely based on importance or relevance to the host-user.
- **Community**: A group of users, possibly sharing interests or interactions, though not fully defined in the query.
- **Entity**: Any person, product, topic, or object mentioned in messages or clusters (e.g., “pizza,” “Paris”).
- **Preference**: Captures the host-user’s (or potentially other users’) likes, dislikes, goals, values, or habits (e.g., “likes pizza,” “goal: learn French”).

#### Understanding the Edges
- **Posts**: PostsUser → Message.
- **Posted in**: Message → Room.
- **Mentions**: Message → Entity.
- **Includes**: Cluster → Message.
- **Belongs to**: User → Community.
- **Participates in**: User → Room.
- **Related to**: Entity → Entity.
- **Has preference**: User → Preference.
- **For**: Preference → Entity.












