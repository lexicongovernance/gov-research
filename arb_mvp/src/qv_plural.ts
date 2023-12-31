function createGroupMemberships(groups: number[][]): number[][] {
    // Define group memberships for each participant.
    // :param: groups (list of lists): a list denotes the group and contains its members. 
    // :returns (list of lists): retunrs a list of group membersips for each participant. 
  const memberships: number[][] = [];

  for (let i = 0; i < groups.length; i++) {
      for (let j of groups[i]) {
          // Ensure memberships[j] is initialized as an array
          memberships[j] = memberships[j] || [];
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
    // :param: i: denotes a participant.
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
  
    // Calculate the first term of connection oriented cluster match 
    for (let g of groups) {
      for (let i of g) {
        result += contributions[i] / groupMemberships[i].length;
      }
    }
  
    // Calculate the interaction term of connection oriented cluster match 
    for (let g of groups) {
      for (let h of groups) {
        if (g === h) continue; // Only skip if the groups are the same group instance (but not if they contain the same content) 
  
        let term1 = 0;
        for (let i of g) {
          term1 += K(i, h, groupMemberships, contributions) / groupMemberships[i].length;
        }
        term1 = Math.sqrt(term1);
  
        let term2 = 0;
        for (let j of h) {
          term2 += K(j, g, groupMemberships, contributions) / groupMemberships[j].length;
        }
        term2 = Math.sqrt(term2);
  
        result += term1 * term2;
      }
    }
  
    return Math.sqrt(result);
}

// Export functions
export default createGroupMemberships;
export { commonGroup, K, clusterMatch };
  
// Example usage
const exampleGroups: number[][] = [[0, 1], [1, 2, 3], [0, 2]];
const groupMemberships: number[][] = createGroupMemberships(exampleGroups)
const exampleContributions: number[] = [1, 2, 3, 4];
const result: number = clusterMatch(exampleGroups, exampleContributions);
  
console.log(groupMemberships);
console.log(result);
  