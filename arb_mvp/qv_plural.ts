function createGroupMemberships(groups: number[][]): number[][] {
    // Define group memberships for each participant.
    // :param: groups (list of lists): a list denotes the group and contains its members. 
    // :returns (list of lists): retunrs a list of group membersips for each participant.  
    
    const memberships: number[][] = new Array(groups.length).fill([]);
  
    for (let i = 0; i < groups.length; i++) {
      for (let j of groups[i]) {
        memberships[j] = [...memberships[j], i];
      }
    }
  
    return memberships;
}

function commonGroup(i: number, j: number, groupMemberships: number[][]): boolean {
    // Define an identifyer indicating whether two participants share the same group or whehter any 
    // other member of the group of the second agent shares a group with the first agent. 
    // :param: i: agent_i denotes a participant not equal to a participant called agent_j. 
    // :param: j: agent_j denotes a participant not equal to a participant called agent_i.
    // :returns (bool): returns true if two participants share a common group and false otherwise.  

    return groupMemberships[i].some(group => groupMemberships[j].includes(group));
}
  
function K(i: number, group: number[], groupMemberships: number[][], contributions: number[]): number {
    // Define the weighting function that attenuates the votes of agent i given different group memberships.  
    // :param: agent_i denotes a participant not equal to a participant called agent_j.
    // :param: group: group denotes the other group.
    // :returns: attenuated number of votes for a given project. 

    if (group.includes(i) || group.some(j => commonGroup(i, j, groupMemberships))) {
      return Math.sqrt(contributions[i]);
    }
    return contributions[i];
}
  
function clusterMatch(groups: number[][], contributions: number[]): number {
    // Calculates the plurality score according to connection oriented cluster match. 
    // :param: groups (list of lists): a list denotes the group and contains its members.
    // :param: contributions (list): number of participant's votes for a given project proposal.
    // :returns: plurality score
    
    const groupMemberships: number[][] = createGroupMemberships(groups);
  
    let result = 0;
  
    // Add the contribution of each agent in each group to the result
    for (let g of groups) {
      for (let i of g) {
        result += contributions[i] / groupMemberships[i].length;
      }
    }
  
    // Iterate over each pair of groups and add their contribution to the result
    for (let g of groups) {
      for (let h of groups) {
        if (g === h) continue; // Skip if the groups are the same
  
        let term1 = 0;
        // Calculate term1 for the current pair of groups
        for (let i of g) {
          term1 += K(i, h, groupMemberships, contributions) / groupMemberships[i].length;
        }
        term1 = Math.sqrt(term1);
  
        let term2 = 0;
        // Calculate term2 for the current pair of groups
        for (let j of h) {
          term2 += K(j, g, groupMemberships, contributions) / groupMemberships[j].length;
        }
        term2 = Math.sqrt(term2);
  
        result += term1 * term2;
      }
    }
  
    return Math.sqrt(result);
}
  
  // Example usage
const exampleGroups: number[][] = [
    [0, 1],
    [1, 2],
    [0, 2],
];
  
const exampleContributions: number[] = [1.5, 2.0, 1.0];
  
const result: number = clusterMatch(exampleGroups, exampleContributions);
  
console.log(result);
  