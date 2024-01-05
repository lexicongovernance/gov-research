/* Hopr node safes overview  */ 
/* %%%%%%%%%%%%%%%%%%%%%%%% */

/* Deployed hopr node safes */
WITH new_hopr_node_safe AS (
    SELECT instance AS safe_address  
    FROM hopr_network_gnosis.HoprNodeStakeFactoryDufour_evt_NewHoprNodeStakeSafe
), 

/* Registered hopr node safes */
registered_node_safes AS (
    SELECT nodeAddress AS node_address, stakingAccount AS safe_address, evt_block_time AS date_registration
    FROM hopr_network_gnosis.HoprNetworkRegistryDufour_evt_RegisteredByManager
),

node_safes AS (
    SELECT new_hopr_node_safe.safe_address, registered_node_safes.node_address, registered_node_safes.date_registration
    FROM new_hopr_node_safe
    LEFT JOIN registered_node_safes
    ON new_hopr_node_safe.safe_address = registered_node_safes.safe_address
)

SELECT *
FROM node_safes
ORDER BY date_registration DESC