/* HOPR Token holders */ 

WITH hopr_token_addresses AS (
    SELECT * FROM unnest(ARRAY[
        CAST(0xF5581dFeFD8Fb0e4aeC526bE659CFaB1f8c781dA AS varbinary), -- HOPR Token on Ethereum Chain 
        CAST(0xD057604A14982FE8D88c5fC25Aac3267eA142a08 AS varbinary), -- HOPR Token on Gnosis Chain
        CAST(0xD4fdec44DB9D44B8f2b6d529620f9C0C7066A2c1 AS varbinary)  -- w(HOPR Token on Gnosis Chain)
    ], ARRAY [
        'HOPR', 'xHOPR', 'wxHOPR'  
    ], ARRAY [
        '18', '18', '18'
    ]) AS t(address, symbol, decimals)
),

example_accounts AS (
    SELECT CAST(address AS varbinary) AS address
    FROM dune.lexicon.dataset_elidgible_addresses
),

/*
example_accounts AS (
    SELECT * FROM unnest(ARRAY[
        CAST(0x217a6d29abbaceafb36207b4cb25acc148e1fc65 AS varbinary), 
        CAST(0xd9a00176cf49dfb9ca3ef61805a2850f45cb1d05 AS varbinary),
        CAST(0xcd1a97453e3525019cdfa66fb669576fafb2c527 AS varbinary), 
        CAST(0x8832376a388cfcb58dab0cce249f65b86041e4bc AS varbinary)
    ]) AS t(address)
),
*/

token_transfers_ethereum AS (
    SELECT "from", "to", contract_address, value, 'ethereum' AS blockchain 
    FROM erc20_ethereum.evt_Transfer 
    WHERE ("from" IN (SELECT address FROM example_accounts)  OR "to" IN (SELECT address FROM example_accounts))
),

token_transfers_gnosis AS (
    SELECT "from", "to", contract_address, value, 'gnosis' AS blockchain 
    FROM erc20_gnosis.evt_Transfer
    WHERE ("from" IN (SELECT address FROM example_accounts)  OR "to" IN (SELECT address FROM example_accounts))
),

token_transfers AS (
    SELECT "from", "to", contract_address, CAST(value AS DECIMAL(38,0)) AS value,
    symbol, CAST(decimals AS INTEGER) AS decimals, blockchain
    FROM (
        SELECT * 
        FROM token_transfers_ethereum
        UNION ALL
        SELECT * 
        FROM token_transfers_gnosis
    ) AS subquery
    LEFT JOIN hopr_token_addresses
    ON subquery.contract_address = hopr_token_addresses.address
),

/* Adjust value column */ 
adjusted_value AS (
    SELECT "from", "to",
    CASE WHEN ("from" IN (SELECT address FROM example_accounts)) THEN -value/power(10, decimals) ELSE value/power(10, decimals) END AS amount,
    contract_address, symbol, blockchain
    FROM token_transfers
    WHERE contract_address IN (SELECT address FROM hopr_token_addresses)
),

/* Aggregate balances by wallet address (uncomment to aggregate by token) */ 
aggregated_balances AS (
    SELECT wallet, SUM(balance) AS total_hopr_balance --, token 
    FROM (  
        SELECT "from" AS wallet, SUM(amount) AS balance -- symbol AS token
        FROM adjusted_value
        WHERE ("from" IN (SELECT address FROM example_accounts))
        GROUP BY "from" --, symbol
        UNION ALL
        SELECT "to" AS wallet, SUM(ABS(amount)) AS balance -- symbol AS token
        FROM adjusted_value
        WHERE ("to" IN (SELECT address FROM example_accounts))
        GROUP BY "to" --, symbol
    ) AS subquery 
    GROUP BY wallet --, token  
),

/* Import safe and node address from list_hopr_node_safe query */
hopr_safes AS (
    SELECT safe_address, node_address 
    FROM query_3240903 -- query Id identifies the query 
),

/* Indicator whether a wallet is a safe */ 
aggregated_balances_hopr_safes AS (
    SELECT *,
        CASE WHEN (wallet IN (SELECT safe_address FROM hopr_safes)) THEN 'Yes' ELSE 'No' END AS is_hopr_safe
    FROM aggregated_balances
)

/* merge node address in case the safe has a registered node */
SELECT wallet, total_hopr_balance, is_hopr_safe, node_address 
FROM aggregated_balances_hopr_safes
LEFT JOIN hopr_safes 
ON aggregated_balances_hopr_safes.wallet = hopr_safes.safe_address


/* Import safe and node address from list_hopr_node_safe query */
--SELECT safe_address, node_address 
--FROM query_3240903 -- query Id identifies the query 