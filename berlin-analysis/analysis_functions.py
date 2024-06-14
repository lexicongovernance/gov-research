"""
This file contains analysis functions for the data analysis of the berlin event
"""
import math
from itertools import combinations

def get_latest_vote_by_user_and_optionid(df, option_id):
    """
    Gets the latest vote data by users for a specified option ID.
    :param: df (pandas.DataFrame): The DataFrame containing the vote data.
    :param: option_id (str): The ID of the option for which to query vote data.
    """
    # Filter the DataFrame by option_id
    filtered_df = df[df['option_id'] == option_id].copy()

    # Rank each user by updated_at in descending order
    filtered_df['rank'] = filtered_df.groupby('user_id')['updated_at'].rank(method='first', ascending=False)

    # Select the latest vote for each user
    latest_votes = filtered_df[filtered_df['rank'] == 1]

    # Create a dictionary from the DataFrame
    vote_dict = latest_votes.set_index('user_id')['num_of_votes'].to_dict()

    return vote_dict

def filter_zero_votes(vote_dict):
    """
    Filters out zero votes from the dictionary.
    
    :param vote_dict: dict - A dictionary with user IDs as keys and their number of votes as values.
    :return: dict - A dictionary with zero votes removed.
    """
    # Filter out entries with zero votes
    filtered_dict = {user_id: votes for user_id, votes in vote_dict.items() if votes != 0}
    return filtered_dict

def get_groups_by_user_and_optionid(df, num_of_votes_dictionary, group_categories):
    """
    Gets group data and creates group dictionary based on user IDs and option ID.
    :param: df (pandas.DataFrame): The DataFrame containing the group data.
    :param: numOfVotesDictionary (dict): Dictionary of user IDs and their respective number of votes.
    :param: groupCategories (list of str): Array of group category IDs.
    """

    # Filter users_to_groups DataFrame by user IDs and group category IDs
    filtered_df = df[df['user_id'].isin(num_of_votes_dictionary.keys()) & df['group_category_id'].isin(group_categories)]

    # Group by group_id and aggregate user_ids into a list
    group_array = filtered_df.groupby('group_id')['user_id'].agg(list).reset_index()

    # Convert group_array DataFrame to dictionary
    groups_dictionary = dict(zip(group_array['group_id'], group_array['user_id']))

    return groups_dictionary

def create_group_memberships(groups):
    """
    Define group memberships for each participant.
    :param: groups (list of lists): a list denotes the group and contains its members. 
    :param: votes (list): number of participant's votes for a given project proposal.
    :returns (list of lists): retunrs a list of group membersips for each participant.  
    """
    memberships = {}
    for group, members in groups.items():
        for member in members:
            memberships.setdefault(member, []).append(group)
    return memberships

def get_group_categories_ids(df, names):
    """
    Filter the DataFrame to include only rows where the 'name' column matches any of the provided names.
    :param: df (pd.DataFrame): The DataFrame containing group categories.
    :param: names (list): A list of names to filter by.
    :returns: list: A list containing the filtered 'id' column.
    """
    filter_condition = df['name'].isin(names)
    filtered_df = df[filter_condition]['id'].tolist()
    return filtered_df

def remove_duplicate_groups(input_groups: dict[str, list[str]]) -> dict[str, list[str]]:
    ''' 
     Removes duplicate groups from the input array of groups.
     :param: inputGroups An array of groups (can contain duplicates).
    '''
    unique_groups = {}

    for group_name, users in input_groups.items():
        # Sort the user arrays to ensure order doesn't matter
        sorted_users = sorted(users)

        # Check if the sorted array is not already in unique_groups
        if not any(sorted(existing_group) == sorted_users for existing_group in unique_groups.values()):
            unique_groups[group_name] = sorted_users

    return unique_groups

def connection_oriented_cluster_match(groups, votes):
    """
    Calculate a score representing the connection-oriented clustering match between groups.
    :param: groups (dict): A dictionary where keys are group names and values are lists of members in each group.
    :param: votes (dict): A dictionary where keys are user IDs and values are their corresponding votes.
    :returns: float: The connection-oriented cluster match score.
    """
    # memberships[i] is the number of groups agent i is in
    memberships = {user: sum(user in members for members in groups.values()) for user in votes.keys()}

    # friend_matrix[i][j] is the number of groups that agent i and j are both in
    friend_matrix = {
        user1: {user2: sum(user1 in members and user2 in members for members in groups.values()) for user2 in votes.keys()}
        for user1 in votes.keys()
    }

    qf_score = sum(votes.values())

    def k_function(user, h):
        if sum(friend_matrix[user][other_user] for other_user in h) > 0:
            return math.sqrt(votes[user])
        return votes[user]

    qf_score += sum(
        2 * math.sqrt(sum(k_function(user, groups[group1]) / memberships[user] for user in groups[group0]))
        * math.sqrt(sum(k_function(other_user, groups[group0]) / memberships[other_user] for other_user in groups[group1]))
        for group0, group1 in combinations(groups.keys(), 2)
    )

    qv_score = math.sqrt(qf_score)
    return qv_score

