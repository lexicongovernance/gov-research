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
