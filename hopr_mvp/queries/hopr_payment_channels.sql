WITH nodes_with_open_channel AS (
    SELECT *
    FROM hopr_network_gnosis.HoprChannelsDufour_evt_ChannelOpened
    --WHERE evt_block_time >= CAST('2023-09-15 00:00' AS TIMESTAMP)
),

channel_balance_increased_evt AS (
    SELECT channelId, evt_tx_hash
    FROM hopr_network_gnosis.HoprChannelsDufour_evt_ChannelBalanceIncreased
), 

open_channels AS (
    SELECT * 
    FROM nodes_with_open_channel
    LEFT JOIN channel_balance_increased_evt
    ON nodes_with_open_channel.evt_tx_hash = channel_balance_increased_evt.evt_tx_hash
),

unique_open_channels AS (
    SELECT source, destination, evt_block_time AS time_opened, channelId, evt_block_number, evt_index 
    FROM (
        SELECT *, row_number() OVER (PARTITION BY channelId ORDER BY evt_block_number DESC, evt_index DESC) AS pos
        FROM open_channels 
    )
    WHERE pos = 1
),

closed_channels AS (
    SELECT *
    FROM hopr_network_gnosis.HoprChannelsDufour_evt_ChannelClosed
),

unique_closed_channels AS (
    SELECT channelId, evt_block_time AS time_closed, evt_block_number, evt_index
    FROM (
        SELECT *, row_number() OVER (PARTITION BY channelId ORDER BY evt_block_number DESC, evt_index DESC) AS pos
        FROM closed_channels 
    )
    WHERE pos = 1
),

open_closed_channels AS (
    SELECT 
        source, destination, time_opened, unique_open_channels.channelId, time_closed, 
        unique_open_channels.evt_block_number as open_blk_num, unique_open_channels.evt_index as open_index,
        unique_closed_channels.evt_block_number as close_blk_num, unique_closed_channels.evt_index as close_index
    FROM unique_open_channels 
    LEFT JOIN unique_closed_channels 
    ON unique_open_channels.channelId = unique_closed_channels.channelId
),
/*
current_open_channels AS (
    SELECT *
    FROM (
        SELECT *,
        CASE WHEN (time_opened > time_closed OR time_closed IS NULL) THEN 1 ELSE 0 END AS channel_status
        FROM open_closed_channels
    )
    WHERE channel_status = 1 
)
*/

current_channels_status AS (
    SELECT *,
    CASE WHEN (
        open_blk_num > close_blk_num OR 
        time_closed IS NULL OR 
        (open_blk_num = close_blk_num AND open_index > close_index)
    ) THEN 1 ELSE 0 END AS channel_status
    FROM open_closed_channels
)
/*
SELECT source, destination, time_opened, channelId
FROM current_open_channels
ORDER BY time_opened DESC
*/
SELECT 
    source, destination, "channelId",
    CASE channel_status WHEN 1 THEN true ELSE false END AS is_channel_opened,
    time_opened, time_closed
FROM current_channels_status