def get_results_dict(option_ids, vote_data, group_data, group_categories_data, group_categories_names):
    """
    Compute various scores for each option ID based on voting and group data, and return the results in a dictionary.
    :param: optionIds (list): A list of option IDs to process.
    :param: voteData (DataFrame): A DataFrame containing voting data.
    :param: groupData (DataFrame): A DataFrame containing group membership data.
    :param: groupCategories (DataFrame): A DataFrame containing group category information.
    :param: group_categories (list): A list of group category names that should be considered for the computation.
    :returns: dict: A dictionary where each key is an option ID and the value is another dictionary containing:
        - totalRawVotes (int): The sum of all votes for the option.
        - quadraticScore (float): The quadratic voting score for the option.
        - pluralityScore (float): The score based on connection-oriented cluster match.
    """
    results_dict = {}

    for option_id in option_ids:
        vote_dict = get_latest_vote_by_user_and_optionid(vote_data, option_id)
        filtered_vote_dict = filter_zero_votes(vote_dict)
        total_raw_votes = sum(vote_dict.values())
        quadratic_score = sum(math.sqrt(value) for value in vote_dict.values())
        group_categories_ids = get_group_categories_ids(group_categories_data, group_categories_names)
        group_dict = get_groups_by_user_and_optionid(group_data, filtered_vote_dict, group_categories_ids)
        filtered_groups = remove_duplicate_groups(group_dict)
        plurality_score = connection_oriented_cluster_match(filtered_groups, filtered_vote_dict)
        results_dict[option_id] = {
            'totalRawVotes': total_raw_votes,
            'quadraticScore': quadratic_score,
            'pluralityScore': plurality_score,
        }
    return results_dict

def get_results_dict_with_duplicates(option_ids, vote_data, group_data, group_categories_data, group_categories_names):
    """
    Compute various scores for each option ID based on voting and group data, and return the results in a dictionary.
    :param: optionIds (list): A list of option IDs to process.
    :param: voteData (DataFrame): A DataFrame containing voting data.
    :param: groupData (DataFrame): A DataFrame containing group membership data.
    :param: groupCategories (DataFrame): A DataFrame containing group category information.
    :param: group_categories (list): A list of group category names that should be considered for the computation.
    :returns: dict: A dictionary where each key is an option ID and the value is another dictionary containing:
        - totalRawVotes (int): The sum of all votes for the option.
        - quadraticScore (float): The quadratic voting score for the option.
        - pluralityScore (float): The score based on connection-oriented cluster match.
    """
    results_dict = {}

    for option_id in option_ids:
        vote_dict = get_latest_vote_by_user_and_optionid(vote_data, option_id)
        filtered_vote_dict = filter_zero_votes(vote_dict)
        total_raw_votes = sum(vote_dict.values())
        quadratic_score = sum(math.sqrt(value) for value in vote_dict.values())
        group_categories_ids = get_group_categories_ids(group_categories_data, group_categories_names)
        group_dict = get_groups_by_user_and_optionid(group_data, filtered_vote_dict, group_categories_ids)
        plurality_score = connection_oriented_cluster_match(group_dict, filtered_vote_dict)
        results_dict[option_id] = {
            'totalRawVotes': total_raw_votes,
            'quadraticScore': quadratic_score,
            'pluralityScore': plurality_score,
        }
    return results_dict

def merge_dicts(dict1, dict2):
    """
    Function to merge two dictionaries.
    """
    merged_dict = {}
    for key in dict1.keys():
        merged_values = {}
        for sub_key in dict1[key]:
            merged_values[sub_key] = dict1[key][sub_key]
        for sub_key in dict2[key]:
            merged_values[sub_key + "Comparison"] = dict2[key][sub_key]
        merged_dict[key] = merged_values
    return merged_dict

def calculate_ranks(results_dict):
    """
    Calculate and update ranks for each value across all options in the results dictionary.
    :param: results_dict (dict): A dictionary where each key is an option ID and the value is another dictionary containing:
        - totalRawVotes (int): The sum of all votes for the option.
        - quadraticScore (float): The quadratic voting score for the option.
        - pluralityScore (float): The score based on connection-oriented cluster match.

    Returns:
    dict: The updated results dictionary with ranks added to each score.
    """
    # Sort the options based on each score in descending order
    total_raw_votes_sorted = sorted(results_dict.items(), key=lambda x: x[1]['totalRawVotes'], reverse=True)
    quadratic_score_sorted = sorted(results_dict.items(), key=lambda x: x[1]['quadraticScore'], reverse=True)
    result_sorted = sorted(results_dict.items(), key=lambda x: x[1]['pluralityScore'], reverse=True)

    # Calculate ranks for each option based on sorted scores
    total_raw_votes_ranks = {option[0]: rank + 1 for rank, option in enumerate(total_raw_votes_sorted)}
    quadratic_score_ranks = {option[0]: rank + 1 for rank, option in enumerate(quadratic_score_sorted)}
    result_ranks = {option[0]: rank + 1 for rank, option in enumerate(result_sorted)}

    # Update the results_dict with ranks for each score
    for option in results_dict:
        results_dict[option]['totalRawVotes'] = {
            'score': results_dict[option]['totalRawVotes'], 
            'rank': total_raw_votes_ranks[option]
        }
        results_dict[option]['quadraticScore'] = {
            'score': results_dict[option]['quadraticScore'], 
            'rank': quadratic_score_ranks[option]
        }
        results_dict[option]['pluralityScore'] = {
            'score': results_dict[option]['pluralityScore'], 
            'rank': result_ranks[option]
        }

    return results_dict
