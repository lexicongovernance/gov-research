/* Active forum participants in a given time interval */ 

-- [params]
-- text :interval = 100 days

WITH proposal_category AS (
    SELECT id AS proposal_category_id
    FROM categories
    -- WHERE id IN (67, 68) -- comment out for specific categories
),

topics_in_category AS (
    -- get all the topics within the category
    -- exclude the deleted topics
    SELECT 
        topics.id AS topic_id, title, views, posts_count, highest_post_number, reply_count, like_count,
        incoming_link_count, category_id, topics.slug AS topics_slug, participant_count
    FROM topics
    WHERE category_id IN (
        SELECT proposal_category_id FROM proposal_category
    )
    AND deleted_at IS NULL -- filter deleted topics
),

posts_in_category AS (
    -- get all the posts (incl. proposal posts and replies) in the given category
    SELECT id AS post_id, topic_id, user_id, post_number, updated_at,
    like_count, reads, word_count 
    FROM posts
    WHERE topic_id IN (
        SELECT topic_id FROM topics_in_category
    )
    AND deleted_at IS NULL -- filter deleted posts
    AND updated_at >= CURRENT_TIMESTAMP - INTERVAL :interval
),

proposals AS (
    -- all the proposal posts that are in a given category
    SELECT id AS post_id, topic_id, post_number, 
    like_count, reads, word_count 
    FROM posts
    WHERE topic_id IN (
        SELECT topic_id FROM topics_in_category
    )
    AND post_number = 1 -- due to likes counting as signatures
    AND updated_at >= CURRENT_TIMESTAMP - INTERVAL :interval
),

proposal_likers AS (
    -- users who liked proposals
    SELECT user_id 
    FROM post_actions
    WHERE post_id IN (
        SELECT post_id FROM proposals
    )
    AND post_action_type_id = 2 -- likes
    AND deleted_at IS NULL -- filter deleted likes
    AND updated_at >= CURRENT_TIMESTAMP - INTERVAL :interval
),

post_writers AS (
    -- users who created posts including replies
    SELECT user_id FROM posts_in_category
),

eligible_users AS (
    SELECT user_id, admin FROM (
        SELECT user_id FROM proposal_likers
        UNION
        SELECT user_id FROM post_writers 
        post_writers
    ) user_with_right_actions
    LEFT JOIN users
    ON user_with_right_actions.user_id = users.id
    WHERE admin = false -- remove admins
),

/* Merge user addresses */
eligible_users_addresses AS (
    SELECT eligible_users.user_id, w.value  
    FROM eligible_users
    LEFT JOIN (
        SELECT * 
        FROM user_custom_fields
        WHERE name = 'user_field_3' -- evm_address
    ) AS w
    ON eligible_users.user_id = w.user_id
)

SELECT *
FROM eligible_users_addresses