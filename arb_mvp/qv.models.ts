import * as math from 'mathjs';

function quadraticVoting(votes: number[]): [Record<number, number>, number] {
  const quadraticVotesDict: Record<number, number> = {};

  for (let agentI = 0; agentI < votes.length; agentI++) {
    const quadraticVotesAgentI = math.sqrt(votes[agentI]) as number;
    quadraticVotesDict[agentI] = quadraticVotesAgentI;
  }

  const sumQuadraticVotes = Object.values(quadraticVotesDict).reduce(
    (acc, value) => acc + value,
    0
  );

  return [quadraticVotesDict, sumQuadraticVotes];
}

// Example usage:
const votes: number[] = [4, 9, 16];
const [result, sum] = quadraticVoting(votes);

console.log('Quadratic Votes:', result);
console.log('Sum of Quadratic Votes:', sum);
